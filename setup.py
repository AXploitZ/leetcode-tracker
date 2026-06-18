#!/usr/bin/env python3
"""
setup.py -- one-time setup for your LeetCode solutions repo

Run this once after creating your repo from the template:
    python setup.py

What it does:
    1. Asks for your GitHub username
    2. Rewrites the badge URLs in README.md to point to your repo
    3. Optionally sets your preferred default language for new solutions
    4. Confirms your local Python and JBang installations
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
README    = REPO_ROOT / "README.md"
NEW_PY    = REPO_ROOT / "scripts" / "new.py"

SUPPORTED_LANGS = ["py", "java", "cpp", "ts", "go", "rs"]


# ---- Helpers -----------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    return raw if raw else default


def check_tool(name: str, version_flag: str = "--version") -> bool:
    return shutil.which(name) is not None


# ---- Steps -------------------------------------------------------------------

def step_github_username() -> str:
    print("\n-- GitHub username")
    print("   Used to point the CI badge URLs at your repo.")
    username = ""
    while not username:
        username = ask("   GitHub username").strip()
        if not username:
            print("   Username cannot be empty.")
    return username


def step_repo_name() -> str:
    print("\n-- Repository name")
    print("   The name you gave the repo on GitHub.")
    return ask("   Repo name", default="leetcode")


def step_default_lang() -> str:
    print("\n-- Default language for new solutions")
    print(f"   Options: {', '.join(SUPPORTED_LANGS)}")
    while True:
        lang = ask("   Default language", default="py")
        if lang in SUPPORTED_LANGS:
            return lang
        print(f"   Invalid choice. Choose from: {', '.join(SUPPORTED_LANGS)}")


def update_readme(username: str, repo_name: str) -> None:
    content = README.read_text(encoding="utf-8")

    # Replace any existing username placeholder or prior username in badge URLs
    content = re.sub(
        r"https://github\.com/[^/]+/[^/]+/actions/workflows/ci\.yml/badge\.svg",
        f"https://github.com/{username}/{repo_name}/actions/workflows/ci.yml/badge.svg",
        content,
    )
    content = re.sub(
        r"https://github\.com/[^/]+/[^/]+/actions/workflows/update-readme\.yml/badge\.svg",
        f"https://github.com/{username}/{repo_name}/actions/workflows/update-readme.yml/badge.svg",
        content,
    )

    README.write_text(content, encoding="utf-8")
    print(f"   README.md updated with github.com/{username}/{repo_name}")


def update_default_lang(lang: str) -> None:
    content = NEW_PY.read_text(encoding="utf-8")

    old = 'langs = args.langs or ["py"]  # default to Python'
    new = f'langs = args.langs or ["{lang}"]  # default to {lang}'

    if old in content:
        content = content.replace(old, new, 1)
        NEW_PY.write_text(content, encoding="utf-8")
        print(f"   scripts/new.py default language set to '{lang}'")
    else:
        print("   Could not update default language in new.py -- set it manually.")


def check_dependencies() -> None:
    print("\n-- Checking dependencies")

    python_ok = sys.version_info >= (3, 10)
    print(f"   Python {sys.version.split()[0]} ... {'ok' if python_ok else 'needs 3.10+'}")

    pytest_ok = check_tool("pytest")
    print(f"   pytest ... {'ok' if pytest_ok else 'not found  (run: pip install pytest)'}")

    jbang_ok = check_tool("jbang")
    print(f"   jbang  ... {'ok' if jbang_ok else 'not found  (see https://www.jbang.dev/download/)'}")


# ---- Main --------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  LeetCode repo setup")
    print("=" * 60)

    username    = step_github_username()
    repo_name   = step_repo_name()
    default_lang = step_default_lang()

    print("\n-- Applying changes")
    update_readme(username, repo_name)
    update_default_lang(default_lang)

    check_dependencies()

    print("\n" + "=" * 60)
    print("  Setup complete.")
    print("=" * 60)
    print(f"""
Next steps:
  1. Commit the changes made by this script:
       git add README.md scripts/new.py
       git commit -m "chore: personalise repo for {username}"
       git push

  2. Start solving:
       python scripts/new.py <problem-number>

  3. See examples/ for a reference solution showing the expected
     file structure and comment format.
""")


if __name__ == "__main__":
    main()
