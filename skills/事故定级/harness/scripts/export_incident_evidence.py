#!/usr/bin/env python3
"""Export aligned incident/baseline minute data to an auditable Excel workbook."""

import argparse
import json
import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill


TZ = ZoneInfo("Asia/Shanghai")
MINUTE = timedelta(minutes=1)
FIELDS = ("order_cnt", "num", "y")


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=TZ)
    return result.astimezone(TZ)


def numeric(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"指标值必须是 JSON 数字，收到 {value!r}")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"指标值必须是非负有限数，收到 {value!r}")
    return value


def minute_series(records, start, end):
    if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
        raise ValueError("records 必须是监控返回的记录数组，不能是错误信封")
    field = next((f for f in FIELDS if any(f in r for r in records)), None)
    if records and field is None:
        raise ValueError("记录中没有 order_cnt、num 或 y 数值字段")
    points = {}
    for record in records:
        t = timestamp(record["__time"])
        if not start <= t <= end:
            continue
        if t.second or t.microsecond:
            raise ValueError(f"记录不是分钟级时间戳：{record['__time']}")
        if t in points:
            raise ValueError(f"重复分钟 {t.isoformat()}，请先确认指标维度，禁止直接相加")
        value = record.get(field)
        points[t] = None if value is None else numeric(value)
    return points, field


def prepare(payload):
    for key in ("business", "metric_name", "metric_id", "unit", "source", "standard_url"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"缺少非空字符串 {key}")
    start = timestamp(payload["incident_start"])
    recovery = timestamp(payload["recovery_start"])
    if recovery < start:
        raise ValueError("开始恢复时间早于开始下跌时间")
    baseline_date = date.fromisoformat(payload["baseline_date"])
    if baseline_date >= start.date():
        raise ValueError("同比日期必须是故障日期之前的历史日期")
    shift = timedelta(days=(baseline_date - start.date()).days)
    fault_start = start.replace(second=0, microsecond=0)
    fault_end = recovery.replace(second=0, microsecond=0)
    window_start = fault_start - 10 * MINUTE
    window_end = fault_end + 10 * MINUTE
    actual, actual_field = minute_series(
        payload["incident_records"], window_start, window_end
    )
    baseline, baseline_field = minute_series(
        payload["baseline_records"], window_start + shift, window_end + shift
    )
    rows = []
    t = window_start
    while t <= window_end:
        b, a = baseline.get(t + shift), actual.get(t)
        rows.append((t, t + shift, b, a, fault_start <= t <= fault_end))
        t += MINUTE
    fault_rows = [r for r in rows if r[4]]
    fault_missing = sum(r[2] is None or r[3] is None for r in fault_rows)
    missing_cells = sum(int(r[2] is None) + int(r[3] is None) for r in rows)
    b = None if fault_missing else sum(r[2] for r in fault_rows)
    a = None if fault_missing else sum(r[3] for r in fault_rows)
    impact = None if fault_missing else max(b - a, 0)
    formula = "max(B−A, 0)"
    if "impact_amount" in payload:
        if not isinstance(payload.get("impact_formula"), str) or not payload["impact_formula"].strip():
            raise ValueError("自定义 impact_amount 必须同时给出业务标准的 impact_formula")
        custom_impact = numeric(payload["impact_amount"])
        if not fault_missing:
            impact = custom_impact
        formula = payload["impact_formula"]
    daily = payload.get("baseline_day_total")
    if daily is not None:
        daily = numeric(daily)
    summary = {
        "business": payload["business"],
        "metric": payload["metric_name"],
        "incident_start": start.isoformat(),
        "recovery_start": recovery.isoformat(),
        "baseline_date": baseline_date.isoformat(),
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "minute_rows": len(rows),
        "fault_minute_points": len(fault_rows),
        "missing_cells": missing_cells,
        "fault_missing_minutes": fault_missing,
        "A": a, "B": b, "I": impact, "C": daily,
        "drop_ratio": (b - a) / b if b is not None and b > 0 else None,
        "daily_impact_ratio": impact / daily if impact is not None and daily else None,
        "impact_formula": formula,
        "incident_value_field": actual_field,
        "baseline_value_field": baseline_field,
    }
    return {"payload": payload, "start": start, "recovery": recovery,
            "baseline_date": baseline_date, "rows": rows, "summary": summary}


def append_row(sheet, values):
    sheet.append(values)
    # Names and source text are data even when they start with an Excel '='.
    for cell in sheet[sheet.max_row]:
        if isinstance(cell.value, str):
            cell.data_type = "s"


def style_headers(sheet, count):
    for row in sheet.iter_rows(min_row=1, max_row=count):
        for cell in row:
            cell.font = Font(name="Arial", bold=True)
            cell.fill = PatternFill("solid", fgColor="E7EDF5")
            cell.alignment = Alignment(horizontal="center")


def write_item(book, item, index):
    payload, rows, summary = item["payload"], item["rows"], item["summary"]
    safe_name = re.sub(r"[\[\]:*?/\\]", "_", payload["metric_name"])
    sheet = book.create_sheet(f"{index}_{safe_name}"[:31])
    append_row(sheet, [None, item["baseline_date"], item["start"].date()])
    append_row(sheet, ["时间", payload["metric_name"], payload["metric_name"]])
    sheet["B1"].number_format = sheet["C1"].number_format = "yyyy/m/d"
    crosses_midnight = rows[0][0].date() != rows[-1][0].date()
    for actual_time, _, b, a, in_fault in rows:
        append_row(sheet, [actual_time.replace(tzinfo=None),
                           b if b is not None else "缺失",
                           a if a is not None else "缺失"])
        sheet.cell(sheet.max_row, 1).number_format = (
            "yyyy-mm-dd hh:mm" if crosses_midnight else "hh:mm"
        )
        for col in (2, 3):
            cell = sheet.cell(sheet.max_row, col)
            cell.number_format = "#,##0.########"
            if cell.value == "缺失":
                cell.fill = PatternFill("solid", fgColor="FCE4D6")
            elif in_fault:
                cell.fill = PatternFill("solid", fgColor="FFF2CC")
    style_headers(sheet, 2)
    sheet.freeze_panes = "B3"
    sheet.column_dimensions["A"].width = 23 if crosses_midnight else 12
    sheet.column_dimensions["B"].width = sheet.column_dimensions["C"].width = 22

    raw = book.create_sheet(f"{index}_完整时间明细")
    append_row(raw, ["同比完整时间", payload["metric_name"] + "（同比）",
                     "故障完整时间", payload["metric_name"] + "（故障当天）", "是否故障时段"])
    for actual_time, baseline_time, b, a, in_fault in rows:
        append_row(raw, [baseline_time.replace(tzinfo=None), b if b is not None else "缺失",
                         actual_time.replace(tzinfo=None), a if a is not None else "缺失", in_fault])
        for col in (1, 3):
            raw.cell(raw.max_row, col).number_format = "yyyy-mm-dd hh:mm:ss"
    style_headers(raw, 1)
    raw.freeze_panes = "A2"
    for col in ("A", "B", "C", "D", "E"):
        raw.column_dimensions[col].width = 24

    info = book["计算依据"]
    for key, value in {
        **summary, "unit": payload["unit"], "metric_id": payload["metric_id"],
        "source": payload["source"], "standard_url": payload["standard_url"],
        "filters": json.dumps(payload.get("filters", {}), ensure_ascii=False),
        "timezone": "Asia/Shanghai", "source_granularity": "MINUTE",
        "window_rule": "故障起止分钟均包含；前后各10分钟不计入A、B、I",
    }.items():
        append_row(info, [index, payload["metric_name"], key,
                          value if value is not None else "无法计算/数据缺失"])
        if key in ("drop_ratio", "daily_impact_ratio") and value is not None:
            info.cell(info.max_row, 4).number_format = "0.00%"
    return sheet.title


def export(inputs, output):
    if output.suffix.lower() != ".xlsx":
        raise ValueError("输出必须是 .xlsx 文件")
    if output.exists():
        raise ValueError(f"输出文件已存在，请使用新的文件名：{output}")
    # Validate every input before writing a workbook.
    items = [prepare(json.loads(path.read_text(encoding="utf-8"))) for path in inputs]
    book = Workbook()
    book.remove(book.active)
    info = book.create_sheet("计算依据")
    append_row(info, ["序号", "影响指标", "字段", "值"])
    names = [write_item(book, item, i) for i, item in enumerate(items, 1)]
    # Put the screenshot-style comparison sheets before the supporting sheets.
    for i, name in enumerate(names):
        book.move_sheet(name, offset=i - book.sheetnames.index(name))
    style_headers(info, 1)
    info.freeze_panes = "A2"
    for col, width in {"A": 10, "B": 18, "C": 30, "D": 85}.items():
        info.column_dimensions[col].width = width
    output.parent.mkdir(parents=True, exist_ok=True)
    book.save(output)
    check = load_workbook(output, read_only=True, data_only=True)
    try:
        for name, item in zip(names, items):
            if check[name].max_row != len(item["rows"]) + 2:
                raise ValueError(f"Excel 回读行数不符：{name}")
    finally:
        check.close()
    return {"output": str(output.resolve()), "metrics": [i["summary"] for i in items]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, nargs="+", required=True,
                        help="每个 JSON 文件对应一个指标和一个同比日期")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = export(args.input, args.output)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"导出失败：{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
