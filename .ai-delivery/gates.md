---
schema_version: 1
generated_on: 2026-08-12
regenerated_on: 2026-09-22
---

# Quality Gates

## About This File

Discovered from this repository — these are the commands the project actually runs, in the
project's own invocation form. `detected` = found in repo config/scripts/CI;
`adopted` = proposed by setup and confirmed, no prior project config; `unavailable` = no
such gate exists here. `blocking` gates fail verification; `advisory` gates report only.

This project now has a dependency manifest: `pyproject.toml` declares the tools below in its
dev group, and `uv.lock` fixes their versions. The manifest names the tools; it defines no
entry point for running them, and the project has no scripts, Makefile or CI, so every
command below except Test remains `adopted` — setup's invocation, not the project's own.
Test is `detected`: `CONTRIBUTING.md` names `uv run pytest` as the command every
contributor runs before opening a pull request. No verify run has executed these gates
yet; the first one is what proves them.

## Commands

### Lint
- command: uv run ruff check src/ tests/
- source: adopted (ruff declared in pyproject.toml dev group; no [tool.ruff] config and no project-defined entry point)
- status: adopted
- gate: blocking

### Format
- command: uv run ruff format --check src/ tests/
- source: adopted (ruff declared in pyproject.toml dev group; no formatter config and no project-defined entry point)
- status: adopted
- gate: blocking

### Type Check
- command: uv run mypy src/
- source: adopted (mypy declared in pyproject.toml dev group; no [tool.mypy] config and no project-defined entry point)
- status: adopted
- gate: blocking

### Test
- command: uv run pytest
- source: detected (CONTRIBUTING.md item 3 names this command as the one every contributor runs before opening a pull request; pytest declared in pyproject.toml dev group, with no [tool.pytest.ini_options])
- status: detected
- gate: blocking

### Coverage
- command: uv run pytest --cov=src --cov-report=term-missing
- source: adopted (pytest-cov declared in pyproject.toml dev group; no [tool.coverage] config and no project-defined entry point)
- status: adopted
- gate: blocking

### SAST
- command: uv run bandit -r src/ -ll
- source: adopted (bandit declared in pyproject.toml dev group; no .bandit config and no project-defined entry point)
- status: adopted
- gate: blocking

### Dependency Scan
- command: uv run pip-audit
- source: adopted (pip-audit declared in pyproject.toml dev group; no CI invocation and no project-defined entry point)
- status: adopted
- gate: blocking

### Secret Detection
- command: gitleaks detect --source .
- source: adopted (no secret scanner declared in the manifest and no repo config found)
- status: adopted
- gate: blocking

### IaC Scan
- command: null
- source: n/a (no infrastructure code and no cloud provider recorded)
- status: unavailable
- gate: n/a

### Build
- command: null
- source: n/a (no distributable artifact defined yet)
- status: unavailable
- gate: n/a

## Thresholds

- coverage_line: 80   [source: tiered scaffold, confirmed by user · tier: 3-model · verified: 2026-08-12]
- coverage_branch: 70   [source: tiered scaffold, confirmed by user · tier: 3-model · verified: 2026-08-12]
- complexity_per_function: warn > 10, fail > 20
- duplication: warn 3–7%, fail > 7%
- lint: 0 errors blocking; warnings ≤ 10 advisory
- pii_in_logs: 0 — always blocking
- critical_path_escalation: paths matching auth/, payments/, security/, session/, token/,
  credential/ use coverage_line ≥ 90

## Threshold Provenance

- project-config: (none — nothing configured in this repository)
- scaffold-default: coverage_line, coverage_branch, complexity_per_function, duplication,
  lint, pii_in_logs, critical_path_escalation
- user-set: (none)
