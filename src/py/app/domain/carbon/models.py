from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import BigIntAuditBase, BigIntBase
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.db.models import User


class DataFeatureMixin:
    """通用数据特征属性（Scope1/2/3 公共）。"""

    data_source: Mapped[str] = mapped_column(String(20))
    collection_method: Mapped[str] = mapped_column(String(20))
    confidence_level: Mapped[str] = mapped_column(String(10))
    data_year_type: Mapped[str] = mapped_column(String(20))
    data_year: Mapped[int | None] = mapped_column(Integer)


class EnterpriseInfo(BigIntBase):
    """企业信息（对应 Django dataapp.EnterpriseInfo）。"""

    __tablename__ = "dataapp_enterpriseinfo"

    name: Mapped[str | None] = mapped_column(String(100))
    belong_unit: Mapped[str | None] = mapped_column(String(100))
    people_count: Mapped[int | None] = mapped_column(Integer)
    park_area: Mapped[float | None] = mapped_column(Float)
    unify_code: Mapped[str | None] = mapped_column(String(30))
    industry: Mapped[str | None] = mapped_column(String(30))
    store_area: Mapped[float | None] = mapped_column(Float)
    green_area: Mapped[float | None] = mapped_column(Float)
    location: Mapped[str | None] = mapped_column(String(50))
    other_info: Mapped[dict | None] = mapped_column(comment="其他信息")


class EmployeeCommute(BigIntBase):
    """员工通勤（对应 Django dataapp.EmployeeCommute）。"""

    __tablename__ = "dataapp_employeecommute"

    name: Mapped[str] = mapped_column(String(10))
    category: Mapped[str | None] = mapped_column(String(10))
    car_power_type: Mapped[int | None] = mapped_column(Integer, default=1, doc="0=柴油, 1=汽油, 2=电力")
    mileage: Mapped[float | None] = mapped_column(Float, default=0.0)
    unit_consumption: Mapped[float | None] = mapped_column(Float, default=0.0)


class MonitorSector(BigIntBase):
    """监控区域（对应 Django dataapp.MonitorSector）。"""

    __tablename__ = "dataapp_monitorsector"

    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str | None] = mapped_column(String(100))
    area: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    area_id: Mapped[int | None] = mapped_column(Integer)
    is_enable: Mapped[bool | None] = mapped_column(Boolean, default=True)

    photos: Mapped[list["MonitorSectorPhoto"]] = relationship(
        back_populates="sector",
        lazy="selectin",
    )


class MonitorSectorPhoto(BigIntBase):
    """监控区域照片（对应 Django dataapp.MonitorSectorPhoto）。"""

    __tablename__ = "dataapp_monitorsectorphoto"

    path: Mapped[str | None] = mapped_column(String(255))
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorsector.id", ondelete="SET NULL"),
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text)
    area_id: Mapped[int | None] = mapped_column(Integer)

    sector: Mapped[MonitorSector | None] = relationship(
        back_populates="photos",
        lazy="selectin",
    )


class InMoney(BigIntBase):
    """入库金额管理（对应 Django dataapp.InMoney）。"""

    __tablename__ = "dataapp_inmoney"

    rkdbh: Mapped[str] = mapped_column(String(20), default="")
    gysmc: Mapped[str | None] = mapped_column(String(100))
    gysbm: Mapped[str | None] = mapped_column(String(15))
    rkrq: Mapped[str | None] = mapped_column(String(30))
    wlbh: Mapped[str | None] = mapped_column(String(15))
    wlms: Mapped[str | None] = mapped_column(String(300))
    pc: Mapped[str | None] = mapped_column(String(15))
    jldw: Mapped[str | None] = mapped_column(String(10))
    shsl: Mapped[float | None] = mapped_column(Float)
    shdj: Mapped[float | None] = mapped_column(Float)
    shje: Mapped[float | None] = mapped_column(Float)
    ckmc: Mapped[str | None] = mapped_column(String(50))
    add_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OutMoney(BigIntBase):
    """出库金额管理（对应 Django dataapp.OutMoney）。"""

    __tablename__ = "dataapp_outmoney"

    ckdbh: Mapped[str] = mapped_column(String(20), default="")
    xmmc: Mapped[str | None] = mapped_column(String(200))
    xmdy: Mapped[str | None] = mapped_column(String(15))
    wlbm: Mapped[str | None] = mapped_column(String(15))
    wlms: Mapped[str | None] = mapped_column(String(300))
    pc: Mapped[str | None] = mapped_column(String(15))
    jldw: Mapped[str | None] = mapped_column(String(10))
    sfsl: Mapped[float | None] = mapped_column(Float)
    dj: Mapped[float | None] = mapped_column(Float)
    je: Mapped[float | None] = mapped_column(Float)
    gzrq: Mapped[str | None] = mapped_column(String(30))
    gysmc: Mapped[str | None] = mapped_column(String(100))
    gc: Mapped[str | None] = mapped_column(String(100))
    lldh: Mapped[str | None] = mapped_column(String(15))
    ckdd: Mapped[str | None] = mapped_column(String(100))
    add_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MonitorEquipment(BigIntBase):
    """监控终端：电表、光伏、摄像头（对应 Django dataapp.MonitorEquipment）。"""

    __tablename__ = "dataapp_monitorequipment"

    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(30))
    code2: Mapped[str | None] = mapped_column(String(30))
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorsector.id", ondelete="SET NULL"),
        index=True,
    )
    category: Mapped[int | None] = mapped_column(Integer, doc="0=电表,1=光伏,2=视频摄像头")
    supplier: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[int | None] = mapped_column(Integer, doc="0=在线,1=故障")
    trip_state: Mapped[int | None] = mapped_column(Integer, doc="0=合闸,1=跳闸")
    location: Mapped[str | None] = mapped_column(String(50))
    install_time: Mapped[datetime | None] = mapped_column(DateTime)
    sort_index: Mapped[int | None] = mapped_column(Integer, default=0)
    is_enable: Mapped[bool | None] = mapped_column(Boolean, default=True)
    # 采集协议：用于 DataCollectorFactory 选择适配器（参考 PRD 4.1）
    protocol: Mapped[str | None] = mapped_column(
        String(20), default="http_yunji", doc="MQTT | modbus | http_yunji"
    )

    sector: Mapped[MonitorSector | None] = relationship(
        backref="equipments",
        lazy="selectin",
    )


class AmmeterIndexValue(BigIntBase):
    """电表终端数值管理（对应 Django dataapp.AmmeterIndexValue）。"""

    __tablename__ = "dataapp_ammeterindexvalue"

    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorequipment.id", ondelete="SET NULL"),
        index=True,
    )
    zygdn: Mapped[float | None] = mapped_column(Float)
    fygdn: Mapped[float | None] = mapped_column(Float)
    zwgdn: Mapped[float | None] = mapped_column(Float)
    fwgdn: Mapped[float | None] = mapped_column(Float)
    zygdnsz: Mapped[float | None] = mapped_column(Float)
    fygdnsz: Mapped[float | None] = mapped_column(Float)
    zwgdnsz: Mapped[float | None] = mapped_column(Float)
    fwgdnsz: Mapped[float | None] = mapped_column(Float)
    reading_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    ammeter_id: Mapped[str | None] = mapped_column(String(20), index=True)
    ammeter_name: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(50))
    area_id: Mapped[str | None] = mapped_column(String(20), index=True)
    area_name: Mapped[str | None] = mapped_column(String(50))
    radio: Mapped[int | None] = mapped_column(Integer, default=1)
    start_time: Mapped[datetime | None] = mapped_column(DateTime)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)
    data_source: Mapped[int | None] = mapped_column(Integer, doc="0=云集,1=红外")
    add_time: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)


class VideoMonitor(BigIntBase):
    """视频监控（对应 Django dataapp.VideoMonitor）。"""

    __tablename__ = "dataapp_videomonitor"

    location: Mapped[str | None] = mapped_column(String(100))
    f_area: Mapped[str | None] = mapped_column(String(50))
    f_area_type: Mapped[str | None] = mapped_column(String(10))
    video_url: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[int | None] = mapped_column(Integer, doc="0=在线,1=故障")
    ip_address: Mapped[str | None] = mapped_column(String(20))
    install_height: Mapped[float | None] = mapped_column(Float, default=0.0)
    install_method: Mapped[str | None] = mapped_column(String(20))
    vedio_type: Mapped[str | None] = mapped_column(String(20))
    pixel: Mapped[str | None] = mapped_column(String(10))
    brand: Mapped[str | None] = mapped_column(String(20))
    b_model: Mapped[str | None] = mapped_column(String(30))
    install_time: Mapped[str | None] = mapped_column(String(30))
    install_x: Mapped[float | None] = mapped_column(Float)
    install_y: Mapped[float | None] = mapped_column(Float)
    add_time: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)


class ApiResultKeyMapping(BigIntBase):
    """API 结果中英文映射（对应 Django dataapp.ApiResultKeyMapping）。"""

    __tablename__ = "dataapp_apiresultkeymapping"

    key_name: Mapped[str | None] = mapped_column(String(30))
    cn_name: Mapped[str | None] = mapped_column(String(30))


class WarningRule(BigIntBase):
    """预警规则设置（对应 Django dataapp.WarningRule）。"""

    __tablename__ = "dataapp_warningrule"

    name: Mapped[str] = mapped_column(String(30), default="")
    description: Mapped[str | None] = mapped_column(Text)
    range_val: Mapped[dict | None] = mapped_column(comment="取值范围")
    event_type: Mapped[int] = mapped_column(Integer, default=1, doc="1=设备故障, 2=用电异常, 3=发电异常, 4=碳排放异常")
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorsector.id", ondelete="SET NULL"),
        index=True,
    )
    table_name: Mapped[str | None] = mapped_column(String(30))


class AlarmEvent(BigIntBase):
    """预警事件（对应 Django dataapp.AlarmEvent）。"""

    __tablename__ = "dataapp_alarmevent"

    rule_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_warningrule.id", ondelete="SET NULL"),
        index=True,
    )
    event_type: Mapped[int] = mapped_column(Integer, doc="1=设备故障, 2=用电异常, 3=发电异常, 4=碳排放异常")
    event_desc: Mapped[str | None] = mapped_column(String(300))
    event_time: Mapped[datetime | None] = mapped_column(DateTime)
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorsector.id", ondelete="SET NULL"),
        index=True,
    )
    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_monitorequipment.id", ondelete="SET NULL"),
        index=True,
    )
    add_time: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    is_handle: Mapped[bool | None] = mapped_column(Boolean, default=False)


class VedioAlarmEvent(BigIntBase):
    """摄像头预警事件（对应 Django dataapp.VedioAlarmEvent）。"""

    __tablename__ = "dataapp_vedioalarmevent"

    event_type: Mapped[int] = mapped_column(Integer, doc="1=未佩戴安全帽, 2=烟火, 3=火点, 4=区域入侵")
    event_desc: Mapped[str | None] = mapped_column(String(300))
    event_time: Mapped[datetime | None] = mapped_column(DateTime)
    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataapp_videomonitor.id", ondelete="SET NULL"),
        index=True,
    )
    add_time: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)
    is_handle: Mapped[bool | None] = mapped_column(Boolean, default=False)


class EnergyStorageValue(BigIntBase):
    """储能量（对应 Django dataapp.EnergyStorageValue）。"""

    __tablename__ = "dataapp_energystoragevalue"

    cn_total: Mapped[float | None] = mapped_column(Float, default=100)
    ratio_total: Mapped[float | None] = mapped_column(Float, default=1)
    cn1: Mapped[float | None] = mapped_column(Float, default=50)
    ratio1: Mapped[float | None] = mapped_column(Float, default=0.5)
    cn2: Mapped[float | None] = mapped_column(Float, default=50)
    ratio2: Mapped[float | None] = mapped_column(Float, default=0.5)


class CarbonAuditBase(BigIntAuditBase, DataFeatureMixin):
    """碳排放业务记录基类。"""

    __abstract__ = True

    status: Mapped[str] = mapped_column(String(20), default="draft")
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("user_account.id", ondelete="SET NULL"), index=True)
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("user_account.id", ondelete="SET NULL"), index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    reject_reason: Mapped[str | None] = mapped_column(Text)


class Scope1MobileCombustion(CarbonAuditBase):
    """Scope1 移动源燃烧（自有车辆/叉车）。"""

    __tablename__ = "dataapp_scope1mobilecombustion"

    record_date: Mapped[date] = mapped_column(Date)
    asset_id: Mapped[str | None] = mapped_column(String(64))
    asset_name: Mapped[str | None] = mapped_column(String(64))
    fuel_type: Mapped[str] = mapped_column(String(16))
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    unit: Mapped[str] = mapped_column(String(5))
    mileage_km: Mapped[Numeric | None] = mapped_column(Numeric(10, 2))
    work_hours: Mapped[Numeric | None] = mapped_column(Numeric(10, 2))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class Scope1StationaryCombustion(CarbonAuditBase):
    """Scope1 固定源燃烧（食堂/锅炉/发电机等）。"""

    __tablename__ = "dataapp_scope1stationarycombustion"

    facility_name: Mapped[str] = mapped_column(String(64))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    fuel_type: Mapped[str] = mapped_column(String(16))
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    unit: Mapped[str] = mapped_column(String(5))
    meter_reading_start: Mapped[Numeric | None] = mapped_column(Numeric(14, 4))
    meter_reading_end: Mapped[Numeric | None] = mapped_column(Numeric(14, 4))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class Scope1RefrigerantLeak(CarbonAuditBase):
    """Scope1 逸散排放（制冷剂填充/泄漏）。"""

    __tablename__ = "dataapp_scope1refrigerantleak"

    device_id: Mapped[str | None] = mapped_column(String(64))
    device_name: Mapped[str | None] = mapped_column(String(64))
    fill_date: Mapped[date] = mapped_column(Date)
    refrigerant_type: Mapped[str] = mapped_column(String(32))
    amount_kg: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    leak_type: Mapped[str] = mapped_column(String(16))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class Scope2ElectricityBill(CarbonAuditBase):
    """Scope2 电费账单（用于校准/补全电力数据）。"""

    __tablename__ = "dataapp_scope2electricitybill"

    account_number: Mapped[str] = mapped_column(String(64))
    billing_month: Mapped[str] = mapped_column(String(7))
    total_kwh: Mapped[Numeric] = mapped_column(Numeric(16, 4))
    peak_kwh: Mapped[Numeric | None] = mapped_column(Numeric(16, 4))
    flat_kwh: Mapped[Numeric | None] = mapped_column(Numeric(16, 4))
    valley_kwh: Mapped[Numeric | None] = mapped_column(Numeric(16, 4))
    amount_cny: Mapped[Numeric | None] = mapped_column(Numeric(16, 2))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class Scope3WasteDisposal(CarbonAuditBase):
    """Scope3 废弃物处理。"""

    __tablename__ = "dataapp_scope3wastedisposal"

    date: Mapped[date] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(32))
    weight_ton: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    treatment_method: Mapped[str] = mapped_column(String(16))
    vendor_name: Mapped[str | None] = mapped_column(String(128))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class Scope3ThirdPartyTransport(CarbonAuditBase):
    """Scope3 外购运输（外包车队）。"""

    __tablename__ = "dataapp_scope3thirdpartytransport"

    waybill_no: Mapped[str] = mapped_column(String(64))
    origin: Mapped[str] = mapped_column(String(128))
    destination: Mapped[str] = mapped_column(String(128))
    vehicle_type: Mapped[str] = mapped_column(String(32))
    distance_km: Mapped[Numeric] = mapped_column(Numeric(12, 2))
    load_ton: Mapped[Numeric] = mapped_column(Numeric(12, 4))
    fuel_amount: Mapped[Numeric | None] = mapped_column(Numeric(12, 4))
    attachment: Mapped[str | None] = mapped_column(String(255))
    remark: Mapped[str | None] = mapped_column(Text)


class EmissionFactor(BigIntAuditBase):
    """排放因子库（对应 Django dataapp.EmissionFactor）。"""

    __tablename__ = "dataapp_emissionfactor"

    scope: Mapped[str] = mapped_column(String(10))
    category: Mapped[str] = mapped_column(String(20))
    sub_category: Mapped[str] = mapped_column(String(64))
    unit: Mapped[str] = mapped_column(String(20))
    factor_value: Mapped[Numeric] = mapped_column(Numeric(18, 8))
    factor_unit: Mapped[str] = mapped_column(String(32), default="kgCO2e")
    year: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(Text)


class IotTelemetry(BigIntBase):
    """IoT 设备上报时序数据（对应 Django dataapp.IotTelemetry）。"""

    __tablename__ = "dataapp_iottelemetry"

    site_id: Mapped[str] = mapped_column(String(64), index=True)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[int] = mapped_column(Integer)
    reading_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    active_power: Mapped[float | None] = mapped_column(Float)
    reactive_power: Mapped[float | None] = mapped_column(Float)
    voltage_a: Mapped[float | None] = mapped_column(Float)
    current_a: Mapped[float | None] = mapped_column(Float)
    total_energy: Mapped[float | None] = mapped_column(Float)
    interval: Mapped[str] = mapped_column(String(8), default="raw")
    raw_payload: Mapped[dict | None] = mapped_column(comment="原始 JSON 报文")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow)


class CarbonAuditLog(BigIntBase):
    """审核操作日志（对应 Django dataapp.AuditLog，表名与 Django 一致）。"""

    __tablename__ = "dataapp_carbonauditlog"

    record_type: Mapped[str] = mapped_column(String(64))
    record_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(16))
    operator_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_account.id", ondelete="SET NULL"), index=True)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
