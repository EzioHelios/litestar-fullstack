"""Import source factor packages into the carbon factor asset library."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from app.domain.carbon import models as m

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

NCSC_SOURCE_SYSTEM = "ncsc_ghg_efdb"


@dataclass(frozen=True)
class FactorImportResult:
    """Summary returned by factor importers."""

    snapshot_id: str
    source_system: str
    checksum_verified: bool
    libraries: int
    categories: int
    raw_records: int
    projection_candidates: int


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _stable_hash(payload: dict[str, Any], snapshot_id: str) -> str:
    source_record_id = _normalize_text(payload.get("sourceRecordId"))
    if source_record_id:
        key = "|".join(
            [
                snapshot_id,
                str(payload.get("sourceLibraryCode") or ""),
                str(payload.get("sourceYear") or ""),
                source_record_id,
            ]
        )
    else:
        key = "|".join(
            [
                snapshot_id,
                str(payload.get("sourceLibraryCode") or ""),
                str(payload.get("sourceYear") or ""),
                " / ".join(payload.get("categoryPath") or []),
                str(payload.get("factorName") or ""),
                str(payload.get("factorUnitRaw") or ""),
                str(payload.get("regionRaw") or ""),
                str(payload.get("gasRaw") or ""),
            ]
        )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _is_projection_candidate(record: dict[str, Any]) -> bool:
    unit = str(record.get("factorUnitRaw") or "")
    name = str(record.get("factorName") or "")
    gas = str(record.get("gasRaw") or "")
    text = f"{unit} {name} {gas}"
    if any(marker in text for marker in ("CH₄", "CH4", "N₂O", "N2O", "tC/TJ", "低位发热量", "氧化率", "%")):
        return False
    return any(marker in text for marker in ("CO₂", "CO2", "CO₂e", "CO2e"))


async def _upsert_one(
    session: AsyncSession,
    model: type[Any],
    match: dict[str, Any],
    values: dict[str, Any],
) -> Any:
    stmt = select(model)
    for field, value in match.items():
        stmt = stmt.where(getattr(model, field) == value)
    existing = (await session.execute(stmt)).scalars().first()
    if existing is None:
        obj = model(**values)
        session.add(obj)
        return obj
    for field, value in values.items():
        setattr(existing, field, value)
    return existing


def verify_sha256sums(package_dir: Path) -> bool:
    """Verify package files against checksums/SHA256SUMS."""
    checksums_path = package_dir / "checksums" / "SHA256SUMS"
    if not checksums_path.exists():
        return False
    for checksum_line in checksums_path.read_text(encoding="utf-8").splitlines():
        stripped_line = checksum_line.strip()
        if not stripped_line:
            continue
        expected, relative = stripped_line.split(maxsplit=1)
        file_path = package_dir / relative
        if not file_path.exists():
            return False
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != expected:
            return False
    return True


def verify_sha256sums_flat(package_dir: Path) -> bool:
    """Verify package files against a root-level SHA256SUMS file."""
    checksums_path = package_dir / "SHA256SUMS"
    if not checksums_path.exists():
        return False
    for checksum_line in checksums_path.read_text(encoding="utf-8").splitlines():
        stripped_line = checksum_line.strip()
        if not stripped_line:
            continue
        expected, relative = stripped_line.split(maxsplit=1)
        file_path = package_dir / relative
        if not file_path.exists():
            return False
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != expected:
            return False
    return True


def _is_full_ncsc_package(root: Path) -> bool:
    return (
        (root / "manifest.json").exists()
        and (root / "catalog" / "selected_libraries.json").exists()
        and (root / "catalog" / "categories.json").exists()
        and (root / "raw" / "records.jsonl").exists()
    )


def _is_gwp_reference_package(root: Path) -> bool:
    return (root / "gwp_ar5_records.json").exists()


async def import_ncsc_factor_package(session: AsyncSession, package_dir: str | Path) -> FactorImportResult:
    """Import an NCSC official greenhouse-gas factor package.

    The importer preserves NCSC as one source system within a broader factor asset model. Future ecoinvent support
    can add another importer that writes the same library/category/raw-record tables with source_system="ecoinvent".
    """
    root = Path(package_dir).expanduser().resolve()
    if not root.exists():
        msg = f"Factor package not found: {root}"
        raise FileNotFoundError(msg)
    if _is_gwp_reference_package(root):
        return await import_ncsc_gwp_ar5_package(session, root)
    if not _is_full_ncsc_package(root):
        msg = f"Unsupported factor package structure: {root}"
        raise FileNotFoundError(msg)

    manifest = _read_json(root / "manifest.json")
    selected_libraries = _read_json(root / "catalog" / "selected_libraries.json").get("selectedLibraries", [])
    categories = _read_json(root / "catalog" / "categories.json").get("categoryRecords", [])
    counts = manifest.get("counts") or {}
    crawl = manifest.get("crawl") or {}
    snapshot_id = str(manifest["snapshotId"])
    source_system = str(manifest.get("sourceSystem") or NCSC_SOURCE_SYSTEM)
    source_url = _normalize_text(manifest.get("sourceUrl"))
    checksum_verified = verify_sha256sums(root)

    await _upsert_one(
        session,
        m.CarbonFactorImportBatch,
        {"source_system": source_system, "snapshot_id": snapshot_id},
        {
            "source_system": source_system,
            "snapshot_id": snapshot_id,
            "package_name": _normalize_text(manifest.get("packageName")),
            "package_version": _normalize_text(manifest.get("packageVersion")),
            "package_type": _normalize_text(manifest.get("packageType")),
            "source_url": source_url,
            "built_at": _parse_datetime(manifest.get("builtAt")),
            "crawl_started_at": _parse_datetime(crawl.get("startedAt")),
            "crawl_finished_at": _parse_datetime(crawl.get("finishedAt")),
            "is_complete": bool(crawl.get("complete")),
            "checksum_verified": checksum_verified,
            "import_status": "imported",
            "library_count": int(counts.get("libraryCount") or 0),
            "category_count": int(counts.get("categoryCount") or 0),
            "leaf_category_count": int(counts.get("leafCategoryCount") or 0),
            "page_count": int(counts.get("pageCount") or 0),
            "record_count": int(counts.get("recordCount") or 0),
            "detail_count": int(counts.get("detailCount") or 0),
            "failure_count": int(counts.get("failureCount") or 0),
            "xlsx_count": int(counts.get("xlsxCount") or 0),
            "manifest_payload": manifest,
        },
    )

    libraries_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for library in selected_libraries:
        library_year = str(library.get("year") or "")
        library_code = str(library.get("code") or "")
        libraries_by_key[(library_year, library_code)] = library
        await _upsert_one(
            session,
            m.CarbonFactorLibrary,
            {"source_system": source_system, "library_year": library_year, "library_code": library_code},
            {
                "source_system": source_system,
                "library_year": library_year,
                "library_code": library_code,
                "library_name": str(library.get("name") or ""),
                "institution": _normalize_text(library.get("institution")),
                "source_pkid": _normalize_text(library.get("pkid")),
                "source_year_id": _normalize_text(library.get("yearId")),
                "raw_payload": library,
            },
        )

    for category in categories:
        library = category.get("library") or {}
        path = [str(item) for item in category.get("categoryPath") or []]
        source_category_id = str(category.get("pkid") or "")
        if not source_category_id:
            continue
        await _upsert_one(
            session,
            m.CarbonFactorCategory,
            {"source_system": source_system, "source_category_id": source_category_id},
            {
                "source_system": source_system,
                "source_category_id": source_category_id,
                "parent_source_category_id": _normalize_text(category.get("parentId")),
                "library_year": _normalize_text(library.get("year")),
                "library_code": _normalize_text(library.get("code")),
                "category_name": str(category.get("name") or ""),
                "category_path": " / ".join(path),
                "depth": max(len(path) - 1, 0),
                "is_leaf": bool(category.get("isLeaf")),
                "raw_payload": category.get("rawPayload") or category,
            },
        )

    raw_records = 0
    projection_candidates = 0
    records_path = root / "raw" / "records.jsonl"
    with records_path.open(encoding="utf-8") as records_file:
        for record_line in records_file:
            stripped_line = record_line.strip()
            if not stripped_line:
                continue
            raw_records += 1
            record = json.loads(stripped_line)
            category_path_items = [str(item) for item in record.get("categoryPath") or []]
            library_year = _normalize_text(record.get("sourceYear"))
            library_code = _normalize_text(record.get("sourceLibraryCode"))
            library = libraries_by_key.get((library_year or "", library_code or ""), {})
            projection_status = "candidate" if _is_projection_candidate(record) else "raw_only"
            if projection_status == "candidate":
                projection_candidates += 1
            stable_hash = _stable_hash(record, snapshot_id)
            await _upsert_one(
                session,
                m.CarbonFactorRawRecord,
                {"source_system": source_system, "snapshot_id": snapshot_id, "stable_hash": stable_hash},
                {
                    "snapshot_id": snapshot_id,
                    "source_system": source_system,
                    "source_url": source_url,
                    "library_year": library_year,
                    "library_code": library_code,
                    "library_name": _normalize_text(record.get("sourceLibraryName")),
                    "category_path": " / ".join(category_path_items),
                    "top_category": category_path_items[0] if category_path_items else None,
                    "second_category": category_path_items[1] if len(category_path_items) > 1 else None,
                    "source_record_id": _normalize_text(record.get("sourceRecordId")),
                    "stable_hash": stable_hash,
                    "factor_name": str(record.get("factorName") or ""),
                    "factor_value_raw": _normalize_text(record.get("factorValue")),
                    "factor_unit_raw": _normalize_text(record.get("factorUnitRaw")),
                    "region_raw": _normalize_text(record.get("regionRaw")),
                    "gas_raw": _normalize_text(record.get("gasRaw")),
                    "time_representativeness": _normalize_text(record.get("timeRepresentativeness")),
                    "provider": _normalize_text(record.get("provider") or library.get("institution")),
                    "source_description": _normalize_text(record.get("sourceDescription")),
                    "projection_status": projection_status,
                    "raw_payload": record.get("rawPayload") or record,
                },
            )

    await session.commit()
    return FactorImportResult(
        snapshot_id=snapshot_id,
        source_system=source_system,
        checksum_verified=checksum_verified,
        libraries=len(selected_libraries),
        categories=len(categories),
        raw_records=raw_records,
        projection_candidates=projection_candidates,
    )


async def import_ncsc_gwp_ar5_package(session: AsyncSession, package_dir: str | Path) -> FactorImportResult:
    """Import the NCSC GWP AR5 table as an independent official factor library."""
    root = Path(package_dir).expanduser().resolve()
    package = _read_json(root / "gwp_ar5_records.json")
    metadata = package.get("metadata") or {}
    records = package.get("records") or []

    source_system = NCSC_SOURCE_SYSTEM
    library_year = "AR5"
    library_code = "GWP"
    library_name = "GWP值(AR5)"
    snapshot_id = _normalize_text(metadata.get("builtAt")) or (
        f"gwp-ar5-{datetime.now(tz=datetime.UTC).strftime('%Y%m%d%H%M%S')}"
    )
    source_url = _normalize_text(metadata.get("sourcePage"))
    checksum_verified = verify_sha256sums_flat(root)

    manifest_payload = {
        "packageType": "reference_table",
        "datasetName": metadata.get("datasetName"),
        "datasetVersion": metadata.get("datasetVersion"),
        "sourceFinding": metadata.get("sourceFinding"),
        "sourceBundle": metadata.get("sourceBundle"),
        "columns": metadata.get("columns"),
        "recordCount": len(records),
    }
    await _upsert_one(
        session,
        m.CarbonFactorImportBatch,
        {"source_system": source_system, "snapshot_id": snapshot_id},
        {
            "source_system": source_system,
            "snapshot_id": snapshot_id,
            "package_name": library_name,
            "package_version": _normalize_text(metadata.get("datasetVersion")) or "1.0.0",
            "package_type": "reference_table",
            "source_url": source_url,
            "built_at": _parse_datetime(_normalize_text(metadata.get("builtAt"))),
            "crawl_started_at": None,
            "crawl_finished_at": None,
            "is_complete": True,
            "checksum_verified": checksum_verified,
            "import_status": "imported",
            "library_count": 1,
            "category_count": 7,
            "leaf_category_count": 6,
            "page_count": 1,
            "record_count": len(records),
            "detail_count": len(records),
            "failure_count": 0,
            "xlsx_count": 1,
            "manifest_payload": manifest_payload,
        },
    )

    await _upsert_one(
        session,
        m.CarbonFactorLibrary,
        {"source_system": source_system, "library_year": library_year, "library_code": library_code},
        {
            "source_system": source_system,
            "library_year": library_year,
            "library_code": library_code,
            "library_name": library_name,
            "institution": "国家应对气候变化战略研究中心",
            "source_pkid": "gwp-ar5",
            "source_year_id": "AR5",
            "raw_payload": {
                "datasetName": metadata.get("datasetName"),
                "sourceBundle": metadata.get("sourceBundle"),
                "sourceFinding": metadata.get("sourceFinding"),
                "sourcePage": source_url,
            },
        },
    )

    category_specs = [
        {
            "source_category_id": "gwp-ar5-root",
            "parent_source_category_id": "-1",
            "category_name": "GWP值(AR5)",
            "category_path": "GWP值(AR5)",
            "depth": 0,
            "is_leaf": False,
            "code": "GWP",
            "sort_num": 0,
        },
        {
            "source_category_id": "gwp-ar5-co2",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "CO₂",
            "category_path": "GWP值(AR5) / CO₂",
            "depth": 1,
            "is_leaf": True,
            "code": "CO2",
            "sort_num": 1,
        },
        {
            "source_category_id": "gwp-ar5-ch4",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "CH₄",
            "category_path": "GWP值(AR5) / CH₄",
            "depth": 1,
            "is_leaf": True,
            "code": "CH4",
            "sort_num": 2,
        },
        {
            "source_category_id": "gwp-ar5-n2o",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "N₂O",
            "category_path": "GWP值(AR5) / N₂O",
            "depth": 1,
            "is_leaf": True,
            "code": "N2O",
            "sort_num": 3,
        },
        {
            "source_category_id": "gwp-ar5-hfcs",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "HFCs",
            "category_path": "GWP值(AR5) / HFCs",
            "depth": 1,
            "is_leaf": True,
            "code": "HFCs",
            "sort_num": 4,
        },
        {
            "source_category_id": "gwp-ar5-pfcs",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "PFCs",
            "category_path": "GWP值(AR5) / PFCs",
            "depth": 1,
            "is_leaf": True,
            "code": "PFCs",
            "sort_num": 5,
        },
        {
            "source_category_id": "gwp-ar5-sf6",
            "parent_source_category_id": "gwp-ar5-root",
            "category_name": "SF₆",
            "category_path": "GWP值(AR5) / SF₆",
            "depth": 1,
            "is_leaf": True,
            "code": "SF6",
            "sort_num": 6,
        },
    ]
    for category in category_specs:
        await _upsert_one(
            session,
            m.CarbonFactorCategory,
            {"source_system": source_system, "source_category_id": category["source_category_id"]},
            {
                "source_system": source_system,
                "source_category_id": category["source_category_id"],
                "parent_source_category_id": category["parent_source_category_id"],
                "library_year": library_year,
                "library_code": library_code,
                "category_name": category["category_name"],
                "category_path": category["category_path"],
                "depth": category["depth"],
                "is_leaf": category["is_leaf"],
                "raw_payload": {"code": category["code"], "sortNum": category["sort_num"]},
            },
        )

    category_map = {
        "CO₂": ("GWP值(AR5) / CO₂", "CO₂"),
        "CH₄": ("GWP值(AR5) / CH₄", "CH₄"),
        "N₂O": ("GWP值(AR5) / N₂O", "N₂O"),
        "HFCs": ("GWP值(AR5) / HFCs", "HFCs"),
        "PFCs": ("GWP值(AR5) / PFCs", "PFCs"),
        "SF₆": ("GWP值(AR5) / SF₆", "SF₆"),
    }
    raw_records = 0
    for record in records:
        raw_records += 1
        gas_type = _normalize_text(record.get("gasType")) or "GWP值(AR5)"
        category_path, top_category = category_map.get(gas_type, ("GWP值(AR5)", "GWP值(AR5)"))
        source_record_id = _normalize_text(record.get("id")) or str(raw_records)
        synthetic_record = {
            "sourceLibraryCode": library_code,
            "sourceYear": library_year,
            "sourceRecordId": source_record_id,
            "categoryPath": category_path.split(" / "),
            "factorName": str(record.get("gasName") or ""),
            "factorValue": record.get("gwpValue"),
            "factorUnitRaw": "GWP值(AR5)",
            "regionRaw": None,
            "gasRaw": gas_type,
        }
        stable_hash = _stable_hash(synthetic_record, snapshot_id)
        await _upsert_one(
            session,
            m.CarbonFactorRawRecord,
            {"source_system": source_system, "snapshot_id": snapshot_id, "stable_hash": stable_hash},
            {
                "snapshot_id": snapshot_id,
                "source_system": source_system,
                "source_url": source_url,
                "library_year": library_year,
                "library_code": library_code,
                "library_name": library_name,
                "category_path": category_path,
                "top_category": top_category,
                "second_category": str(record.get("gasName") or ""),
                "source_record_id": source_record_id,
                "stable_hash": stable_hash,
                "factor_name": str(record.get("gasName") or ""),
                "factor_value_raw": _normalize_text(record.get("gwpValue")),
                "factor_unit_raw": "GWP值(AR5)",
                "region_raw": None,
                "gas_raw": gas_type,
                "time_representativeness": "AR5",
                "provider": "国家应对气候变化战略研究中心",
                "source_description": _normalize_text(metadata.get("sourceFinding")),
                "projection_status": "raw_only",
                "raw_payload": {
                    "metadata": metadata,
                    "record": record,
                },
            },
        )

    await session.commit()
    return FactorImportResult(
        snapshot_id=snapshot_id,
        source_system=source_system,
        checksum_verified=checksum_verified,
        libraries=1,
        categories=len(category_specs),
        raw_records=raw_records,
        projection_candidates=0,
    )
