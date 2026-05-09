"""Import reusable calculation factor checklists into the emission factor library."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, select

from app.domain.carbon import models as m

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_key(value: Any) -> str | None:
    text = _normalize_text(value)
    return text.lower() if text else None


def _parse_bool(value: Any, default: bool = False) -> bool:
    text = _normalize_text(value)
    if text is None:
        return default
    return text.lower() in {"1", "true", "yes", "y", "on", "是", "启用", "active"}


def _parse_int(value: Any) -> int | None:
    text = _normalize_text(value)
    if text is None:
        return None
    return int(text)


def _parse_decimal(value: Any) -> Decimal | None:
    text = _normalize_text(value)
    if text is None:
        return None
    try:
        return Decimal(text)
    except InvalidOperation as exc:  # pragma: no cover - defensive branch
        msg = f"Invalid decimal value: {text}"
        raise ValueError(msg) from exc


def _compose_note(row: ChecklistRow) -> str | None:
    parts: list[str] = []
    if row.note:
        parts.append(row.note)
    if row.business_meaning:
        parts.append(f"业务含义: {row.business_meaning}")
    if row.conversion_rule:
        parts.append(f"换算规则: {row.conversion_rule}")
    if row.matching_hint:
        parts.append(f"匹配提示: {row.matching_hint}")
    return "\n".join(parts) if parts else None


@dataclass(slots=True)
class ChecklistRow:
    """A normalized checklist row ready for validation or import."""

    line_number: int
    scope: str
    category: str
    sub_category: str
    unit: str
    factor_value: Decimal | None
    factor_unit: str
    year: int
    source: str
    source_system: str | None
    source_snapshot_id: str | None
    source_library_year: str | None
    source_library_code: str | None
    source_record_id: str | None
    raw_record_id: int | None
    projection_status: str
    review_status: str
    is_active: bool
    conversion_rule: str | None
    business_meaning: str | None
    matching_hint: str | None
    note: str | None


@dataclass(slots=True)
class ChecklistImportResult:
    """Summary for checklist imports."""

    imported: int
    updated: int
    skipped_pending: int
    skipped_invalid: int
    resolved_raw_records: int


def load_checklist_rows(csv_path: str | Path) -> list[ChecklistRow]:
    """Load and normalize checklist rows from CSV."""
    root = Path(csv_path).expanduser().resolve()
    with root.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows: list[ChecklistRow] = []
        for line_number, raw_row in enumerate(reader, start=2):
            factor_value = _parse_decimal(raw_row.get("factor_value"))
            rows.append(
                ChecklistRow(
                    line_number=line_number,
                    scope=_normalize_key(raw_row.get("scope")) or "",
                    category=_normalize_key(raw_row.get("category")) or "",
                    sub_category=_normalize_key(raw_row.get("sub_category")) or "",
                    unit=_normalize_text(raw_row.get("unit")) or "",
                    factor_value=factor_value,
                    factor_unit=_normalize_text(raw_row.get("factor_unit")) or "",
                    year=_parse_int(raw_row.get("year")) or 0,
                    source=_normalize_text(raw_row.get("source")) or "",
                    source_system=_normalize_key(raw_row.get("source_system")),
                    source_snapshot_id=_normalize_text(raw_row.get("source_snapshot_id")),
                    source_library_year=_normalize_text(raw_row.get("source_library_year")),
                    source_library_code=_normalize_text(raw_row.get("source_library_code")),
                    source_record_id=_normalize_text(raw_row.get("source_record_id")),
                    raw_record_id=_parse_int(raw_row.get("raw_record_id")),
                    projection_status=_normalize_key(raw_row.get("projection_status")) or "manual",
                    review_status=_normalize_key(raw_row.get("review_status")) or "draft",
                    is_active=_parse_bool(raw_row.get("is_active")),
                    conversion_rule=_normalize_text(raw_row.get("conversion_rule")),
                    business_meaning=_normalize_text(raw_row.get("business_meaning")),
                    matching_hint=_normalize_text(raw_row.get("matching_hint")),
                    note=_normalize_text(raw_row.get("note")),
                )
            )
    return rows


async def _resolve_raw_record(session: AsyncSession, row: ChecklistRow) -> m.CarbonFactorRawRecord | None:
    if row.raw_record_id is not None:
        raw = await session.get(m.CarbonFactorRawRecord, row.raw_record_id)
        if raw is None:
            msg = f"Raw record {row.raw_record_id} not found"
            raise ValueError(msg)
        return raw

    if not (row.source_system and row.source_snapshot_id and row.source_library_year and row.source_library_code and row.source_record_id):
        return None

    stmt = select(m.CarbonFactorRawRecord).where(
        and_(
            m.CarbonFactorRawRecord.source_system == row.source_system,
            m.CarbonFactorRawRecord.snapshot_id == row.source_snapshot_id,
            m.CarbonFactorRawRecord.library_year == row.source_library_year,
            m.CarbonFactorRawRecord.library_code == row.source_library_code,
            m.CarbonFactorRawRecord.source_record_id == row.source_record_id,
        )
    )
    raw = (await session.execute(stmt)).scalars().first()
    if raw is None:
        msg = (
            "Raw record not found for "
            f"{row.source_system}/{row.source_snapshot_id}/{row.source_library_year}/{row.source_library_code}/{row.source_record_id}"
        )
        raise ValueError(msg)
    return raw


async def _upsert_emission_factor(
    session: AsyncSession,
    row: ChecklistRow,
    raw_record: m.CarbonFactorRawRecord | None,
) -> tuple[m.EmissionFactor, bool]:
    stmt = select(m.EmissionFactor).where(
        and_(
            m.EmissionFactor.scope == row.scope,
            m.EmissionFactor.category == row.category,
            m.EmissionFactor.sub_category == row.sub_category,
            m.EmissionFactor.unit == row.unit,
            m.EmissionFactor.year == row.year,
        )
    )
    existing = (await session.execute(stmt)).scalars().first()
    values = {
        "scope": row.scope,
        "category": row.category,
        "sub_category": row.sub_category,
        "unit": row.unit,
        "factor_value": row.factor_value,
        "factor_unit": row.factor_unit,
        "year": row.year,
        "source": row.source,
        "is_active": row.is_active,
        "note": _compose_note(row),
        "source_system": row.source_system or (raw_record.source_system if raw_record else None),
        "source_snapshot_id": row.source_snapshot_id or (raw_record.snapshot_id if raw_record else None),
        "raw_record_id": raw_record.id if raw_record else row.raw_record_id,
        "projection_status": row.projection_status,
        "review_status": row.review_status,
    }
    if existing is None:
        obj = m.EmissionFactor(**values)
        session.add(obj)
        return obj, True
    for field, value in values.items():
        setattr(existing, field, value)
    return existing, False


async def import_calculation_factor_checklist(
    session: AsyncSession,
    csv_path: str | Path,
) -> ChecklistImportResult:
    """Import a reusable calculation-factor checklist CSV into `dataapp_emissionfactor`."""
    rows = load_checklist_rows(csv_path)
    imported = 0
    updated = 0
    skipped_pending = 0
    skipped_invalid = 0
    resolved_raw_records = 0

    for row in rows:
        if not row.scope or not row.category or not row.sub_category or not row.unit or not row.factor_unit or row.year <= 0:
            skipped_invalid += 1
            continue
        if row.factor_value is None:
            skipped_pending += 1
            continue

        raw_record = await _resolve_raw_record(session, row)
        if raw_record is not None:
            resolved_raw_records += 1

        _, created = await _upsert_emission_factor(session, row, raw_record)
        if created:
            imported += 1
        else:
            updated += 1

    await session.commit()
    return ChecklistImportResult(
        imported=imported,
        updated=updated,
        skipped_pending=skipped_pending,
        skipped_invalid=skipped_invalid,
        resolved_raw_records=resolved_raw_records,
    )
