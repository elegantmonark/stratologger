"""Inspect telemetry integrity, continuity, timing and sensor health.

Author: Trishan Biswas
Project started: February 2026
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass, field, asdict
import json
import math
from pathlib import Path
import re

from validate_log import EXPECTED_HEADER, checksum_for

MASK = 0xFFFFFFFF


@dataclass
class LogReport:
    rows: int = 0
    errors: Counter = field(default_factory=Counter)
    examples: list[str] = field(default_factory=list)
    timestamp_rollovers: int = 0
    packet_rollovers: int = 0
    max_interval_ms: int = 0
    elapsed_ms: int = 0

    def flag(self, kind: str, line: int, detail: str) -> None:
        self.errors[kind] += 1
        if len(self.examples) < 20:
            self.examples.append(f"line {line}: {kind}: {detail}")

    @property
    def error_count(self) -> int:
        return sum(self.errors.values())

    def to_dict(self) -> dict:
        result = asdict(self)
        result["errors"] = dict(self.errors)
        result["error_count"] = self.error_count
        result["status"] = "FAIL" if self.error_count else "PASS"
        return result


def uint32(text: str) -> int:
    if not re.fullmatch(r"[0-9]+", text) or int(text) > MASK:
        raise ValueError("expected an unsigned 32 bit integer")
    return int(text)


def audit(path: Path, *, max_interval_ms: int = 750) -> LogReport:
    report = LogReport()
    previous_packet = previous_timestamp = None
    # Only retain totals and a few examples, even for a long log.
    with path.open("rb") as raw:
        raw.seek(0, 2)
        if raw.tell():
            raw.seek(-1, 2)
            if raw.read(1) != b"\n":
                report.flag("truncated", 0, "file does not end with a newline")
    line_number = 1
    try:
        with path.open(newline="", encoding="ascii") as handle:
            reader = csv.reader(handle, strict=True)
            if next(reader, None) != EXPECTED_HEADER:
                report.flag("header", 1, "expected the telemetry CSV header")
            for row in reader:
                line_number = reader.line_num
                if not row:
                    continue
                report.rows += 1
                if len(row) != 13:
                    report.flag("malformed", line_number, f"expected 13 fields, got {len(row)}")
                    continue
                try:
                    packet = uint32(row[0])
                    timestamp = uint32(row[1])
                    values = [float(item) for item in row[2:12]]
                    if not re.fullmatch(r"[0-9a-fA-F]{8}", row[12]):
                        raise ValueError("checksum must contain eight hexadecimal digits")
                    expected = checksum_for(packet, timestamp, values)
                    if int(row[12], 16) != expected:
                        report.flag("checksum", line_number, f"expected {expected:08X}, got {row[12]}")
                except (ValueError, OverflowError) as exc:
                    report.flag("malformed", line_number, str(exc))
                    continue
                if not all(math.isfinite(value) for value in values):
                    report.flag("nonfinite", line_number, "sensor field contains NaN or infinity")
                if math.isfinite(values[1]) and not 0 <= values[1] <= 100:
                    report.flag("range", line_number, "humidity is outside 0 to 100 percent")
                if math.isfinite(values[2]) and values[2] <= 0:
                    report.flag("range", line_number, "pressure must be positive")
                if previous_packet is not None:
                    step = (packet - previous_packet) & MASK
                    if step != 1:
                        kind = "packet_gap" if 1 < step < 2**31 else "packet_order"
                        report.flag(kind, line_number, f"{previous_packet} to {packet}")
                    elif packet < previous_packet:
                        report.packet_rollovers += 1
                    delta = (timestamp - previous_timestamp) & MASK
                    if delta == 0 or delta >= 2**31:
                        report.flag("timestamp_order", line_number, f"{previous_timestamp} to {timestamp}")
                    else:
                        report.elapsed_ms += delta
                        report.max_interval_ms = max(report.max_interval_ms, delta)
                        if timestamp < previous_timestamp:
                            report.timestamp_rollovers += 1
                        if delta > max_interval_ms:
                            report.flag("timing_gap", line_number, f"{delta} ms exceeds {max_interval_ms} ms")
                previous_packet, previous_timestamp = packet, timestamp
    except (UnicodeError, csv.Error) as exc:
        report.flag("malformed", line_number, str(exc))
    if report.rows == 0:
        report.flag("empty", 0, "no data rows")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--json", type=Path, help="write a machine readable report")
    parser.add_argument("--max-interval-ms", type=int, default=750,
                        help="largest accepted interval for the 500 ms mission stream")
    args = parser.parse_args()
    if not args.csv_file.is_file() or args.max_interval_ms <= 0:
        parser.error("provide a readable CSV and a positive interval limit")
    report = audit(args.csv_file, max_interval_ms=args.max_interval_ms)
    print(json.dumps(report.to_dict(), indent=2))
    if args.json:
        args.json.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return int(report.error_count > 0)


if __name__ == "__main__":
    raise SystemExit(main())
