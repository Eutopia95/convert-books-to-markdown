#!/usr/bin/env python3
"""Validate a clean Obsidian Markdown book output directory."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote


PROMO_PATTERNS = {
    "piracy disclaimer": re.compile(r"本书仅供个人学习|请购买正版|自负法律后果"),
    "download promotion": re.compile(
        r"z-?library|1lib|电子书下载网站|免费电子书|微信公众号|加小编QQ",
        re.I,
    ),
    "duplicate English TOC": re.compile(r"^Table of Contents\s*$", re.M),
}


def canonical_copy_name(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"(?:\s*\([2-9]\d*\)|\s+copy|\s+-\s+副本)$", "", stem, flags=re.I)
    return stem + path.suffix.lower()


def resolve_link(md_file: Path, target: str) -> Path | None:
    target = target.strip().strip("<>")
    if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
        return None
    # Split a real Markdown fragment before URL-decoding. An encoded `%23`
    # belongs to the filename and must not be mistaken for an anchor marker.
    target = target.split("#", 1)[0]
    if not target:
        return None
    target = unquote(target)
    return (md_file.parent / target).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--settle-seconds", type=float, default=0)
    args = parser.parse_args()

    if args.settle_seconds:
        time.sleep(args.settle_seconds)

    root = args.output.resolve()
    if not root.is_dir():
        print(f"ERROR: output folder does not exist: {root}")
        return 2

    files = sorted(path for path in root.rglob("*") if path.is_file())
    markdown = [path for path in files if path.suffix.lower() == ".md"]
    errors: list[str] = []
    warnings: list[str] = []
    if not markdown:
        errors.append("no Markdown files found")

    by_parent_and_canonical: dict[tuple[Path, str], list[Path]] = defaultdict(list)
    for path in files:
        by_parent_and_canonical[(path.parent, canonical_copy_name(path))].append(path)
    for paths in by_parent_and_canonical.values():
        if len(paths) > 1:
            errors.append("copy-like duplicate names: " + ", ".join(str(p.relative_to(root)) for p in paths))
    # Finder commonly creates `Title 2.ext`, but a bare numeric suffix can also
    # be semantic (`Chapter 20.md`). Treat it as a copy only when the unsuffixed
    # sibling actually exists.
    file_set = set(files)
    reported_numeric_pairs: set[tuple[Path, Path]] = set()
    for path in files:
        match = re.fullmatch(r"(.+?)\s+([2-9]\d*)", path.stem)
        if not match:
            continue
        original = path.with_name(match.group(1) + path.suffix)
        if original in file_set:
            pair = (original, path)
            if pair not in reported_numeric_pairs:
                reported_numeric_pairs.add(pair)
                errors.append(
                    "copy-like duplicate names: "
                    + ", ".join(str(p.relative_to(root)) for p in pair)
                )

    exact: dict[str, list[Path]] = defaultdict(list)
    normalized: dict[str, list[Path]] = defaultdict(list)
    for path in markdown:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        exact[hashlib.sha256(raw).hexdigest()].append(path)
        compact = re.sub(r"\s+", "", text)
        normalized[hashlib.sha256(compact.encode()).hexdigest()].append(path)

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines or not lines[0].startswith("# "):
            warnings.append(f"missing opening H1: {path.relative_to(root)}")
        elif len(lines) > 1:
            title = re.sub(r"^#\s+", "", lines[0]).strip()
            second = re.sub(r"^#+\s+", "", lines[1]).strip()
            if title and title == second:
                errors.append(f"repeated opening title: {path.relative_to(root)}")

        references = re.findall(r"\[\^([^\]]+)\](?!:)", text)
        definitions = re.findall(r"^\[\^([^\]]+)\]:", text, flags=re.M)
        missing_defs = sorted(set(references) - set(definitions))
        unused_defs = sorted(set(definitions) - set(references))
        if missing_defs:
            errors.append(f"missing footnote definitions in {path.relative_to(root)}: {missing_defs}")
        if unused_defs:
            warnings.append(f"unused footnote definitions in {path.relative_to(root)}: {unused_defs}")

        links: list[str] = []
        links.extend(re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text))
        links.extend(re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", text, flags=re.I))
        links.extend(re.findall(r"!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text))
        for target in links:
            resolved = resolve_link(path, target)
            if resolved is not None and not resolved.exists():
                errors.append(f"broken local link in {path.relative_to(root)}: {target}")

        for label, pattern in PROMO_PATTERNS.items():
            if pattern.search(text):
                warnings.append(f"possible {label} in {path.relative_to(root)}")

    for groups, label in ((exact, "exact"), (normalized, "whitespace-normalized")):
        for paths in groups.values():
            if len(paths) > 1:
                errors.append(
                    f"{label} duplicate Markdown content: "
                    + ", ".join(str(path.relative_to(root)) for path in paths)
                )

    print(f"root={root}")
    print(f"files={len(files)} markdown={len(markdown)} assets={len(files) - len(markdown)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"result={'FAIL' if errors else 'PASS'} errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
