# Customization Guide

This document covers how to extend or adjust the repo beyond the defaults.

---

## Adding a new topic

1. Create the folder at the repo root:
   ```bash
   mkdir my-new-topic
   touch my-new-topic/.gitkeep
   ```

2. Add it to the `TOPIC_ORDER` and `TOPIC_DISPLAY` dicts in both
   `scripts/new.py` and `scripts/update_readme.py`:
   ```python
   # In both files
   TOPIC_ORDER = [
       ...
       "my-new-topic",
   ]

   TOPIC_DISPLAY = {
       ...
       "my-new-topic": "My New Topic",
   }
   ```

3. Add a row to the topics table in `README.md` — it will be auto-populated
   on the next push, but adding the row now keeps it in the right order:
   ```markdown
   | [My New Topic](./my-new-topic/) | 0 | 0 | 0 | 0 |
   ```

---

## Supporting a new language

There are four places to update.

### 1. `scripts/new.py`

Add the file extension to `SUPPORTED_LANGS`:
```python
SUPPORTED_LANGS = ["py", "java", "cpp", "ts", "go", "rs", "kt"]
```

Add a mapping from LeetCode's `langSlug` to your extension in `_LC_LANG_MAP`:
```python
_LC_LANG_MAP = {
    ...
    "kotlin": "kt",
}
```

Add a header generator function following the pattern of `_header_py` or
`_header_java`, then handle the new extension in `generate_file`:
```python
def generate_file(meta: dict, topic: str, ext: str) -> str:
    if ext == "py":   ...
    if ext == "java": ...
    if ext == "kt":
        return _header_kt(meta, topic) + meta["snippets"].get("kt", "")
    ...
```

### 2. `scripts/update_readme.py`

Add the extension and display name to `LANG_EXT`, and optionally a badge
character to `LANG_BADGE`:
```python
LANG_EXT = {
    ...
    ".kt": "Kotlin",
}

LANG_BADGE = {
    ...
    "Kotlin": "K",
}
```

### 3. `templates/`

Create `templates/template.kt` following the same header format as the
existing templates.

### 4. `.github/workflows/ci.yml`

Add the extension to the `paths` trigger in both `on.push` and
`on.pull_request`:
```yaml
paths:
  - "*/*.kt"
```

Add a new job to compile and run tests for the language, or extend the
existing Java job if the language runs on the JVM and supports JBang.

---

## Changing the default language

Run the setup script again and choose a different language when prompted, or
edit `scripts/new.py` directly:
```python
langs = args.langs or ["java"]  # change "py" to your preferred default
```

---

## Renaming or removing a topic

1. Rename or delete the folder.
2. Update `TOPIC_ORDER` and `TOPIC_DISPLAY` in both script files.
3. Update the topics table row in `README.md`.
4. Move any existing solution files to the new location if renaming.

---

## Changing the file naming convention

Solution files are named `<number>-<slug>.<ext>` by `scripts/new.py`. The
number is always zero-padded to four digits. If you want a different format,
update the `filename` line in `new.py`'s `main()` function:
```python
filename = f"{meta['number']}-{meta['slug']}.{ext}"
```

The `update_readme.py` scanner derives the problem number from the filename
using `re.match(r"^(\d{3,4})", path.stem)`, so any format that starts with
the problem number will continue to work.

---

## Multiple solutions for the same problem

Add additional classes to the same file. Use descriptive names that convey
the approach:

```python
class SolutionBruteForce:
    # Time: O(n^2), Space: O(1)
    ...

class Solution:
    # Time: O(n), Space: O(n)
    ...
```

Add a corresponding test class for each:
```python
@pytest.mark.skip(reason='not solved yet')
def test_brute_force_example_1():
    assert SolutionBruteForce().twoSum([2, 7, 11, 15], 9) == [0, 1]
```

The `scripts/new.py` scaffolds a `SolutionBruteForce` stub alongside the
main `Solution` class by default.
