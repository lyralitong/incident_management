"""Deterministic building blocks for the incident-grading domain harness.

This module deliberately contains no model calls or network requests. Adapters
fetch and normalize data; these functions validate and calculate only.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable


class GradingInputError(ValueError):
    """Raised when a normalized grading input is not auditable."""


def _number(value: Any) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise GradingInputError(f"指标值不是数字：{value!r}")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise GradingInputError(f"指标值不是数字：{value!r}") from exc
    if not result.is_finite() or result < 0:
        raise GradingInputError(f"指标值必须是非负有限数：{value!r}")
    return result


def _time(record: dict[str, Any]) -> datetime:
    raw = record.get("__time")
    if not isinstance(raw, str):
        raise GradingInputError("记录缺少 __time")
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def fault_minute_points(start: datetime, end: datetime) -> int:
    """Return the inclusive number of minute buckets between two endpoints."""
    if start.second or start.microsecond or end.second or end.microsecond:
        raise GradingInputError("故障端点必须按整分钟对齐")
    seconds = (end.replace(second=0, microsecond=0) - start.replace(second=0, microsecond=0)).total_seconds()
    if seconds < 0 or seconds % 60:
        raise GradingInputError("故障端点必须按分钟对齐且开始时间不晚于结束时间")
    return int(seconds // 60) + 1


def detect_recovery_start(
    records: Iterable[dict[str, Any]],
    value_field: str,
    start_index: int = 0,
    confirmations: int = 2,
) -> dict[str, Any] | None:
    """Find the first confirmed rise after a valley.

    The candidate is the first bucket strictly above the current valley. The
    following ``confirmations`` buckets are evidence only; they do not move the
    reported recovery time. A candidate is rejected if those buckets return to
    the valley or below it. A later lower point starts a new valley search.
    """
    rows = sorted(records, key=_time)
    if not rows or not 0 <= start_index < len(rows):
        return None
    values = [_number(row.get(value_field)) for row in rows]
    valley_index = start_index
    valley = values[valley_index]
    rejected: list[dict[str, Any]] = []
    i = valley_index + 1
    while i < len(rows):
        value = values[i]
        if value < valley:
            valley_index, valley = i, value
            i += 1
            continue
        if value == valley:
            i += 1
            continue
        confirmation_rows = rows[i + 1 : i + 1 + confirmations]
        if len(confirmation_rows) < confirmations:
            return None
        confirmation_values = [values[i + 1 + offset] for offset in range(confirmations)]
        if any(item <= valley for item in confirmation_values):
            rejected.append({
                "candidate": rows[i]["__time"],
                "candidate_value": str(value),
                "reason": "后续分钟重新探至谷底或更低",
            })
            i += 1
            continue
        return {
            "valley_time": rows[valley_index]["__time"],
            "valley_value": str(valley),
            "candidate_time": rows[i]["__time"],
            "candidate_value": str(value),
            "confirmation": [
                {"time": row["__time"], "value": str(values[i + 1 + offset])}
                for offset, row in enumerate(confirmation_rows)
            ],
            "rejected_candidates": rejected,
        }
    return None


def calculate_l0s(
    *,
    core_grade: str | None,
    drop_ratio: Decimal | float | int | None,
    duration_minutes: Decimal | float | int | None,
    factor: str | None,
    responsibility: str | None,
    business_applicable: bool,
) -> dict[str, Any]:
    """Calculate L0S using the core metric path only.

    ``pending`` is intentional when responsibility or grading factor is not
    confirmed. It must not be rendered as zero by a caller.
    """
    if not business_applicable:
        return {"status": "not_applicable", "minutes": Decimal("0"), "formula": "不适用", "reason": "业务方不在 L0S 适用范围"}
    if factor is None or responsibility is None:
        return {"status": "pending", "minutes": None, "formula": "待定", "reason": "定级因素或责任属性未确认"}
    if factor != "core_metric":
        return {"status": "not_applicable", "minutes": Decimal("0"), "formula": "不适用", "reason": "不是核心指标路径"}
    if responsibility == "third_party":
        return {"status": "not_applicable", "minutes": Decimal("0"), "formula": "不适用", "reason": "已确认第三方责任"}
    if responsibility != "confirmed_non_third_party":
        return {"status": "pending", "minutes": None, "formula": "待定", "reason": "责任属性未确认"}
    if core_grade not in {"P1", "P2", "P3"}:
        return {"status": "not_applicable", "minutes": Decimal("0"), "formula": "不适用", "reason": "核心指标路径不是 P1-P3"}
    if drop_ratio is None or duration_minutes is None:
        return {"status": "pending", "minutes": None, "formula": "待定", "reason": "缺少故障时长或实际下跌比例"}
    ratio = _number(drop_ratio)
    duration = _number(duration_minutes)
    if ratio > 1:
        raise GradingInputError("下跌比例必须使用 0 到 1 的小数")
    if core_grade == "P1":
        formula, minutes = "T", duration
    elif core_grade == "P2" and ratio >= Decimal("0.5"):
        formula, minutes = "T", duration
    elif core_grade == "P2":
        formula, minutes = "T × r × 2", duration * ratio * 2
    else:
        formula, minutes = "T × r", duration * ratio
    return {
        "status": "computed",
        "minutes": minutes,
        "formula": formula,
        "inputs": {"T": str(duration), "r": str(ratio), "core_grade": core_grade},
        "reason": "核心指标路径且已确认非第三方责任",
    }
