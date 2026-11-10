"""Run repeatable telemetry fault cases and export their results.

Author: Trishan Biswas
Project started: February 2026
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import platform
import tempfile
import time
from datetime import datetime, timezone

from log_audit import audit, MASK
from validate_log import EXPECTED_HEADER, checksum_for


def refresh(row: list[str]) -> None:
    row[-1] = f"{checksum_for(int(row[0]), int(row[1]), [float(v) for v in row[2:12]]):08X}"


def encode(rows: list[list[str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(EXPECTED_HEADER)
    writer.writerows(rows)
    return stream.getvalue().encode("ascii")


def build_cases() -> list[tuple[str, bytes, set[str]]]:
    base = []
    for i in range(600):
        row = [str(i + 1), str((i + 1) * 500), "20.00", "45.50", "1012.75",
               "4.00", "-0.125", "0.250", "9.810", "-0.0125", "0.0250", "0.0000", ""]
        refresh(row)
        base.append(row)
    cases = [("clean_5_minutes", encode(base), set())]
    rows = copy.deepcopy(base)
    rows[100][2] = "20.01"
    cases.append(("changed_measurement", encode(rows), {"checksum"}))
    rows = copy.deepcopy(base)
    del rows[100]
    cases.append(("dropped_packet", encode(rows), {"packet_gap", "timing_gap"}))
    rows = copy.deepcopy(base)
    rows.insert(100, rows[99].copy())
    cases.append(("duplicate_packet", encode(rows), {"packet_order", "timestamp_order"}))
    rows = copy.deepcopy(base)
    rows[100], rows[101] = rows[101], rows[100]
    cases.append(("reordered_packets", encode(rows), {"packet_order", "timestamp_order"}))
    rows = copy.deepcopy(base)
    rows[100][1] = rows[99][1]
    refresh(rows[100])
    cases.append(("frozen_clock", encode(rows), {"timestamp_order"}))
    rows = copy.deepcopy(base)
    for row in rows[100:]:
        row[1] = str(int(row[1]) + 5000)
        refresh(row)
    cases.append(("acquisition_stall", encode(rows), {"timing_gap"}))
    cases.append(("partial_final_row", encode(base)[:-16], {"truncated", "malformed"}))
    cases.append(("missing_final_newline", encode(base)[:-1], {"truncated"}))
    rows = copy.deepcopy(base)
    rows[100][2] = "nan"
    refresh(rows[100])
    cases.append(("sensor_nan_valid_checksum", encode(rows), {"nonfinite"}))
    rows = copy.deepcopy(base)
    rows[100][3] = "145.50"
    refresh(rows[100])
    cases.append(("humidity_out_of_range", encode(rows), {"range"}))
    rows = copy.deepcopy(base)
    rows[100][0] = str(2**32)
    cases.append(("packet_integer_overflow", encode(rows), {"malformed"}))
    rows = copy.deepcopy(base)
    rows[100][2] = "1e309"
    cases.append(("infinite_reading", encode(rows), {"nonfinite"}))
    rows = copy.deepcopy(base)
    rows[100][2] = "1e30"
    cases.append(("scaled_integer_overflow", encode(rows), {"malformed"}))
    cases.append(("header_only", encode([]), {"empty"}))
    cases.append(("wrong_header", encode(base).replace(b"PACKET_ID", b"SEQ", 1), {"header"}))
    cases.append(("invalid_encoding", encode(base) + b"\xff\n", {"malformed"}))
    rows = copy.deepcopy(base)
    for i, row in enumerate(rows):
        row[0] = str((MASK - 10 + i) & MASK)
        row[1] = str((MASK - 1000 + i * 500) & MASK)
        refresh(row)
    cases.append(("counter_rollovers", encode(rows), set()))
    # Flipping the same bit in two scaled fields cancels in an XOR checksum.
    rows = copy.deepcopy(base)
    rows[100][2] = "20.01"
    rows[100][5] = "4.01"
    cases.append(("xor_cancellation", encode(rows), set()))
    return cases


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def run(current: Path, legacy: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="stratologger_campaign_") as folder:
        for name, raw, required in build_cases():
            path = Path(folder) / f"{name}.csv"
            path.write_bytes(raw)
            report = audit(path)
            passed = required.issubset(report.errors) if required else report.error_count == 0
            if name == "counter_rollovers":
                passed = passed and report.timestamp_rollovers == report.packet_rollovers == 1
            results.append({"case": name, "expectation_met": passed,
                            "required_errors": sorted(required), **report.to_dict()})
    native = {}
    for name, path in (("legacy", legacy), ("current", current)):
        start = time.perf_counter()
        report = audit(path)
        native[name] = {**report.to_dict(), "validation_seconds": time.perf_counter() - start,
                        "input_sha256": digest(path)}
    regression_ok = (native["current"]["rows"] == native["legacy"]["rows"]
                     and native["current"]["rows"] >= 100000
                     and native["current"]["error_count"] == 0
                     and native["legacy"]["errors"].get("checksum", 0) > 0)
    root = Path(__file__).resolve().parents[1]
    sources = ["include/telemetry_types.h", "include/telemetry_csv.h",
               "src/storage/TelemetryLogger.cpp", "tests/telemetry_csv_fixture.cpp",
               "tools/validate_log.py", "tools/log_audit.py", "tools/run_log_campaign.py"]
    summary = {"created_utc": datetime.now(timezone.utc).isoformat(),
               "data_origin": "synthetic host inputs, not a sensor capture",
               "python": platform.python_version(), "platform": platform.system(),
               "source_sha256": {p: digest(root / p) for p in sources},
               "cases": results, "native_serializer": native,
               "all_expectations_met": regression_ok and all(r["expectation_met"] for r in results)}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (output / "fault_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["case", "expectation_met", "rows", "error_count", "categories"])
        for r in results:
            writer.writerow([r["case"], r["expectation_met"], r["rows"], r["error_count"],
                             "; ".join(f"{k}={v}" for k, v in r["errors"].items())])
    plots(summary, output)
    return summary


def plots(summary: dict, output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 8), gridspec_kw={"width_ratios": [1, 2]})
    counts = [summary["native_serializer"][name]["errors"].get("checksum", 0)
              for name in ("legacy", "current")]
    bars = axes[0].bar(["Previous logger", "Revised logger"], counts, color=["#db654e", "#208c83"])
    axes[0].bar_label(bars, padding=4)
    axes[0].set_ylabel("Checksum mismatches in 100,000 synthetic rows")
    axes[0].set_title("Decimal rounding regression")
    cases = summary["cases"]
    names = [r["case"].replace("_", " ") for r in cases]
    values = [r["error_count"] for r in cases]
    axes[1].barh(names, values, color="#376c99")
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Reported errors per test file")
    axes[1].set_title("Controlled fault cases")
    axes[1].set_xticks(range(max(values) + 1))
    fig.suptitle("Stratologger software validation | synthetic inputs", fontsize=15)
    fig.text(0.5, 0.015, "Zero errors are expected for clean data and rollovers. XOR cancellation exposes an undetected corruption case.",
             ha="center", fontsize=10)
    fig.tight_layout(rect=(0, 0.045, 1, 0.96))
    fig.savefig(output / "validation_overview.png", dpi=170)
    fig.savefig(output / "validation_overview.svg")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/log-validation"))
    args = parser.parse_args()
    result = run(args.current, args.legacy, args.output)
    print(f"Cases meeting expectations: {sum(r['expectation_met'] for r in result['cases'])}/{len(result['cases'])}")
    for version, report in result["native_serializer"].items():
        print(f"{version}: {report['rows']} rows, {report['error_count']} errors")
    raise SystemExit(0 if result["all_expectations_met"] else 1)
