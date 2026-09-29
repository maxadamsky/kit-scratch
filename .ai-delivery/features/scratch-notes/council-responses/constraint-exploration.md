## Council Response

**Evidence consulted:** /Users/maxdamsky/Projects/kit-scratch/pyproject.toml, /Users/maxdamsky/Projects/kit-scratch/README.md, /Users/maxdamsky/Projects/kit-scratch/CONTRIBUTING.md, /Users/maxdamsky/Projects/kit-scratch/.gitignore, /Users/maxdamsky/Projects/kit-scratch/uv.lock (grep only), /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/features/scratch-notes/qa-log.md

### Direction 1: One stdlib script plus one test file, no packaging change

**Approach Summary**
The repository has no Python source at all. `pyproject.toml` has `dependencies = []`, no `[build-system]` and no `[project.scripts]`, and `CONTRIBUTING.md` says `uv run pytest` currently exits 5 with "no tests ran". The smallest build is therefore two new files and nothing else:
- `scratch_notes.py` at the repository root. It opens the file read-only, scans it line by line with `re`, counts open items with `^\s*[-*+] \[ \]`, collects ATX headings (`^#{1,6}\s`), and skips lines inside ``` and ~~~ fenced blocks. It prints plain text, or `json.dumps` output when given `--json`.
- `test_scratch_notes.py`.

It uses the standard library's `argparse`, `re`, `json` and `sys`, catches `OSError` and `UnicodeDecodeError`, writes those errors to stderr and exits with 1. The shell prompt calls it as `python3 /path/to/scratch_notes.py notes.md --json` rather than through `uv run`, so each prompt draw skips uv's environment check. If you keep the test in `tests/` instead of the root, you also need a two-line `[tool.pytest.ini_options] pythonpath = ["."]` entry in the existing `pyproject.toml`.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| Two new files, and no change to `pyproject.toml` or `uv.lock` | No `scratch-notes` command on PATH: you call it by path, or add a shell alias |
| Nothing but the interpreter starts on each prompt draw, so it stays fast enough | You rely on `python3` on PATH being 3.11 or newer, which `requires-python` does not enforce outside uv |
| The first test module turns `uv run pytest` from exit 5 into a real gate, and the existing `pytest-cov`, `ruff`, `mypy` and `bandit` cover it with no new setup | `CONTRIBUTING.md` item 3 ("exit code 5 is the expected result") goes stale and needs a one-line edit |

**Risks**
- **Code-block false positives:** a `- [ ]` or `# ` inside a fenced code block would be counted. That breaks the success signal that the prompt count always matches a count by hand, so the fence tracking is required, not optional.
- **The parser is already installed:** `markdown-it-py` is in `.venv` because pip-audit pulls in `rich` (`uv.lock` lines 607 and 1012). An implementer could import it by accident. Nothing flags that import, because the package is installed; it would break the "no Markdown parser" constraint and would fail under a bare `python3` call. A test should run the script under `python3 -I` to prove it uses the standard library only.
- **Undefined edge cases:** The framing does not define headings or the JSON field names. My assumption: headings are ATX `#` lines only, not underlined ("setext") headings, and the JSON is `{"open": N, "headings": [...]}`. Your prompt scripts will depend on those field names, so fix them once in the tests.

**Estimated Complexity**
`Low`: this is about 60 lines of standard-library code and a table of test cases. Almost all the work is in the edge-case list: fences, indentation, `[x]` versus `[ ]`, numbered items and empty files.

### Direction 2: The same module, exposed as a `scratch-notes` console script

**Approach Summary**
This keeps Direction 1's code but installs it as a real command:
- Move the code into a `src/scratch_notes/` package.
- Add `[project.scripts] scratch-notes = "scratch_notes:main"` to `pyproject.toml`.
- Add a `[build-system]` section, for example hatchling, so that uv installs the project into `.venv`.

This matches the tool name in the framing literally, but it adds new files, a build backend and lockfile churn.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| A real `scratch-notes` command, as the framing names it | Adds a build backend. That is a build-time dependency, arguably against "no new dependency" |
| The Python version is pinned through uv | Calling `uv run scratch-notes` on every prompt draw adds uv's startup and sync check; avoiding that means hard-coding the `.venv/bin` path |

**Risks**
- **Prompt latency:** `uv run` in a prompt hook is noticeably slower than a bare interpreter, which puts the "every draw" constraint at risk.
- **Lockfile churn:** adding a build backend changes `uv.lock` and project metadata for no functional gain.

**Estimated Complexity**
`Low` to `Medium`: the code is the same, but the packaging and install path are new surface in a repository that has none today.

## What Already Exists

- `/Users/maxdamsky/Projects/kit-scratch/pyproject.toml`: a uv project already pinned to Python 3.11 or newer, with `pytest`, `pytest-cov`, `ruff`, `mypy` and `bandit` in the dev group. Test, coverage, lint, type-check and security scanning need no new setup.
- `/Users/maxdamsky/Projects/kit-scratch/uv.lock` and `.venv/`: the environment is already resolved, so Direction 1 needs no lockfile change.
- `/Users/maxdamsky/Projects/kit-scratch/CONTRIBUTING.md` item 3: `uv run pytest` is already the agreed gate. The first test module lands straight into it.
- Nothing in the repository does Markdown scanning, command-line parsing or JSON output. There is no source code to reuse, which confirms the developer's own prior-art answer.

## Strongest Statement

Build Direction 1: one standard-library file and one test file, with no packaging change, called from the prompt as `python3 scratch_notes.py --json` rather than through `uv run`. The size budget belongs in the edge-case tests, not in infrastructure. The fenced-code-block rule and the "`[x]` is not open" rule are what make the prompt count trustworthy, and that trust is the whole success signal.

Three items need action:
- The JSON field names and the heading definition are still open. You, Max Adamsky, as project lead, should settle them before the tests are written.
- If the change lands, whoever makes it needs to update item 3 of `CONTRIBUTING.md`.
- That same person should add the `python3 -I` test that guards against importing `markdown-it-py`.

**END OF RESPONSE. Do not add anything after this line.**
