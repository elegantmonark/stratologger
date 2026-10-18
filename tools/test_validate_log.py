"""CSV validator tests.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing
"""

import csv
from pathlib import Path
import tempfile
import unittest

from validate_log import EXPECTED_HEADER, checksum_for, validate


class ValidatorTests(unittest.TestCase):
    def make_log(self, corrupt_checksum: bool = False) -> Path:
        temporary = tempfile.NamedTemporaryFile(
            mode="w", encoding="ascii", newline="", suffix=".CSV", delete=False
        )
        packet_id = 1
        timestamp = 500
        values = [22.25, 45.5, 1012.75, 4.25, -0.125, 0.25, 9.81,
                  -0.0125, 0.025, 0.0]
        checksum = checksum_for(packet_id, timestamp, values)
        if corrupt_checksum:
            checksum ^= 1
        with temporary:
            writer = csv.writer(temporary, lineterminator="\n")
            writer.writerow(EXPECTED_HEADER)
            writer.writerow([packet_id, timestamp, *values, f"{checksum:08X}"])
        return Path(temporary.name)

    def test_valid_log_passes(self):
        path = self.make_log()
        self.addCleanup(path.unlink)
        self.assertEqual(validate(path, verbose=False), (0, 1))

    def test_corrupt_checksum_fails(self):
        path = self.make_log(corrupt_checksum=True)
        self.addCleanup(path.unlink)
        errors, rows = validate(path, verbose=False)
        self.assertEqual(rows, 1)
        self.assertGreater(errors, 0)


if __name__ == "__main__":
    unittest.main()

