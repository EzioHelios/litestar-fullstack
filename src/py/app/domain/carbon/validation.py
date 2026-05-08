"""
碳数据填报校验（参考 PRD 5.2、7）。

- 数值非负、日期非未来、异常波动提示等。
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

# 校验失败时抛出，由控制器捕获返回 400
class CarbonValidationError(ValueError):
    """碳数据校验错误。"""
    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)


def _to_decimal(v: Any) -> Decimal | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return v
    try:
        return Decimal(str(v))
    except Exception:
        return None


def validate_amount_non_negative(amount: Any, field_name: str = "消耗量") -> None:
    """校验数量/消耗量非负。"""
    d = _to_decimal(amount)
    if d is None:
        raise CarbonValidationError(f"{field_name}必须为有效数值", field=field_name)
    if d < 0:
        raise CarbonValidationError(f"{field_name}不能为负数", field=field_name)


def validate_date_not_future(d: date | str | None, field_name: str = "日期") -> None:
    """校验日期不为未来。"""
    if d is None:
        return
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d[:10])
        except ValueError:
            raise CarbonValidationError(f"{field_name}格式无效 (YYYY-MM-DD)", field=field_name)
    today = date.today()
    if d > today:
        raise CarbonValidationError(f"{field_name}不能晚于今天", field=field_name)


def validate_period_start_end(start: date | str | None, end: date | str | None) -> None:
    """校验账期起止：起 <= 止。"""
    if start is None or end is None:
        return
    if isinstance(start, str):
        try:
            start = date.fromisoformat(start[:10])
        except ValueError:
            raise CarbonValidationError("账期开始日期格式无效", field="period_start")
    if isinstance(end, str):
        try:
            end = date.fromisoformat(end[:10])
        except ValueError:
            raise CarbonValidationError("账期结束日期格式无效", field="period_end")
    if start > end:
        raise CarbonValidationError("账期开始日期不能晚于结束日期", field="period_end")


def validate_consumption(amount: Any, field_name: str = "消耗量") -> None:
    """
    通用消耗量校验：非负、数值有效。
    PRD 7：serializers 增加校验逻辑（validate_consumption），确保符合物理常识。
    """
    validate_amount_non_negative(amount, field_name)


def validate_billing_month(value: str | None) -> None:
    """账期格式 YYYY-MM。"""
    if not value or len(value) < 7:
        return
    try:
        y, m = int(value[:4]), int(value[4:6]) if value[4:6].isdigit() else int(value[5:7])
        if m < 1 or m > 12:
            raise CarbonValidationError("账期月份需在 01-12", field="billing_month")
    except (ValueError, IndexError):
        raise CarbonValidationError("账期格式应为 YYYY-MM", field="billing_month")
