# NCSC 因子投影包迁移指南

## 目标

本目录保存一组面向 `litestar-fullstack` 的国家温室气体排放因子数据库投影包。它不是 NCSC 官方库的全量镜像，而是从已抓取的官方 raw snapshot 中筛选出当前 `dataapp_emissionfactor` 可直接承载、可用于计算和演示的因子行。

采用这种交付形式的原因：

- 不新增业务模块，不改 API 路由，不改变现有碳模块边界。
- 不要求 `litestar-fullstack` 在线访问 `data.ncsc.org.cn`。
- 不把官方全量复杂结构强塞进当前计算因子表。
- 后续如果要建设完整官方因子库，当前数据包仍可作为投影结果回归样本。

## 文件说明

```text
resources/factors/ncsc/
  ncsc_emission_factors.projected.json
  ncsc_emission_factors.manifest.json
  MIGRATION_GUIDE.md
```

### `ncsc_emission_factors.projected.json`

面向当前模型 `app.domain.carbon.models.EmissionFactor` 的可导入数据包。

每条 `records[]` 记录只包含当前表可接受的字段：

```json
{
  "scope": "scope2",
  "category": "electricity",
  "sub_category": "grid_electricity_jiangsu",
  "unit": "kWh",
  "factor_value": "0.5827",
  "factor_unit": "kgCO2/kWh",
  "year": 2026,
  "source": "NCSC 2026 G02 行业企业排放因子",
  "is_active": true,
  "note": "{...trace metadata...}"
}
```

`note` 是 JSON 字符串，保存来源追溯信息，包括：

- `sourceSystem`
- `sourceUrl`
- `sourceLibraryCode`
- `sourceLibraryName`
- `sourceYear`
- `sourceRecordId`
- `referenceKey`
- `categoryPath`
- `factorName`
- `factorUnitRaw`
- `regionRaw`
- `gasRaw`
- `projectionPackage`

### `ncsc_emission_factors.manifest.json`

记录投影包元信息和统计结果。

当前包来自 `backend-feat-energy` 中的 NCSC raw snapshot：

- `snapshotId`: `20260503T133840Z`
- 官方 raw library 数：`5`
- 官方 raw category 数：`821`
- 官方 raw leaf category 数：`545`
- 官方 raw page 数：`545`
- 官方 raw record 数：`1441`
- 本次投影记录数：`105`

本次投影分布：

- `scope1`: `65`
- `scope2`: `40`
- `fuel`: `65`
- `electricity`: `40`

## 投影边界

本包只导入当前系统能解释的计算因子：

- 直接 `CO2/CO2e` 因子
- 可解析数值
- 可解析单位，且单位包含分子/分母，例如 `kgCO2/kWh`、`tCO2/TJ`
- `scope1` 燃料燃烧因子
- `scope2` 外购电力因子

本包明确跳过：

- `CH4`
- `N2O`
- 含碳量，例如 `tC/TJ`
- 氧化率、百分比、无量纲参数
- 过程参数或暂时无法解释到当前 `scope/category/sub_category` 的官方记录
- 当前模型无法完整保存的官方原始复杂结构

## 推荐导入策略

第一阶段建议写一个小型工具脚本，而不是新增业务 API。推荐路径：

```text
tools/factor_library/import_ncsc_factors.py
```

推荐命令形态：

```bash
uv run python tools/factor_library/import_ncsc_factors.py --dry-run
uv run python tools/factor_library/import_ncsc_factors.py --apply
uv run python tools/factor_library/import_ncsc_factors.py --apply --replace-package ncsc-ghg-efdb-litestar-fullstack-projection-20260503T133840Z-v1
```

### 幂等键

当前表没有 `source_record_id` 等独立字段，所以第一阶段推荐幂等键为：

```text
scope + category + sub_category + year + source
```

如果后续需要更强幂等，可以从 `note` 中解析 `referenceKey`。

### 导入伪代码

```python
from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.config import alchemy
from app.db import models as m

PACKAGE_PATH = Path("resources/factors/ncsc/ncsc_emission_factors.projected.json")


async def import_ncsc_factors(dry_run: bool = True) -> None:
    payload = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    rows = payload["records"]

    created = 0
    reused = 0

    async with alchemy.get_session() as session:
        for row in rows:
            stmt = select(m.EmissionFactor).where(
                m.EmissionFactor.scope == row["scope"],
                m.EmissionFactor.category == row["category"],
                m.EmissionFactor.sub_category == row["sub_category"],
                m.EmissionFactor.year == row["year"],
                m.EmissionFactor.source == row["source"],
            )
            existing = (await session.execute(stmt)).scalars().first()
            if existing is not None:
                reused += 1
                continue

            created += 1
            if dry_run:
                continue

            session.add(
                m.EmissionFactor(
                    scope=row["scope"],
                    category=row["category"],
                    sub_category=row["sub_category"],
                    unit=row["unit"],
                    factor_value=Decimal(row["factor_value"]),
                    factor_unit=row["factor_unit"],
                    year=row["year"],
                    source=row["source"],
                    is_active=row["is_active"],
                    note=row["note"],
                )
            )

        if not dry_run:
            await session.commit()

    print({"total": len(rows), "created": created, "reused": reused, "dryRun": dry_run})


if __name__ == "__main__":
    asyncio.run(import_ncsc_factors(dry_run=True))
```

正式实现时建议把 `dry-run/apply/replace-package` 做成 argparse 参数，并在 `--replace-package` 时只删除 `note` 中包含对应 `projectionPackage` 的 NCSC 记录。

## 导入前检查

导入前建议执行：

```bash
python -m json.tool resources/factors/ncsc/ncsc_emission_factors.projected.json >/dev/null
python -m json.tool resources/factors/ncsc/ncsc_emission_factors.manifest.json >/dev/null
```

人工抽查：

- `manifest.projection.recordCount` 是否等于 `projected.records` 长度。
- `factor_value` 是否都是字符串形式的十进制数。
- `factor_unit` 长度是否不超过当前模型 `String(32)`。
- `unit` 长度是否不超过当前模型 `String(20)`。
- `source` 长度是否不超过当前模型 `String(128)`。
- `note` 是否能被 `json.loads()` 解析。

## 导入后验证

导入后建议执行：

```sql
select scope, category, count(*)
from dataapp_emissionfactor
where source like 'NCSC %'
group by scope, category
order by scope, category;
```

预期至少看到：

```text
scope1 | fuel        | 65
scope2 | electricity | 40
```

也可以抽查江苏电力因子：

```sql
select scope, category, sub_category, unit, factor_value, factor_unit, year, source
from dataapp_emissionfactor
where sub_category = 'grid_electricity_jiangsu'
order by year desc;
```

## 回滚策略

如果只想回滚本投影包，建议按 `note` 中的包名删除：

```sql
delete from dataapp_emissionfactor
where source like 'NCSC %'
  and note like '%ncsc-ghg-efdb-litestar-fullstack-projection-20260503T133840Z-v1%';
```

如果后续 importer 支持 `--replace-package`，应优先使用 importer 回滚或替换，避免误删人工维护的 NCSC 因子。

## 后续升级建议

第一阶段先用本包完成交付；如果后续要做“专属因子库产品能力”，再新增官方因子领域表：

- `official_factor_snapshot`
- `official_factor_library`
- `official_factor_category`
- `official_factor_record`

然后把当前 `dataapp_emissionfactor` 作为业务计算投影表，而不是官方全量原始表。这样既能保留官方数据全貌，也不会污染现有计算逻辑。
