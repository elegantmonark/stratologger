"""Fault cases for the mission log checker.

Author: Trishan Biswas
Project started: February 2026
"""

from pathlib import Path
import tempfile
import unittest

from log_audit import audit
from run_log_campaign import build_cases


class LogAuditTests(unittest.TestCase):
    def test_fault_campaign(self):
        with tempfile.TemporaryDirectory() as folder:
            for name, raw, expected in build_cases():
                with self.subTest(case=name):
                    path = Path(folder) / "case.csv"
                    path.write_bytes(raw)
                    report = audit(path)
                    if expected:
                        self.assertTrue(expected.issubset(report.errors), report.to_dict())
                    else:
                        self.assertEqual(report.error_count, 0)
                    if name == "counter_rollovers":
                        self.assertEqual(report.packet_rollovers, 1)
                        self.assertEqual(report.timestamp_rollovers, 1)

    def test_existing_format_example(self):
        path = Path(__file__).resolve().parents[1] / "data/format-example.csv"
        self.assertEqual(audit(path).error_count, 0)

    def test_late_sampling_threshold_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "case.csv"
            path.write_bytes(build_cases()[0][1])
            self.assertEqual(audit(path, max_interval_ms=499).errors["timing_gap"], 599)
            self.assertEqual(audit(path, max_interval_ms=500).error_count, 0)


if __name__ == "__main__":
    unittest.main()
