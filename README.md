# LeetCode Solutions

![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)
![Update README](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/update-readme.yml/badge.svg)
<!-- BEGIN_BADGE:problems -->
![Problems Solved](https://img.shields.io/badge/problems_solved-0-blue)
<!-- END_BADGE:problems -->

A template repository for tracking LeetCode solutions, with automated README
updates, multi-language support, and CI-verified test cases.

---

## Getting started

### 1. Create your repo from this template

Click **Use this template** at the top of the GitHub page and create a new
repository under your account.

### 2. Clone and run setup

```bash
git clone https://github.com/<you>/<your-repo>.git
cd <your-repo>
python setup.py
```

The setup script will:
- Ask for your GitHub username and repo name, then update the badge URLs
- Ask for your preferred default language (Python by default)
- Check that Python, pytest, and JBang are installed locally

### 3. Install dependencies

```bash
# Python test runner
pip install pytest

# Java test runner (required only if you solve in Java)
# See https://www.jbang.dev/download/ for your platform
brew install jbang        # macOS
sdk install jbang         # Linux via SDKMAN
choco install jbang       # Windows via Chocolatey
```

### 4. Commit the setup changes and push

```bash
git add README.md scripts/new.py
git commit -m "chore: personalise repo"
git push
```

The CI badge will go green once the first push runs.

---

## Solving a problem

```bash
python scripts/new.py 121
```

The script fetches the problem title, difficulty, and starter code from
LeetCode, asks you to pick a topic, and creates a pre-filled solution file.
Remove the `@pytest.mark.skip` / `@Disabled` decorators from the tests once
your solution is correct, then commit and push.

```bash
# Scaffold with a specific language (default: py)
python scripts/new.py 121 --lang java

# Scaffold both at once
python scripts/new.py 121 --lang py --lang java
```

### Running tests locally

```bash
# Python -- runs all solution files
pytest

# Python -- single file
pytest arrays-hashing/0001-two-sum.py -v

# Java -- single file
jbang arrays-hashing/0001-two-sum.java
```

---

## Repository structure

```
.
├── arrays-hashing/
├── two-pointers/
├── sliding-window/
├── stack/
├── binary-search/
├── linked-list/
├── trees/
├── tries/
├── heap-priority-queue/
├── backtracking/
├── graphs/
├── dynamic-programming/
├── greedy/
├── intervals/
├── math-geometry/
├── bit-manipulation/
├── examples/               # reference solutions showing expected file format
├── scripts/
│   ├── new.py              # scaffold a new solution
│   └── update_readme.py    # auto-run by CI to regenerate the tables below
├── templates/              # base templates for each language
├── setup.py                # one-time personalisation script
└── pyproject.toml          # pytest configuration
```

Solution files are named `<number>-<slug>.<ext>`:
```
0001-two-sum.py
0001-two-sum.java
0001-two-sum.cpp
```

---

## Solutions

> Auto-generated on every push. Do not edit manually.

<!-- BEGIN_SOLUTIONS_TABLE -->
| # | Problem | Difficulty | Topic |  | Notes |
|---|---------|------------|-------||-------|
<!-- END_SOLUTIONS_TABLE -->

---

## Progress by topic

> Auto-generated on every push. Do not edit manually.

<!-- BEGIN_TOPICS_TABLE -->
| Topic | Easy | Medium | Hard | Total |
|-------|------|--------|------|-------|
| [Arrays & Hashing](./arrays-hashing/) | 0 | 0 | 0 | 0 |
| [Two Pointers](./two-pointers/) | 0 | 0 | 0 | 0 |
| [Sliding Window](./sliding-window/) | 0 | 0 | 0 | 0 |
| [Stack](./stack/) | 0 | 0 | 0 | 0 |
| [Binary Search](./binary-search/) | 0 | 0 | 0 | 0 |
| [Linked List](./linked-list/) | 0 | 0 | 0 | 0 |
| [Trees](./trees/) | 0 | 0 | 0 | 0 |
| [Tries](./tries/) | 0 | 0 | 0 | 0 |
| [Heap / Priority Queue](./heap-priority-queue/) | 0 | 0 | 0 | 0 |
| [Backtracking](./backtracking/) | 0 | 0 | 0 | 0 |
| [Graphs](./graphs/) | 0 | 0 | 0 | 0 |
| [Dynamic Programming](./dynamic-programming/) | 0 | 0 | 0 | 0 |
| [Greedy](./greedy/) | 0 | 0 | 0 | 0 |
| [Intervals](./intervals/) | 0 | 0 | 0 | 0 |
| [Math & Geometry](./math-geometry/) | 0 | 0 | 0 | 0 |
| [Bit Manipulation](./bit-manipulation/) | 0 | 0 | 0 | 0 |
<!-- END_TOPICS_TABLE -->

---

## Customisation

See [CUSTOMIZATION.md](./CUSTOMIZATION.md) for how to add topics, support new
languages, and adjust the folder structure.
