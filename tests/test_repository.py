"""Repository integrity checks.

Author: Trishan Biswas
Project started: February 2026
Status: Ongoing
"""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as element_tree
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".pio", ".pio-core", ".platformio-core", ".platformio-tool"}


class RepositoryTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = (
            "README.md",
            "LICENSE",
            "NOTICE",
            "CITATION.cff",
            "platformio.ini",
            "electrical/bom.csv",
            "electrical/netlist.csv",
            "electrical/wiring-diagram.svg",
            "mechanical/enclosure.scad",
            "data/format-example.csv",
            "docs/validation.md",
        )
        for relative_path in required:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_local_markdown_links_exist(self) -> None:
        pattern = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
        missing: list[str] = []
        for markdown in ROOT.rglob("*.md"):
            if any(part in IGNORED_PARTS for part in markdown.parts):
                continue
            for target in pattern.findall(markdown.read_text(encoding="utf-8")):
                target = target.strip().split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (markdown.parent / target).resolve().exists():
                    missing.append(f"{markdown.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])

    def test_wiring_diagram_is_valid_xml(self) -> None:
        element_tree.parse(ROOT / "electrical" / "wiring-diagram.svg")

    def test_code_headers_identify_project_author(self) -> None:
        source_files = [
            *ROOT.glob("include/*.h"),
            *ROOT.glob("src/**/*.h"),
            *ROOT.glob("src/**/*.cpp"),
            *ROOT.glob("tools/*.py"),
            ROOT / "mechanical" / "enclosure.scad",
        ]
        for source in source_files:
            text = source.read_text(encoding="utf-8")[:500]
            self.assertIn("Trishan Biswas", text, str(source.relative_to(ROOT)))
            self.assertIn("February 2026", text, str(source.relative_to(ROOT)))

    def test_repository_text_has_no_local_absolute_paths(self) -> None:
        forbidden = ("C:\\Users\\", "/Users/", "/home/")
        matches: list[str] = []
        text_suffixes = {".cff", ".cpp", ".csv", ".h", ".ini", ".md", ".py", ".scad", ".svg", ".yaml"}
        for path in ROOT.rglob("*"):
            if (
                not path.is_file()
                or path.suffix.lower() not in text_suffixes
                or any(part in IGNORED_PARTS for part in path.parts)
                or path.resolve() == Path(__file__).resolve()
            ):
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                if marker in text:
                    matches.append(f"{path.relative_to(ROOT)}: {marker}")
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()

