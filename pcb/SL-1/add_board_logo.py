"""Add Stratologger's native silkscreen logo without rebuilding copper routing.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing. Existing board bytes are backed up before the first change.
"""

import shutil
from pathlib import Path

import pcbnew

from generate_stratologger_pcb import add_stratologger_logo


def main():
    root = Path(__file__).resolve().parent
    path = root / "Stratologger_SL1.kicad_pcb"
    board = pcbnew.LoadBoard(str(path))
    for item in board.GetDrawings():
        if (isinstance(item, pcbnew.PCB_SHAPE)
                and item.GetShape() == pcbnew.SHAPE_T_CIRCLE
                and item.GetLayer() == pcbnew.F_SilkS
                and item.GetCenter() == pcbnew.VECTOR2I(pcbnew.FromMM(87.5), pcbnew.FromMM(71.0))):
            print("Stratologger logo already present; no change.")
            return
    backup = root / "review" / "original-before-logo.kicad_pcb"
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(path, backup)
    add_stratologger_logo(board)
    pcbnew.SaveBoard(str(path), board)
    print("Added native front-silkscreen logo. Copper routing unchanged.")


if __name__ == "__main__":
    main()
