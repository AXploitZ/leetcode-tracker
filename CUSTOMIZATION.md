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

`scripts/new.py` always scaffolds a single `Solution` class. If you want to
keep a second approach (e.g. a brute-force version for comparison) in the
same file, add it yourself following the pattern below -- this keeps the
script simple while still letting you compare approaches when it's useful.

**Python**

Add another class with a name that describes the approach, plus a comment
with its complexity:

```python
class SolutionBruteForce:
    # Time: O(n^2), Space: O(1)
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []


class Solution:
    # Time: O(n), Space: O(n)
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        ...
```

Add a matching `@pytest.mark.skip` test for the new class -- pytest discovers
any `test_*` function in the file automatically, so no other wiring is needed:

```python
@pytest.mark.skip(reason='not solved yet')
def test_brute_force_example_1():
    assert SolutionBruteForce().twoSum([2, 7, 11, 15], 9) == [0, 1]
```

**Java**

Add the second class and a matching `*Test` class:

```java
class SolutionBruteForce {
    // Time: O(n^2), Space: O(1)
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++)
            for (int j = i + 1; j < nums.length; j++)
                if (nums[i] + nums[j] == target)
                    return new int[]{i, j};
        return new int[]{};
    }
}

class SolutionBruteForceTest {
    private final SolutionBruteForce solution = new SolutionBruteForce();

    @Disabled("not solved yet")
    @Test
    void testExample1() {
        assertArrayEquals(new int[]{0, 1}, solution.twoSum(new int[]{2, 7, 11, 15}, 9));
    }
}
```

No changes to `JBangRunner` are needed -- it discovers every `*Test` class in
the file automatically via `selectPackage("")`, so the new test class is
picked up and reported the next time you run `jbang <file>.java`.
