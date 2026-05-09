from __future__ import annotations

import csv
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.domain.carbon.calculation_factor_importer import import_calculation_factor_checklist
from app.domain.carbon.models import CarbonFactorRawRecord, EmissionFactor

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.anyio


async def test_import_calculation_factor_checklist_writes_emission_factor(session, tmp_path: Path) -> None:
    raw_record = CarbonFactorRawRecord(
        snapshot_id="20260503T133840Z",
        source_system="ncsc_ghg_efdb",
        source_url="https://data.ncsc.org.cn/factories/index",
        library_year="2026",
        library_code="G02",
        library_name="行业企业排放因子",
        category_path="净购入电力与热力 / 电力消费 / 电力平均二氧化碳排放因子(不包括市场化交易的非化石能源电量) / 全国平均二氧化碳排放因子(不包括市场化交易的非化石能源电量)",
        top_category="净购入电力与热力",
        second_category="电力消费",
        source_record_id="1768712086295601328",
        stable_hash="test-stable-hash",
        factor_name="适用区域 - 全国 - 2023年因子 (kgCO₂/kWh)",
        factor_value_raw="0.6096",
        factor_unit_raw="kgCO₂/kWh",
        region_raw=None,
        gas_raw="CO2",
        time_representativeness="2026",
        provider="国家应对气候变化战略研究中心",
        source_description=None,
        projection_status="raw_only",
        raw_payload={},
    )
    session.add(raw_record)
    await session.commit()

    csv_path = tmp_path / "checklist.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "scope",
                "category",
                "sub_category",
                "unit",
                "factor_value",
                "factor_unit",
                "year",
                "source",
                "source_system",
                "source_snapshot_id",
                "source_library_year",
                "source_library_code",
                "source_record_id",
                "raw_record_id",
                "projection_status",
                "review_status",
                "is_active",
                "conversion_rule",
                "business_meaning",
                "matching_hint",
                "note",
            ]
        )
        writer.writerow(
            [
                "scope2",
                "electricity",
                "grid_electricity_national",
                "kWh",
                "0.6096",
                "kgCO2e/kWh",
                "2023",
                "NCSC 2026 行业企业排放因子",
                "ncsc_ghg_efdb",
                "20260503T133840Z",
                "2026",
                "G02",
                "1768712086295601328",
                "",
                "direct",
                "approved",
                "true",
                "",
                "全国口径购入电力",
                "",
                "",
            ]
        )

    result = await import_calculation_factor_checklist(session, csv_path)

    assert result.imported == 1
    assert result.updated == 0
    assert result.skipped_pending == 0
    assert result.skipped_invalid == 0
    assert result.resolved_raw_records == 1

    factor = (await session.execute(select(EmissionFactor))).scalars().first()
    assert factor is not None
    assert factor.scope == "scope2"
    assert factor.category == "electricity"
    assert factor.sub_category == "grid_electricity_national"
    assert factor.unit == "kWh"
    assert factor.factor_value == Decimal("0.6096")
    assert factor.factor_unit == "kgCO2e/kWh"
    assert factor.year == 2023
    assert factor.raw_record_id == raw_record.id
    assert "全国口径购入电力" in (factor.note or "")
