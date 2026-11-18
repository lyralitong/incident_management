"""Behavior checks using synthetic data only; no monitoring requests."""

import copy
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from openpyxl import load_workbook

from export_incident_evidence import MINUTE, export, prepare, timestamp


def fixture(start="2026-10-12T14:41:00+08:00", end="2026-10-12T14:51:00+08:00"):
    first, last = timestamp(start), timestamp(end)
    payload = {
        "business": "测试业务", "metric_name": "完单量", "metric_id": "test_metric",
        "unit": "单", "source": "synthetic-test", "standard_url": "https://example.test/standard",
        "incident_start": start, "recovery_start": end,
        "baseline_date": "2026-09-21", "baseline_day_total": 500000,
        "incident_records": [], "baseline_records": [],
    }
    shift = timedelta(days=(timestamp("2026-09-21").date() - first.date()).days)
    t = first - 10 * MINUTE
    while t <= last + 10 * MINUTE:
        # High padding values catch accidental inclusion in incident totals.
        inside = first <= t <= last
        payload["incident_records"].append({"__time": t.isoformat(), "num": 500 if inside else 99999})
        payload["baseline_records"].append({"__time": (t + shift).isoformat(), "num": 1000 if inside else 88888})
        t += MINUTE
    return payload


class EvidenceExportTests(unittest.TestCase):
    def test_only_fault_minutes_enter_totals(self):
        result = prepare(fixture())["summary"]
        self.assertEqual(result["minute_rows"], 31)
        self.assertEqual(result["fault_minute_points"], 11)
        self.assertEqual((result["A"], result["B"], result["I"]), (5500, 11000, 5500))
        self.assertEqual(result["drop_ratio"], .5)
        self.assertEqual(result["daily_impact_ratio"], .011)

    def test_zero_is_data_and_field_priority_is_respected(self):
        payload = fixture()
        for records in (payload["incident_records"], payload["baseline_records"]):
            for record in records:
                record.update(order_cnt=record["num"], num=999, y=999)
        payload["incident_records"][10]["order_cnt"] = 0
        result = prepare(payload)["summary"]
        self.assertEqual(result["incident_value_field"], "order_cnt")
        self.assertEqual(result["missing_cells"], 0)
        self.assertEqual(result["A"], 5000)
        self.assertEqual(result["I"], 6000)

    def test_missing_buffer_does_not_change_fault_totals(self):
        payload = fixture()
        payload["baseline_records"].pop(0)
        result = prepare(payload)["summary"]
        self.assertEqual(result["missing_cells"], 1)
        self.assertEqual(result["fault_missing_minutes"], 0)
        self.assertEqual(result["I"], 5500)

    def test_missing_fault_suppresses_results_even_with_override(self):
        payload = fixture()
        payload["incident_records"].pop(10)
        payload.update(impact_amount=20000, impact_formula="人工核验的业务公式示例")
        result = prepare(payload)["summary"]
        self.assertEqual(result["fault_missing_minutes"], 1)
        for field in ("A", "B", "I", "drop_ratio", "daily_impact_ratio"):
            self.assertIsNone(result[field])

    def test_cross_midnight_and_full_dates(self):
        item = prepare(fixture("2026-10-12T23:58:00+08:00", "2026-10-13T00:02:00+08:00"))
        self.assertEqual(len(item["rows"]), 25)
        self.assertEqual(item["rows"][0][0].isoformat(), "2026-10-12T23:48:00+08:00")
        self.assertEqual(item["rows"][-1][1].isoformat(), "2026-09-22T00:12:00+08:00")
        self.assertEqual(item["summary"]["I"], 2500)

    def test_duplicate_and_nonfinite_values_fail(self):
        payload = fixture()
        payload["incident_records"].append(copy.deepcopy(payload["incident_records"][10]))
        with self.assertRaisesRegex(ValueError, "重复分钟"):
            prepare(payload)
        payload = fixture()
        payload["incident_records"][0]["num"] = float("nan")
        with self.assertRaisesRegex(ValueError, "非负有限数"):
            prepare(payload)

    def test_utc_timestamps_align_with_shanghai(self):
        payload = fixture()
        for record in payload["baseline_records"]:
            record["__time"] = (timestamp(record["__time"]) - timedelta(hours=8)).replace(tzinfo=None).isoformat() + "Z"
        self.assertEqual(prepare(payload)["summary"]["missing_cells"], 0)

    def test_custom_impact_and_zero_daily_denominator(self):
        payload = fixture()
        payload.update(impact_amount=20000, impact_formula="真实需求×正常完成率−实际完单=20000", baseline_day_total=0)
        result = prepare(payload)["summary"]
        self.assertEqual(result["I"], 20000)
        self.assertIsNone(result["daily_impact_ratio"])

    def test_workbook_roundtrip_matches_layout_and_evidence(self):
        with tempfile.TemporaryDirectory(prefix="incident-evidence-test-") as directory:
            root = Path(directory)
            source, output = root / "source.json", root / "evidence.xlsx"
            payload = fixture()
            source.write_text(json.dumps(payload), encoding="utf-8")
            export([source], output)
            book = load_workbook(output, data_only=True)
            try:
                sheet = book.worksheets[0]
                self.assertEqual(sheet.max_row, 33)
                self.assertEqual(sheet["B1"].value.date().isoformat(), "2026-09-21")
                self.assertEqual(sheet["C1"].value.date().isoformat(), "2026-10-12")
                self.assertEqual([sheet.cell(2, i).value for i in range(1, 4)], ["时间", "完单量", "完单量"])
                self.assertEqual(sheet["A3"].value.strftime("%H:%M"), "14:31")
                self.assertEqual(sheet["A33"].value.strftime("%H:%M"), "15:01")
                self.assertEqual((sheet["B13"].value, sheet["C13"].value), (1000, 500))
                self.assertIn("1_完整时间明细", book.sheetnames)
                self.assertIn("计算依据", book.sheetnames)
            finally:
                book.close()
            with self.assertRaisesRegex(ValueError, "已存在"):
                export([source], output)


if __name__ == "__main__":
    unittest.main()
