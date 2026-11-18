import unittest
from decimal import Decimal

from grading_core import calculate_l0s, detect_recovery_start, fault_minute_points


class GradingCoreTests(unittest.TestCase):
    def test_recovery_candidate_is_not_delayed_by_confirmations(self):
        records = [
            {"__time": f"2026-10-12T14:{minute:02d}:00+08:00", "num": value}
            for minute, value in [(48, 9590), (49, 9675), (50, 10041), (51, 10844)]
        ]
        result = detect_recovery_start(records, "num")
        self.assertEqual(result["valley_time"], "2026-10-12T14:48:00+08:00")
        self.assertEqual(result["candidate_time"], "2026-10-12T14:49:00+08:00")
        self.assertEqual(len(result["confirmation"]), 2)

    def test_recovery_candidate_is_rejected_when_new_low_appears(self):
        records = [
            {"__time": f"2026-10-12T14:{minute:02d}:00+08:00", "num": value}
            for minute, value in [(48, 9590), (49, 9675), (50, 9500), (51, 9700), (52, 9800), (53, 9900)]
        ]
        result = detect_recovery_start(records, "num")
        self.assertEqual(result["candidate_time"], "2026-10-12T14:51:00+08:00")
        self.assertEqual(result["rejected_candidates"][0]["candidate"], "2026-10-12T14:49:00+08:00")

    def test_inclusive_minute_points(self):
        from datetime import datetime
        start = datetime.fromisoformat("2026-10-12T14:41:00+08:00")
        end = datetime.fromisoformat("2026-10-12T14:51:00+08:00")
        self.assertEqual(fault_minute_points(start, end), 11)
        with self.assertRaisesRegex(ValueError, "整分钟"):
            fault_minute_points(start.replace(second=1), end)

    def test_l0s_rules_and_pending_state(self):
        result = calculate_l0s(core_grade="P2", drop_ratio=Decimal("0.4"), duration_minutes=10, factor="core_metric", responsibility="confirmed_non_third_party", business_applicable=True)
        self.assertEqual(result["minutes"], Decimal("8.0"))
        pending = calculate_l0s(core_grade="P2", drop_ratio=0.4, duration_minutes=10, factor="core_metric", responsibility=None, business_applicable=True)
        self.assertEqual(pending["status"], "pending")
        self.assertIsNone(pending["minutes"])


if __name__ == "__main__":
    unittest.main()
