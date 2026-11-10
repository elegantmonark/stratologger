# PCB

**Fabrication is on hold:** the 27 October audit identified an ESP32 socket-map
mismatch with the common 30-pin DOIT module. Do not order the current SL-1 ZIP.
See [the review](SL-1/review/PCB_AUDIT.md).

The PCB directory contains the custom motherboard that replaces the proposed
breadboard and perfboard construction. Each numbered SL version remains separate so
that a manufacturing release can be traced back to the reviewed source files.

[`SL-1/`](SL-1/README.md) contains the routed 90 by 70 mm motherboard and its
fabrication package. The design passes KiCad DRC, but the exact plug-in modules still
require a 1:1 physical fit check before the board is ordered.
