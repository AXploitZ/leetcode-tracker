# Contributing

Contributions that improve the template for everyone are welcome — bug fixes,
language support, script improvements, and documentation.

---

## What belongs here

- Fixes to `scripts/new.py` or `scripts/update_readme.py`
- New language templates under `templates/`
- CI workflow improvements
- Documentation clarifications

What does not belong here: personal solution files. This repo is a template,
not a shared solution bank.

---

## Making a change

1. Fork the repo and create a branch:
   ```bash
   git checkout -b fix/description-of-change
   ```

2. Make your changes. If touching `new.py` or `update_readme.py`, verify the
   scripts still run without errors:
   ```bash
   python scripts/new.py --help
   python scripts/update_readme.py
   ```

3. If adding a new language template, make sure it follows the same header
   format as `templates/template.py` and `templates/Template.java`.

4. Open a pull request with a clear description of what changed and why.

---

## Reporting issues

Open a GitHub issue with:
- The command you ran
- The full error output
- Your Python version (`python --version`) and OS
