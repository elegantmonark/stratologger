#!/usr/bin/env python3
"""Validate payload CSV structure, sequence, timestamps, and checksums.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import sys


EXPECTED_HEADER = [
    "PACKET_ID",
    "TIMESTAMP_MS",
    "TEMP_C",
    "HUMIDITY_PCT",
    "PRESSURE_HPA",
    "ALTITUDE_M",
    "ACCEL_X_MS2",
    "ACCEL_Y_MS2",
    "ACCEL_Z_MS2",
    "GYRO_X_RADS",
    "GYRO_Y_RADS",
    "GYRO_Z_RADS",
    "CHECKSUM_HEX",
]
SCALES = (100.0, 100.0, 100.0, 100.0, 1000.0, 1000.0, 1000.0,
          10000.0, 10000.0, 10000.0)


def lround_away_from_zero(value: float) -> int:
    """Match C/C++ lroundf rather than Python's ties-to-even round()."""
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def scaled_u32(value: float, scale: float) -> int:
    if not math.isfinite(value):
        return 0x80000000
    return lround_away_from_zero(value * scale) & 0xFFFFFFFF


def checksum_for(packet_id: int, timestamp_ms: int, values: list[float]) -> int:
    checksum = (packet_id ^ timestamp_ms) & 0xFFFFFFFF
    for value, scale in zip(values, SCALES, strict=True):
        checksum ^= scaled_u32(value, scale)
    return checksum & 0xFFFFFFFF


def validate(path: Path, *, verbose: bool = True) -> tuple[int, int]:
    errors = 0
    rows_seen = 0
    previous_packet: int | None = None
    previous_timestamp: int | None = None

    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        errors += 1
        if verbose:
            print("ERROR: file does not end with a newline (possible truncated row)")

    with path.open("r", newline="", encoding="ascii") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            if verbose:
                print("ERROR: empty file")
            return 1, 0

        if header != EXPECTED_HEADER:
            errors += 1
            if verbose:
                print("ERROR: CSV header does not match the telemetry schema")

        for line_number, row in enumerate(reader, start=2):
            if not row:
                continue
            rows_seen += 1
            if len(row) != len(EXPECTED_HEADER):
                errors += 1
                if verbose:
                    print(f"ERROR line {line_number}: expected 13 fields, got {len(row)}")
                continue
            try:
                packet_id = int(row[0])
                timestamp = int(row[1])
                values = [float(item) for item in row[2:12]]
                recorded = int(row[12], 16)
            except ValueError as exc:
                errors += 1
                if verbose:
                    print(f"ERROR line {line_number}: invalid value ({exc})")
                continue

            expected = checksum_for(packet_id, timestamp, values)
            if recorded != expected:
                errors += 1
                if verbose:
                    print(
                        f"ERROR line {line_number}: checksum {recorded:08X}, "
                        f"expected {expected:08X}"
                    )

            if previous_packet is not None and packet_id != previous_packet + 1:
                errors += 1
                relation = "duplicate/backwards" if packet_id <= previous_packet else "gap"
                if verbose:
                    print(
                        f"ERROR line {line_number}: packet {relation}: "
                        f"{previous_packet} -> {packet_id}"
                    )
            if previous_timestamp is not None and timestamp < previous_timestamp:
                errors += 1
                if verbose:
                    print(
                        f"ERROR line {line_number}: timestamp moved backwards: "
                        f"{previous_timestamp} -> {timestamp}"
                    )
            previous_packet = packet_id
            previous_timestamp = timestamp

    if verbose:
        status = "PASS" if errors == 0 else "FAIL"
        print(f"{status}: {rows_seen} data rows, {errors} error(s)")
    return errors, rows_seen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    if not args.csv_file.is_file():
        parser.error(f"not a file: {args.csv_file}")
    errors, _ = validate(args.csv_file)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

