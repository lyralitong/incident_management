"""Offline, deterministic orchestration for normalized grading evidence.

Network adapters and policy evaluators are intentionally outside this module.
They must provide normalized records and a policy evaluation before this
workflow can produce a computed result.
"""

from __future__ import annotations

from typing import Any

from grading_core import GradingInputError, calculate_l0s, detect_recovery_start

GRADE_ORDER = {f"P{i}": i for i in range(0, 10)}


def compute_metric(metric: dict[str, Any]) -> dict[str, Any]:
    required = ("metric_name", "value_field", "records", "core_grade", "drop_ratio", "duration_minutes")
    missing = [key for key in required if key not in metric]
    if missing:
        return {"status": "pending", "metric_name": metric.get("metric_name"), "uncertainties": [f"缺少字段：{', '.join(missing)}"]}
    try:
        recovery = detect_recovery_start(
            metric["records"],
            metric["value_field"],
            start_index=int(metric.get("start_index", 0)),
        )
        l0s = calculate_l0s(
            core_grade=metric["core_grade"],
            drop_ratio=metric["drop_ratio"],
            duration_minutes=metric["duration_minutes"],
            factor=metric.get("factor"),
            responsibility=metric.get("responsibility"),
            business_applicable=bool(metric.get("business_applicable", False)),
        )
    except (KeyError, TypeError, ValueError, GradingInputError) as exc:
        return {"status": "blocked", "metric_name": metric.get("metric_name"), "uncertainties": [str(exc)]}
    result = {
        "status": "computed" if recovery is not None else "pending",
        "metric_name": metric["metric_name"],
        "core_grade": metric["core_grade"],
        "recovery": recovery,
        "l0s": {key: str(value) if key == "minutes" and value is not None else value for key, value in l0s.items()},
        "uncertainties": [] if recovery is not None else ["观察窗口内未形成已确认的开始回升时间"],
    }
    return result


def compute_result(case: dict[str, Any], metrics: list[dict[str, Any]], policy_version: str) -> dict[str, Any]:
    """Build the stable result envelope consumed by the report renderer."""
    computed = [compute_metric(metric) for metric in metrics]
    grades = [item["core_grade"] for item in computed if item.get("core_grade") in GRADE_ORDER]
    # P0 is more severe than P1, so the lowest numeric grade wins.
    final_grade = min(grades, key=lambda grade: GRADE_ORDER[grade]) if grades else None
    if not computed:
        status = "blocked"
    elif any(item["status"] == "blocked" for item in computed):
        status = "blocked"
    elif any(item["status"] == "pending" for item in computed):
        status = "pending"
    else:
        status = "computed"
    uncertainties = [item for result in computed for item in result.get("uncertainties", [])]
    return {
        "status": status,
        "final_grade": final_grade,
        "metrics": computed,
        "evidence": case.get("evidence", []),
        "policy_version": policy_version,
        "l0s": None,
        "uncertainties": uncertainties,
    }
