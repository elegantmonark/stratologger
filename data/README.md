# Telemetry data

No hardware capture is published at this revision.

`format-example.csv` is a short synthetic file used to demonstrate the schema and test
the validator. It must not be cited as sensor output. A real capture should be stored in
a revision-specific directory together with a completed copy of
`run-metadata-template.yaml`.

Before publishing a run:

- validate it with `python tools/validate_log.py <file>`;
- record the firmware revision and wiring revision;
- record the test conditions and reference instruments;
- preserve the original file without manual correction; and
- check the metadata for personal or location information that is not required to
  reproduce the result.

