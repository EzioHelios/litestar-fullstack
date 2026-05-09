# 计算因子清单格式

本文件定义 Scope 1/2/3 计算因子库的可复用清单格式，目标是同时满足：

- 人工梳理和审核
- 后续程序批量导入 `dataapp_emissionfactor`
- 与官方因子库 `carbon_factor_raw_record` 建立追溯关系

推荐使用 UTF-8 编码的 CSV 文件，字段顺序固定。

## 文件用途

一条清单记录表示一个“可直接进入核算引擎”的计算因子，而不是一条原始官方因子。

例如：

- `scope1 / fuel / diesel / L`
- `scope2 / electricity / grid_electricity / kWh`
- `scope3 / transport / heavy_truck / t·km`

## 字段定义

| 字段名 | 必填 | 说明 |
|---|---|---|
| `scope` | 是 | `scope1` / `scope2` / `scope3` |
| `category` | 是 | 计算大类。当前建议：`fuel` / `refrigerant` / `electricity` / `waste` / `transport` |
| `sub_category` | 是 | 计算子类编码，必须稳定、可复用、适合程序匹配 |
| `unit` | 是 | 活动量单位，对应 `EmissionFactor.unit` |
| `factor_value` | 否 | 最终计算因子值；未完成换算前可留空 |
| `factor_unit` | 是 | 最终因子单位，建议统一写 `kgCO2e/<activity_unit>` |
| `year` | 是 | 计算因子适用年份 |
| `source` | 是 | 人类可读来源名称，例如 `NCSC 2026 行业企业排放因子` |
| `source_system` | 否 | 来源系统，当前官方库默认 `ncsc_ghg_efdb` |
| `source_snapshot_id` | 否 | 官方库导入批次 ID，例如 `20260503T133840Z` |
| `source_library_year` | 否 | 官方库版本年份，例如 `2026` / `AR5` |
| `source_library_code` | 否 | 官方库代码，例如 `G02` / `GWP` |
| `source_record_id` | 否 | 官方原始记录的 `source_record_id`，用于跨环境稳定追溯 |
| `raw_record_id` | 否 | 当前环境数据库中的 `carbon_factor_raw_record.id`，仅本环境有效 |
| `projection_status` | 是 | `manual` / `derived` / `direct`，表示该计算因子的形成方式 |
| `review_status` | 是 | `draft` / `pending` / `approved` / `rejected` |
| `is_active` | 是 | `true` / `false` |
| `conversion_rule` | 否 | 计算因子换算规则说明，例如 `CO2+CH4*GWP+N2O*GWP, then convert TJ->L` |
| `business_meaning` | 否 | 该计算点的业务口径说明 |
| `matching_hint` | 否 | 原始因子检索提示，便于人工复核 |
| `note` | 否 | 备注 |

## 使用规则

1. `scope + category + sub_category + unit + year` 应视为一条计算因子的业务唯一键。
2. `sub_category` 不要直接用中文展示名，建议使用稳定编码，如：
   - `diesel`
   - `gasoline`
   - `natural_gas`
   - `grid_electricity_national`
   - `waste_municipal_incineration`
   - `transport_heavy_truck`
3. 如果计算因子直接来自官方库单条记录，`projection_status` 写 `direct`。
4. 如果需要多个官方因子合成或单位换算，`projection_status` 写 `derived`，并填写 `conversion_rule`。
5. 如果暂时只是业务待确认项，还没完成官方映射，`projection_status` 可写 `manual`，`factor_value` 留空。
6. `raw_record_id` 只适合当前数据库，不适合作为跨环境唯一追溯键；跨环境请优先保留 `source_snapshot_id + source_library_year + source_library_code + source_record_id`。

## 当前建议的首批计算点

- Scope 1 燃料燃烧
  - `diesel`
  - `gasoline`
  - `lng`
  - `cng`
  - `natural_gas`
- Scope 1 制冷剂
  - `R22`
  - `R32`
  - `R134a`
  - `R410A`
  - `R404A`
  - `R407C`
- Scope 2 购入电力
  - `grid_electricity_national`
  - `grid_electricity_<province>`
- Scope 3 废弃物
  - `waste_municipal_incineration`
  - `waste_municipal_landfill`
  - `waste_packaging_recycle`
- Scope 3 外购运输
  - `transport_light_truck`
  - `transport_heavy_truck`

## 导入建议

后续程序导入时，建议按以下顺序处理：

1. 读取 CSV
2. 校验 `scope/category/sub_category/unit/year`
3. 若存在 `raw_record_id`，直接关联官方原始因子
4. 若不存在 `raw_record_id`，尝试用 `source_snapshot_id + source_library_year + source_library_code + source_record_id` 解析
5. 写入 `dataapp_emissionfactor`
6. 对 `factor_value` 为空的记录拒绝导入到启用状态

## 导入命令

模板确认无误后，可以直接执行：

```bash
app carbon import-calculation-factor-checklist docs/carbon/calculation-factor-checklist-template.csv
```

说明：

- `factor_value` 为空的行会被视为待补全项，不会写入启用的计算因子
- `business_meaning`、`conversion_rule`、`matching_hint` 会被保留到 `note` 中，便于后续复核
