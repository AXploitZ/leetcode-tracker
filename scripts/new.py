#!/usr/bin/env python3
"""
new.py -- scaffold a new LeetCode solution file

Usage:
    python scripts/new.py <problem-number> [--lang py] [--lang java]

Examples:
    python scripts/new.py 121
    python scripts/new.py 121 --lang java
    python scripts/new.py 121 --lang py --lang java

What it does:
    1. Fetches problem title, difficulty, slug, starter code, and examples
       from the LeetCode GraphQL API (no login required for public problems)
    2. Parses example inputs + outputs from the problem HTML to generate
       real test cases (falls back to TODO stubs if parsing is uncertain)
    3. Asks you to choose the topic folder interactively
    4. Creates solution file(s) with header, starter code, and tests pre-filled
    5. Tests are skipped by default -- remove the skip decorator once your
       solution is correct and you want CI to verify it
    6. Opens the file in $EDITOR if set
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

# ---- Config ------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent

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

SUPPORTED_LANGS  = ["py", "java", "cpp", "ts", "go", "rs"]
DIFFICULTY_EMOJI = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}

# ---- LeetCode API ------------------------------------------------------------

_GRAPHQL_URL = "https://leetcode.com/graphql"

_PROBLEM_QUERY = """
query problemData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId
    title
    titleSlug
    difficulty
    content
    codeSnippets { lang langSlug code }
    exampleTestcaseList
  }
}
"""

_SLUG_QUERY = """
query problemByNumber($skip: Int!, $limit: Int!) {
  problemsetQuestionList(categorySlug: "" limit: $limit skip: $skip filters: {}) {
    questions { frontendQuestionId titleSlug }
  }
}
"""

_LC_LANG_MAP = {
    "python3":    "py",
    "java":       "java",
    "cpp":        "cpp",
    "typescript": "ts",
    "golang":     "go",
    "rust":       "rs",
}


# A fixed CSRF token value is fine for read-only public queries.
# LeetCode requires it to be present and consistent between the header
# and the cookie -- the actual value doesn't matter for unauthenticated requests.
_CSRF_TOKEN = "leetcode-new-py"


def _graphql(query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        _GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Referer":        "https://leetcode.com/problems/",
            "Origin":         "https://leetcode.com",
            "x-csrftoken":    _CSRF_TOKEN,
            "Cookie":         f"csrftoken={_CSRF_TOKEN}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        raise RuntimeError(
            f"HTTP {e.code} from LeetCode API.\n"
            f"Response: {body}\n"
            "If this keeps happening, LeetCode may have changed their API. "
            "Check https://github.com/nicksyou/leetcode-api for updates."
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}") from e


def fetch_slug_for_number(number: int) -> str | None:
    """
    Resolve a problem number to its title slug.

    Strategy:
    1. Try the unofficial REST API first -- it returns a stable JSON list
       and is less rate-limited than GraphQL for this kind of lookup.
    2. Fall back to the GraphQL problemsetQuestionList query.
    """
    # Strategy 1: REST problems list (paginated, 100 per page)
    page  = (number - 1) // 100
    offset = page * 100
    rest_url = (
        f"https://leetcode.com/api/problems/all/"
    )
    try:
        req = urllib.request.Request(
            rest_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Referer": "https://leetcode.com",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for stat_pair in data.get("stat_status_pairs", []):
            stat = stat_pair.get("stat", {})
            if str(stat.get("frontend_question_id")) == str(number):
                return stat["question__title_slug"]
    except Exception:
        pass  # fall through to GraphQL

    # Strategy 2: GraphQL problemsetQuestionList
    try:
        skip = max(0, number - 50)
        data = _graphql(_SLUG_QUERY, {"skip": skip, "limit": 100})
        questions = (
            data.get("data", {})
                .get("problemsetQuestionList", {})
                .get("questions", [])
        )
        for q in questions:
            if str(q.get("frontendQuestionId")) == str(number):
                return q["titleSlug"]
    except Exception:
        pass

    return None


def fetch_problem(number: int) -> dict:
    """Return problem metadata from LeetCode. Raises RuntimeError on failure."""
    print(f"  Fetching problem #{number} from LeetCode...")

    slug = fetch_slug_for_number(number)
    if not slug:
        raise RuntimeError(
            f"Could not find problem #{number} on LeetCode. "
            "Check the number and your internet connection."
        )

    data = _graphql(_PROBLEM_QUERY, {"titleSlug": slug})
    q = data.get("data", {}).get("question")
    if not q:
        raise RuntimeError(f"LeetCode returned no data for slug '{slug}'.")

    snippets: dict[str, str] = {}
    for s in q.get("codeSnippets") or []:
        ext = _LC_LANG_MAP.get(s["langSlug"])
        if ext:
            snippets[ext] = s["code"]

    return {
        "number":         q["questionFrontendId"].zfill(4),
        "title":          q["title"],
        "slug":           q["titleSlug"],
        "difficulty":     q["difficulty"].lower(),
        "snippets":       snippets,
        "content":        q.get("content") or "",
        "example_inputs": q.get("exampleTestcaseList") or [],
    }


# ---- Example parser ----------------------------------------------------------

@dataclass
class Example:
    index:  int
    inputs: list   # raw input lines from exampleTestcaseList
    output: str | None = None   # parsed from HTML; None means parse failed


def _strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()



def _extract_problem_statement(content_html: str) -> tuple[str, str]:
    """
    Parse the LeetCode problem HTML into two clean plain-text strings:
      - statement   : the opening description (before the first Example)
      - constraints : the bullet-point constraints list

    Returns ("", "") on any parse failure -- callers fall back to placeholders.
    """
    if not content_html:
        return "", ""

    try:
        h = re.sub(r"\s+", " ", content_html)

        # Statement: everything before <strong>Example 1
        parts = re.split(r"<strong[^>]*>\s*Example\s*1", h, maxsplit=1)
        raw_stmt = parts[0] if parts else h

        # Convert block-level tags to newlines before stripping tags
        raw_stmt = re.sub(r"</p>|</li>|<br\s*/?>", "\n", raw_stmt, flags=re.I)
        raw_stmt = re.sub(r"<li[^>]*>", "- ", raw_stmt, flags=re.I)
        raw_stmt = re.sub(
            r"<code[^>]*>(.*?)</code>", r"`\1`", raw_stmt, flags=re.I | re.DOTALL
        )
        stmt_text = _strip_tags(raw_stmt)

        # Collapse runs of blank lines; wrap long lines at 72 chars
        stmt_lines: list[str] = []
        prev_blank = False
        for line in stmt_text.splitlines():
            line = line.strip()
            if not line:
                if not prev_blank:
                    stmt_lines.append("")
                prev_blank = True
            else:
                while len(line) > 72:
                    cut = line.rfind(" ", 0, 72)
                    if cut == -1:
                        cut = 72
                    stmt_lines.append(line[:cut])
                    line = line[cut:].lstrip()
                stmt_lines.append(line)
                prev_blank = False
        statement = "\n".join(stmt_lines).strip()

        # Constraints: items in the <ul> that follows "Constraints:"
        constraints = ""
        constr_m = re.search(
            r"Constraints\s*:?\s*</[^>]+>\s*<ul[^>]*>(.*?)</ul>",
            h,
            re.I | re.DOTALL,
        )
        if constr_m:
            raw_c = re.sub(
                r"<code[^>]*>(.*?)</code>", r"`\1`",
                constr_m.group(1),
                flags=re.I | re.DOTALL,
            )
            items = re.findall(r"<li[^>]*>(.*?)</li>", raw_c, re.I | re.DOTALL)
            constraints = "\n".join(
                "- " + _strip_tags(item).strip() for item in items
            )

        return statement, constraints

    except Exception:
        return "", ""



def _parse_outputs(content_html: str) -> list[str]:
    """
    Extract Output values from LeetCode problem HTML.
    Returns one string per example. Conservative: returns [] on any ambiguity.
    """
    outputs: list[str] = []

    # Primary pattern: <strong>Output:</strong> value
    for m in re.finditer(
        r"<strong[^>]*>\s*Output\s*:?\s*</strong>\s*:?\s*(.*?)(?=<(?:strong|p|pre|br|div)|$)",
        content_html,
        re.IGNORECASE | re.DOTALL,
    ):
        val = _strip_tags(m.group(1)).strip().rstrip(",")
        if val:
            outputs.append(val)

    # Fallback: inside <pre> blocks
    if not outputs:
        for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", content_html, re.DOTALL):
            m = re.search(
                r"Output\s*:\s*(.+?)(?=\n[A-Z]|\Z)",
                _strip_tags(pre),
                re.DOTALL,
            )
            if m:
                outputs.append(m.group(1).strip())

    return outputs


def parse_examples(meta: dict) -> list[Example]:
    raw_inputs: list[str] = meta["example_inputs"]
    outputs = _parse_outputs(meta["content"])

    examples = []
    for i, raw in enumerate(raw_inputs):
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        out   = outputs[i] if i < len(outputs) else None
        examples.append(Example(index=i + 1, inputs=lines, output=out))
    return examples


# ---- Signature helpers -------------------------------------------------------

def _py_method_info(snippet: str) -> tuple[str, list[str]]:
    m = re.search(r"def\s+(\w+)\s*\(self(?:,\s*([^)]*))?\)", snippet)
    if not m:
        return "solve", []
    method = m.group(1)
    params_str = m.group(2) or ""
    params = [p.strip().split(":")[0].strip() for p in params_str.split(",") if p.strip()]
    return method, params


def _java_method_info(snippet: str) -> tuple[str, list[str], str]:
    m = re.search(r"public\s+([\w\[\]<>]+)\s+(\w+)\s*\(([^)]*)\)", snippet)
    if not m:
        return "solve", [], "void"
    ret_type   = m.group(1)
    method     = m.group(2)
    params_raw = m.group(3)
    params = [p.strip().split()[-1] for p in params_raw.split(",") if p.strip()]
    return method, params, ret_type


# ---- Test builders -----------------------------------------------------------

def _build_py_tests(meta: dict) -> str:
    snippet          = meta["snippets"].get("py", "")
    method, params   = _py_method_info(snippet)
    examples         = parse_examples(meta)

    def test_block(class_name: str, prefix: str) -> list[str]:
        block = []
        for ex in examples:
            args = ex.inputs[: len(params)]
            call = f"{class_name}().{method}({', '.join(args)})"
            block.append("@pytest.mark.skip(reason='not solved yet')")
            block.append(f"def {prefix}{ex.index}():")
            if ex.output is not None:
                block.append(f"    assert {call} == {ex.output}")
            else:
                block.append(f"    # TODO: assert {call} == <expected>")
            block.append("")
        return block

    lines = [
        "",
        "",
        "# " + "-" * 75,
        "# Tests  (remove @pytest.mark.skip once your solution is correct)",
        "# " + "-" * 75,
        "import pytest",
        "",
    ]
    lines += test_block("Solution", "test_example_")

    lines += [
        "",
        'if __name__ == "__main__":',
        "    pytest.main([__file__, '-v'])",
        "",
    ]
    return "\n".join(lines)


_JBANG_DEPS = (
    "//DEPS org.junit.jupiter:junit-jupiter:5.10.2\n"
    "//DEPS org.junit.platform:junit-platform-console-standalone:1.10.2\n"
)

_JBANG_RUNNER = """\

// JBang entry point -- discovers and runs every *Test class in this file,
// printing a per-test PASS / FAIL / SKIP line similar to `pytest -v`.
class JBangRunner {
    public static void main(String[] args) throws Exception {
        var launcher = org.junit.platform.launcher.core.LauncherFactory.create();
        var request  = org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder
            .request()
            // Selects all test classes in the default (unnamed) package,
            // so any *Test class added to this file is picked up automatically.
            .selectors(org.junit.platform.engine.discovery.DiscoverySelectors
                .selectPackage(""))
            .build();

        // Live, per-test output -- prints as each test finishes (PASS / FAIL / SKIP)
        var verbose = new org.junit.platform.launcher.TestExecutionListener() {
            @Override
            public void executionSkipped(
                    org.junit.platform.launcher.TestIdentifier id, String reason) {
                if (id.isTest())
                    System.out.println("SKIP  " + id.getDisplayName() + "  (" + reason + ")");
            }

            @Override
            public void executionFinished(
                    org.junit.platform.launcher.TestIdentifier id,
                    org.junit.platform.engine.TestExecutionResult result) {
                if (!id.isTest()) return;
                switch (result.getStatus()) {
                    case SUCCESSFUL:
                        System.out.println("PASS  " + id.getDisplayName());
                        break;
                    case FAILED:
                        System.out.println("FAIL  " + id.getDisplayName());
                        result.getThrowable().ifPresent(t ->
                            System.out.println("      " + t.getMessage()));
                        break;
                    default:
                        break;
                }
            }
        };

        // Aggregate summary -- printed once at the end
        var summaryListener = new org.junit.platform.launcher.listeners.SummaryGeneratingListener();

        launcher.execute(request, verbose, summaryListener);

        var summary = summaryListener.getSummary();
        System.out.println();
        System.out.println(
            summary.getTestsSucceededCount() + " passed, " +
            summary.getTestsFailedCount()    + " failed, " +
            summary.getTestsSkippedCount()   + " skipped"
        );

        if (summary.getTotalFailureCount() > 0) System.exit(1);
    }
}
"""


def _build_java_tests(meta: dict) -> str:
    snippet                  = meta["snippets"].get("java", "")
    method, params, ret_type = _java_method_info(snippet)
    examples                 = parse_examples(meta)
    array_types = {"int[]", "String[]", "double[]", "long[]", "boolean[]", "char[]"}

    def to_java_arg(raw: str) -> str:
        """Convert a raw LeetCode input string to a Java literal.

        Handles:
          [2,7,11,15]  ->  new int[]{2,7,11,15}
          "hello"      ->  "hello"
          42           ->  42        (unchanged)
        """
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1]
            # Detect element type: quoted strings -> String, else int
            if inner.startswith('"') or inner.startswith("'"):
                return f'new String[]{{{inner}}}'
            return f"new int[]{{{inner}}}"
        return raw

    def to_java_expected(val: str, rtype: str) -> str:
        """Convert a parsed output string to the right Java expected literal."""
        val = val.strip()
        if rtype in array_types:
            elem_type = rtype.replace("[]", "")
            inner = val[1:-1] if val.startswith("[") else val
            return f"new {elem_type}[]{{{inner}}}"
        if rtype == "boolean":
            return val.lower()
        return val

    def test_class(class_name: str, field_name: str) -> list[str]:
        block = [
            f"class {class_name}Test {{",
            f"    private final {class_name} {field_name} = new {class_name}();",
            "",
        ]
        for ex in examples:
            raw_args = ex.inputs[: len(params)]
            java_args = [to_java_arg(a) for a in raw_args]
            call = f"{field_name}.{method}({', '.join(java_args)})"
            block.append('    @Disabled("not solved yet")')
            block.append("    @Test")
            block.append(f"    void testExample{ex.index}() {{")
            if ex.output is not None:
                expected = to_java_expected(ex.output, ret_type)
                if ret_type in array_types:
                    block.append(f"        assertArrayEquals({expected}, {call});")
                elif ret_type == "boolean":
                    block.append(f"        assertEquals({expected}, {call});")
                else:
                    block.append(f"        assertEquals({expected}, {call});")
            else:
                block.append(f"        // TODO: assertEquals(<expected>, {call});")
            block.append("    }")
            block.append("")
        block.append("}")
        return block

    lines = [
        "",
        "",
        "// " + "-" * 73,
        "// Tests  (remove @Disabled once your solution is correct)",
        "// " + "-" * 73,
        "",
    ]
    lines += test_class("Solution", "solution")
    return "\n".join(lines)


# ---- File assembly -----------------------------------------------------------

def _java_default_return(ret_type: str) -> str:
    """Return a valid Java default value for the given return type."""
    defaults = {
        "void":    "",
        "int":     "0",
        "long":    "0L",
        "double":  "0.0",
        "float":   "0.0f",
        "boolean": "false",
        "char":    "'\\0'",
        "String":  "null",
    }
    if ret_type in defaults:
        return defaults[ret_type]
    if ret_type.endswith("[]"):
        return "null"
    return "null"  # covers List<>, Map<>, etc.

def _header_py(meta: dict, topic: str) -> str:
    diff  = meta["difficulty"].capitalize()
    emoji = DIFFICULTY_EMOJI.get(meta["difficulty"], "")
    return (
        '"""\n'
        f"Problem:    {meta['title']}\n"
        f"Link:       https://leetcode.com/problems/{meta['slug']}/\n"
        f"Number:     {meta['number']}\n"
        f"Topic:      {TOPIC_DISPLAY[topic]}\n"
        f"Difficulty: {diff}  {emoji}\n"
        "\n"
        "---\n"
        "\n"
        "Problem Statement:\n"
        "    (paste from LeetCode)\n"
        "\n"
        "Examples:\n"
        "    Input:  ...\n"
        "    Output: ...\n"
        "\n"
        "Constraints:\n"
        "    - ...\n"
        "\n"
        "---\n"
        "\n"
        "Approach:\n"
        "    ...\n"
        "\n"
        "Complexity:\n"
        "    Time:  O(?)\n"
        "    Space: O(?)\n"
        '"""\n'
        "\n"
        "from typing import List, Optional\n"
        "\n"
        "\n"
    )


def _header_java(meta: dict, topic: str) -> str:
    diff  = meta["difficulty"].capitalize()
    emoji = DIFFICULTY_EMOJI.get(meta["difficulty"], "")
    return (
        _JBANG_DEPS
        # All imports must appear before any class declaration in Java.
        # Hoisting them here (after //DEPS, before the Javadoc) keeps the
        # file legal regardless of what the LeetCode snippet adds.
        + "import org.junit.jupiter.api.Disabled;\n"
        + "import org.junit.jupiter.api.Test;\n"
        + "import static org.junit.jupiter.api.Assertions.*;\n"
        + "import java.util.*;\n"
        + "\n"
        + "/**\n"
        f" * Problem:    {meta['title']}\n"
        f" * Link:       https://leetcode.com/problems/{meta['slug']}/\n"
        f" * Number:     {meta['number']}\n"
        f" * Topic:      {TOPIC_DISPLAY[topic]}\n"
        f" * Difficulty: {diff}  {emoji}\n"
        " *\n"
        " * -------------------------------------------------------------------\n"
        " *\n"
        " * Problem Statement:\n"
        " *   (paste from LeetCode)\n"
        " *\n"
        " * Approach:\n"
        " *   ...\n"
        " *\n"
        " * Complexity:\n"
        " *   Time:  O(?)\n"
        " *   Space: O(?)\n"
        " */\n"
        "\n"
    )


def generate_file(meta: dict, topic: str, ext: str) -> str:
    if ext == "py":
        return (
            _header_py(meta, topic)
            + meta["snippets"].get("py", "class Solution:\n    pass\n")
            + _build_py_tests(meta)
        )
    if ext == "java":
        return (
            _header_java(meta, topic)
            + meta["snippets"].get("java", "class Solution {\n}\n")
            + _build_java_tests(meta)
            + _JBANG_RUNNER
        )
    # Other languages -- minimal scaffold
    snippet = meta["snippets"].get(ext, "// solution here\n")
    return f"// {meta['title']} -- {meta['difficulty'].capitalize()}\n\n" + snippet


# ---- Topic picker ------------------------------------------------------------

def pick_topic() -> str:
    print("\nPick a topic:")
    for i, t in enumerate(TOPIC_ORDER, 1):
        print(f"  {i:>2}. {TOPIC_DISPLAY[t]}")

    while True:
        raw = input("\nTopic number: ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(TOPIC_ORDER):
                return TOPIC_ORDER[idx]
        matches = [t for t in TOPIC_ORDER if raw.lower() in t]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            print(f"  Ambiguous -- matches: {', '.join(matches)}")
            continue
        print(f"  Invalid -- enter a number (1-{len(TOPIC_ORDER)}) or part of a topic name.")


# ---- Main --------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a new LeetCode solution file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/new.py 121\n"
            "  python scripts/new.py 121 --lang java\n"
            "  python scripts/new.py 121 --lang py --lang java\n"
        ),
    )
    parser.add_argument("number", type=int, help="LeetCode problem number")
    parser.add_argument(
        "--lang", "-l",
        action="append",
        dest="langs",
        choices=SUPPORTED_LANGS,
        metavar="LANG",
        help=f"language(s) to scaffold ({', '.join(SUPPORTED_LANGS)}). "
             "Repeat for multiple. Defaults to py.",
    )
    return parser.parse_args()


def main() -> None:
    args  = parse_args()
    langs = args.langs or ["py"]

    try:
        meta = fetch_problem(args.number)
    except RuntimeError as e:
        print(f"\n  {e}", file=sys.stderr)
        sys.exit(1)

    diff_emoji = DIFFICULTY_EMOJI.get(meta["difficulty"], "")
    print(f"\n  #{meta['number']} -- {meta['title']} "
          f"({meta['difficulty'].capitalize()} {diff_emoji})")

    examples = parse_examples(meta)
    parsed   = sum(1 for e in examples if e.output is not None)
    print(f"  {len(examples)} example(s) found, "
          f"{parsed} with parseable outputs, "
          f"{len(examples) - parsed} as TODO stubs")

    topic     = pick_topic()
    topic_dir = REPO_ROOT / topic
    topic_dir.mkdir(exist_ok=True)

    created: list[Path] = []
    for ext in langs:
        filename = f"{meta['number']}-{meta['slug']}.{ext}"
        dest     = topic_dir / filename

        if dest.exists():
            print(f"\n  {dest.relative_to(REPO_ROOT)} already exists -- skipping.")
            continue

        dest.write_text(generate_file(meta, topic, ext), encoding="utf-8")

        gitkeep = topic_dir / ".gitkeep"
        if gitkeep.exists():
            gitkeep.unlink()

        print(f"\n  Created: {dest.relative_to(REPO_ROOT)}")
        created.append(dest)

    if not created:
        print("\nNo files created.")
        sys.exit(0)

    editor = os.environ.get("EDITOR", "")
    if editor:
        subprocess.run([editor] + [str(p) for p in created])

    print(f"\nDone! Solve it, remove the skip decorators, then:")
    print(f"    git add . && git commit -m 'solve: {meta['slug']}'")


if __name__ == "__main__":
    main()
