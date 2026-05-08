from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.anyio

# Endpoints backed by SQLAlchemy ORM models (work with test DB schema)
CARBON_ORM_ENDPOINTS: list[str] = [
    # Scope1/2/3 列表接口
    "/api/carbon/scope1-mobile-combustion",
    "/api/carbon/scope1-stationary-combustion",
    "/api/carbon/scope1-refrigerant-leak",
    "/api/carbon/scope2-electricity-bill",
    "/api/carbon/scope3-waste-disposal",
    "/api/carbon/scope3-third-party-transport",
    # 统一待审核列表
    "/api/carbon/pending",
    # 排放因子库
    "/api/carbon/emission-factors",
    # IoT 与审核日志
    "/api/carbon/iot-telemetry",
    "/api/carbon/audit-logs",
]

# Endpoints that query raw SQL database views (require legacy views in DB)
CARBON_VIEW_ENDPOINTS: list[str] = [
    "/api/page1/ydfdzl/day",
    "/api/page1/yjzl/day",
    "/api/page2/spgl",
    "/api/page3/cnsy",
    "/api/page4/tpfltj",
]


async def test_carbon_orm_endpoints_return_json(client: AsyncClient) -> None:
    """连通性测试：ORM 端点不应返回 5xx。"""
    for path in CARBON_ORM_ENDPOINTS:
        response = await client.get(path)
        assert response.status_code < 500, f"{path} 返回 {response.status_code}"
        if response.content:
            _ = response.json()


async def test_carbon_view_endpoints_return_json(client: AsyncClient) -> None:
    """连通性测试：大屏视图端点应优雅处理视图不存在的情况。

    这些端点查询数据库视图（如 yj_day_sum_view），在测试数据库中不存在。
    当前预期行为是返回 500（因 controller 缺少错误处理），标记为 xfail。
    """
    for path in CARBON_VIEW_ENDPOINTS:
        response = await client.get(path)
        # 这些端点查询不存在的视图会 500，这是已知的 controller 层缺陷
        # 当 controller 加上错误处理后，应改为 assert < 500
        assert response.status_code < 500, f"{path} 返回 {response.status_code}"
