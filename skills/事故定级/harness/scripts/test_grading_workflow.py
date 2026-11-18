import unittest

from grading_workflow import compute_result


class GradingWorkflowTests(unittest.TestCase):
    def test_result_envelope_is_stable_and_uses_highest_grade(self):
        records = [
            {"__time": f"2026-10-12T14:{minute:02d}:00+08:00", "num": value}
            for minute, value in [(48, 9590), (49, 9675), (50, 10041), (51, 10844)]
        ]
        result = compute_result(
            {"incident_id": "i-1", "evidence": [{"source": "fixture"}]},
            [
                {
                    "metric_name": "完单量",
                    "value_field": "num",
                    "records": records,
                    "start_index": 0,
                    "core_grade": "P2",
                    "drop_ratio": 0.4,
                    "duration_minutes": 10,
                    "factor": "core_metric",
                    "responsibility": "confirmed_non_third_party",
                    "business_applicable": True,
                },
                {
                    "metric_name": "呼叫量",
                    "value_field": "num",
                    "records": records,
                    "start_index": 0,
                    "core_grade": "P1",
                    "drop_ratio": 0.7,
                    "duration_minutes": 10,
                    "factor": "core_metric",
                    "responsibility": "confirmed_non_third_party",
                    "business_applicable": True,
                },
            ],
            "2026-11-12",
        )
        self.assertEqual(result["status"], "computed")
        self.assertEqual(result["final_grade"], "P1")
        self.assertEqual(result["policy_version"], "2026-11-12")
        self.assertEqual(result["metrics"][0]["recovery"]["candidate_time"], "2026-10-12T14:49:00+08:00")


if __name__ == "__main__":
    unittest.main()
