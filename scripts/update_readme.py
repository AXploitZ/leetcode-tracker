#!/usr/bin/env python3
"""
update_readme.py

Scans all solution files in the repo, extracts metadata from their header
comments, and rewrites the README's auto-generated sections in place.

Only the content between the sentinel comments is replaced — your hand-written
sections (intro, structure description, how-to-add, etc.) are untouched.

Sentinels in README.md:
    <!-- BEGIN_SOLUTIONS_TABLE -->   ...   <!-- END_SOLUTIONS_TABLE -->
    <!-- BEGIN_TOPICS_TABLE -->      ...   <!-- END_TOPICS_TABLE -->
    <!-- BEGIN_BADGE:problems -->    ...   <!-- END_BADGE:problems -->
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent

# Topics in the order they should appear in the README
TOPIC_ORDER = [
    "arrays-hashing",
    "two-pointers",
    "sliding-window",
    "stack",
    "binary-search",
    "linked-list",
    "trees",
    "tries",
    "heap-priority-queue",
    "backtracking",
    "graphs",
    "dynamic-programming",
    "greedy",
    "intervals",
    "math-geometry",
    "bit-manipulation",
]

TOPIC_DISPLAY = {
    "arrays-hashing":      "Arrays & Hashing",
    "two-pointers":        "Two Pointers",
    "sliding-window":      "Sliding Window",
    "stack":               "Stack",
    "binary-search":       "Binary Search",
    "linked-list":         "Linked List",
    "trees":               "Trees",
    "tries":               "Tries",
    "heap-priority-queue": "Heap / Priority Queue",
    "backtracking":        "Backtracking",
    "graphs":              "Graphs",
    "dynamic-programming": "Dynamic Programming",
    "greedy":              "Greedy",
    "intervals":           "Intervals",
    "math-geometry":       "Math & Geometry",
    "bit-manipulation":    "Bit Manipulation",
}

DIFFICULTY_ORDER = ["easy", "medium", "hard"]

LANG_EXT = {
    ".py":   "Python",
    ".java": "Java",
    ".cpp":  "C++",
    ".ts":   "TypeScript",
    ".js":   "JavaScript",
    ".go":   "Go",
    ".rs":   "Rust",
    ".rb":   "Ruby",
    ".kt":   "Kotlin",
    ".cs":   "C#",
    ".swift":"Swift",
}

LANG_BADGE = {
    "Python":     "🐍",
    "Java":       "☕",
    "C++":        "⚙️",
    "TypeScript": "🟦",
    "JavaScript": "🟨",
    "Go":         "🐹",
    "Rust":       "🦀",
    "Ruby":       "💎",
    "Kotlin":     "🎯",
    "C#":         "🔷",
    "Swift":      "🦅",
}

DIFFICULTY_EMOJI = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}

# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Solution:
    number:     str          # e.g. "0001"
    title:      str          # e.g. "Two Sum"
    link:       str          # e.g. "https://leetcode.com/problems/two-sum/"
    topic:      str          # folder name, e.g. "arrays-hashing"
    difficulty: str          # "easy" | "medium" | "hard"
    slug:       str          # e.g. "two-sum"
    langs:      dict[str, Path] = field(default_factory=dict)  # lang -> path
    notes:      str = ""

# ── Parsing ───────────────────────────────────────────────────────────────────

_PATTERNS = {
    "number":     re.compile(r"(?:Number|#)\s*[:\-]?\s*(\d{3,4})", re.I),
    "title":      re.compile(r"Problem\s*[:\-]\s*(.+)", re.I),
    "link":       re.compile(r"Link\s*[:\-]\s*(https?://\S+)", re.I),
    "difficulty": re.compile(r"Difficulty\s*[:\-]\s*(Easy|Medium|Hard)", re.I),
    "notes":      re.compile(r"Approach\s*[:\-]\s*(.+)", re.I),
}


def parse_header(path: Path) -> dict[str, str]:
    """Read the first 40 lines of a file and extract metadata."""
    meta: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:40]
        text = "\n".join(lines)
        for key, pat in _PATTERNS.items():
            m = pat.search(text)
            if m:
                meta[key] = m.group(1).strip().rstrip(".")
    except Exception:
        pass
    return meta


def slug_from_path(path: Path) -> str:
    """Extract slug from filename like 0001-two-sum.py → two-sum."""
    stem = path.stem  # "0001-two-sum"
    parts = stem.split("-", 1)
    return parts[1] if len(parts) == 2 else stem


def scan_solutions() -> list[Solution]:
    """Walk the repo and collect all solutions, grouped by problem number.

    Flat structure: each topic folder contains solution files directly,
    with no difficulty subdirectories. Difficulty is read from the file header.
    """
    by_number: dict[str, Solution] = {}

    for topic in TOPIC_ORDER:
        topic_dir = REPO_ROOT / topic
        if not topic_dir.is_dir():
            continue

        for fpath in sorted(topic_dir.iterdir()):
            ext = fpath.suffix.lower()
            if ext not in LANG_EXT or fpath.name.startswith("."):
                continue

            lang = LANG_EXT[ext]
            meta = parse_header(fpath)

            # Derive number from filename if not in header
            num_match = re.match(r"^(\d{3,4})", fpath.stem)
            number = meta.get("number", "")
            if not number and num_match:
                number = num_match.group(1).zfill(4)
            if not number:
                continue  # skip files without a number

            number = number.zfill(4)

            # Difficulty comes from header; fall back to "unknown"
            difficulty = meta.get("difficulty", "unknown").lower()

            if number not in by_number:
                slug = slug_from_path(fpath)
                lc_link = f"https://leetcode.com/problems/{slug}/"
                by_number[number] = Solution(
                    number=number,
                    title=meta.get("title", slug.replace("-", " ").title()),
                    link=meta.get("link", lc_link),
                    topic=topic,
                    difficulty=difficulty,
                    slug=slug,
                    notes=meta.get("notes", ""),
                )

            # Record this language solution (relative path for the link)
            rel = fpath.relative_to(REPO_ROOT)
            by_number[number].langs[lang] = rel

    return sorted(by_number.values(), key=lambda s: s.number)


# ── Table builders ────────────────────────────────────────────────────────────

def _lang_cell(sol: Solution, lang: str) -> str:
    if lang in sol.langs:
        path = sol.langs[lang]
        badge = LANG_BADGE.get(lang, "✅")
        return f"[{badge}]({path})"
    return ""


def build_solutions_table(solutions: list[Solution]) -> str:
    # Collect all languages that actually appear in the repo
    all_langs = []
    for lang in LANG_EXT.values():
        if any(lang in sol.langs for sol in solutions):
            all_langs.append(lang)

    header_cols = " | ".join(all_langs)
    sep_cols    = " | ".join(["---"] * len(all_langs))

    lines = [
        f"| # | Problem | Difficulty | Topic | {header_cols} | Notes |",
        f"|---|---------|------------|-------|{sep_cols}|-------|",
    ]

    for sol in solutions:
        diff_icon = DIFFICULTY_EMOJI.get(sol.difficulty, "")
        lang_cells = " | ".join(_lang_cell(sol, lang) for lang in all_langs)
        topic_label = TOPIC_DISPLAY.get(sol.topic, sol.topic)
        notes = sol.notes[:60] + "…" if len(sol.notes) > 60 else sol.notes
        lines.append(
            f"| {sol.number} | [{sol.title}]({sol.link}) "
            f"| {diff_icon} {sol.difficulty.capitalize()} "
            f"| {topic_label} | {lang_cells} | {notes} |"
        )

    return "\n".join(lines)


def build_topics_table(solutions: list[Solution]) -> str:
    counts: dict[str, dict[str, int]] = {
        t: {"easy": 0, "medium": 0, "hard": 0} for t in TOPIC_ORDER
    }
    for sol in solutions:
        if sol.topic in counts:
            counts[sol.topic][sol.difficulty] += 1

    lines = [
        "| Topic | Easy | Medium | Hard | Total |",
        "|-------|------|--------|------|-------|",
    ]
    for topic in TOPIC_ORDER:
        c = counts[topic]
        total = sum(c.values())
        display = TOPIC_DISPLAY.get(topic, topic)
        lines.append(
            f"| [{display}](./{topic}/) | {c['easy']} | {c['medium']} | {c['hard']} | {total} |"
        )

    return "\n".join(lines)


def build_problems_badge(solutions: list[Solution]) -> str:
    count = len(solutions)
    return (
        f"![Problems Solved](https://img.shields.io/badge/"
        f"problems_solved-{count}-blue)"
    )


# ── README rewriter ───────────────────────────────────────────────────────────

def replace_section(content: str, begin: str, end: str, new_body: str) -> str:
    """Replace everything between sentinel comments (inclusive)."""
    pattern = re.compile(
        rf"({re.escape(begin)}\n).*?(\n{re.escape(end)})",
        re.DOTALL,
    )
    replacement = rf"\g<1>{new_body}\g<2>"
    updated, n = pattern.subn(replacement, content)
    if n == 0:
        print(f"  ⚠️  Sentinel not found: {begin!r} — skipping section.")
    return updated


def update_readme(solutions: list[Solution]) -> bool:
    """
    Rewrite README.md in place. Returns True if the file was changed.
    """
    readme_path = REPO_ROOT / "README.md"
    if not readme_path.exists():
        print("ERROR: README.md not found at repo root.", file=sys.stderr)
        sys.exit(1)

    original = readme_path.read_text(encoding="utf-8")
    content  = original

    content = replace_section(
        content,
        "<!-- BEGIN_SOLUTIONS_TABLE -->",
        "<!-- END_SOLUTIONS_TABLE -->",
        build_solutions_table(solutions),
    )
    content = replace_section(
        content,
        "<!-- BEGIN_TOPICS_TABLE -->",
        "<!-- END_TOPICS_TABLE -->",
        build_topics_table(solutions),
    )
    content = replace_section(
        content,
        "<!-- BEGIN_BADGE:problems -->",
        "<!-- END_BADGE:problems -->",
        build_problems_badge(solutions),
    )

    if content == original:
        return False

    readme_path.write_text(content, encoding="utf-8")
    return True


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("🔍 Scanning solutions…")
    solutions = scan_solutions()
    print(f"   Found {len(solutions)} unique problems.")

    print("✏️  Updating README.md…")
    changed = update_readme(solutions)

    if changed:
        print("✅  README.md updated.")
    else:
        print("✅  README.md already up to date — nothing to commit.")


if __name__ == "__main__":
    main()
