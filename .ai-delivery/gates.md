---
schema_version: 1
generated_on: 2026-08-12
regenerated_on: 2026-09-07
---

# Quality Gates

## About This File

Discovered from this repository — these are the commands the project actually runs, in the
project's own invocation form. `detected` = found in repo config/scripts/CI;
`adopted` = proposed by setup and confirmed, no prior project config; `unavailable` = no
such gate exists here. `blocking` gates fail verification; `advisory` gates report only.

This project is greenfield: nothing was discovered, so every command below is `adopted` and
none has been executed. The first verify run is what proves them.

## Commands

### Lint
- command: uv run ruff check src/ tests/
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Format
- command: uv run ruff format --check src/ tests/
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Type Check
- command: uv run mypy src/
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Test
- command: uv run pytest
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Coverage
- command: uv run pytest --cov=src --cov-report=term-missing
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### SAST
- command: uv run bandit -r src/ -ll
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Dependency Scan
- command: uv run pip-audit
- source: adopted (no repo config found — greenfield)
- status: adopted
- gate: blocking

### Secret Detection
- command: gitleaks detect --source .
- source: adopted (no repo config found — greenfield)
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
