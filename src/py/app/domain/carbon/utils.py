from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.domain.carbon import models as m

# 排放因子与面积常量
YD_CPFL_PFYZ = 0.5810  # 对应旧版 YD_CPFL_PFYZ
GF_CJPL_PFYZ = 0.5810  # 对应旧版 GF_CJPL_PFYZ
_CKYQZMJ = 25600
_CKCCMJ = 10200

def calc_employee_commute_emission(car_power_type: int, gas: float, distance: float) -> float:
    """计算员工通勤碳排放量 (从 xtck_deploy 迁移)"""
    # (0, '柴油'), (1, '汽油'), (2, '电力')
    GWP_N2O = 310
    GWP_CH4 = 21
    
    if car_power_type == 0:  # 柴油
        n2o_factor = 15
        ch4_factor = 0
        co2_factor = 3.0959 * 0.85
    elif car_power_type == 1:  # 汽油
        n2o_factor = 6
        ch4_factor = 57
        co2_factor = 3.04254 * 0.725
    else:  # 电力 (2)
        n2o_factor = 0
        ch4_factor = 0
        co2_factor = YD_CPFL_PFYZ

    # E燃烧 = E燃烧-CO2 + E燃烧-CH4 + E燃烧-N2O
    co2_emission = (
        gas * co2_factor +
        distance * ch4_factor * GWP_CH4 / (10 ** 6) +
        distance * n2o_factor * GWP_N2O / (10 ** 6)
    )
    return co2_emission

async def calc_day_ygtq_cpfl(db_session: AsyncSession) -> float:
    """计算每天员工通勤碳排放量 (适配 SQLAlchemy)"""
    from sqlalchemy import select
    from app.domain.carbon.models import EmployeeCommute
    
    result = await db_session.execute(select(EmployeeCommute))
    ecs = result.scalars().all()
    
    total_cpfl = 0.0
    for ec in ecs:
        dis = ec.mileage * 2
        gas = ec.unit_consumption / 100 * dis
        cpfl = calc_employee_commute_emission(ec.car_power_type, gas, dis)
        total_cpfl += cpfl
        
    return total_cpfl * 0.75  # 增加修正系数
