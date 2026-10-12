# Verification record: Pull request checklist

This is the durable record of how the pull request checklist was verified: each unit's
verdict, the evidence behind it, and any warnings accepted. It matters because the
Linear comments carry the narrative, but this file is the committed record a later
reviewer can read next to the code.

**Feature directory:** `.ai-delivery/features/pull-request-checklist/`
**Linear project:** P-MAX-12 Pull request checklist
**Profile:** software

> **Terms used here.** MAX-45 (`CONTRIBUTING.md`), MAX-46 (the README sentence) and MAX-47
> (the integration unit) are Linear issues. The *setup check* is the kit's staleness
> check, which reads FRESH or STALE. A verdict of *pass-with-warnings* means every
> acceptance criterion passed and the verifier recorded non-blocking warnings. The
> checks are the pytest modules in `checks/`, run by naming that directory.

## Unit verdicts

| Unit | Verdict | Checks | Rework cycles | Label now |
|---|---|---|---|---|
| MAX-45, Publish the pull request checklist in CONTRIBUTING.md | pass-with-warnings; warnings accepted by Max Adamsky, 2026-09-22 | 23 of 23 pass | 0 | `verified` |
| MAX-46, Link the pull request checklist from the README | pass-with-warnings; warnings accepted by Max Adamsky, 2026-09-22 | 12 of 12 pass | 0 | `verified` |

## Evidence, batch 1, 2026-09-22

- **Checks directory:** 35 passed, in one run of both modules.
- **Plain `uv run pytest` from the root:** "no tests ran", exit code 5. Checklist item 3
  is true.
- **ruff check, ruff format --check and mypy on the checks directory:** clean.
- **bandit on the checks directory, medium severity and above:** no findings.
- **gitleaks on `CONTRIBUTING.md`, `README.md` and the checks directory:** no leaks.
- **`git diff 7133948 -- README.md`:** two lines added at the end, none removed.
- **`CONTRIBUTING.md`:** 30 lines, none over 90 columns, ending with a single newline.
- **Setup check:** STALE, reporting only that `README.md` changed. This is expected
  until MAX-47's setup re-run.

## Accepted warnings

Max Adamsky accepted these on 2026-09-22 rather than rework the check modules. None
concerns the published documents.

- **MAX-45:**
  - The excluded-word check misses hyphenated compounds such as "kit-based".
  - Several checks have no deliberately broken sample proving they can fire, among them
    the `codex/` rejection and the check for content after item 5.
  - Required phrases match as substrings, and the settled wording "one commit per" and
    "filed or picked" is not required by the check, although the document carries it.
- **MAX-46:** the title check, the file-ending check and the two-link case of the link
  check have no deliberately broken sample.

## Approved exceptions

- **ADR-001.** The check modules sit outside the test command recorded in
  `.ai-delivery/gates.md`, so that a plain `uv run pytest` keeps exiting with code 5, as
  FR-004 requires. FR-004 outranks the project rubric's reachability item under config's
  `nfr_precedence`. Max Adamsky approved it with the implementation plan.
- **Recorded gates.** The lint, format and type-check commands in `gates.md` name `src/`
  and `tests/`, which do not exist, so they cannot pass here. The same tools ran on the
  checks directory by name.

## Gate states

The software profile carries no sign-off gate. The setup check read STALE after the README
edit, and it has read FRESH since the setup re-run at integration on 2026-09-22.

## Integration, MAX-47, 2026-09-22

**Verdict:** the post-integration verifier returned pass-with-warnings, and Max Adamsky
accepted the warnings. The joined feature works end to end:
- README's last sentence links to the root `CONTRIBUTING.md`, which holds the checklist.
- Checklist item 3's command behaves as the item says.
- A kit session passes the setup check.

**What integration changed:**
- Created `checks/test_checklist_reachable.py`, with 7 checks: 3 against the real files
  and 4 against temporary sample files.
- Re-ran setup in the main session. It rewrote `.ai-delivery/stack-fingerprint` (README's
  new hash, with CONTRIBUTING.md added to the files setup reads), `.ai-delivery/conventions.md`
  (five CONTRIBUTING.md conventions, two Linear lines and three dates refreshed) and
  `.ai-delivery/gates.md` (the Test gate is now `detected`), and it added one entry to
  `docs/decisions.md`. `config.md` and `rubrics.md` are unchanged. Max Adamsky confirmed
  every change in setup's proposal.

**Evidence:**
- **All three check modules:** 42 passed (23, 12 and 7).
- **Plain `uv run pytest`:** "no tests ran", exit code 5.
- **Setup check:** STALE before the re-run, FRESH with exit 0 after it.
- **`git diff 7133948 -- README.md`:** two lines added, none removed.
- **ruff check, ruff format --check, mypy and bandit on the checks directory:** clean.
- **gitleaks:** no leaks on every new and changed file, or across the git history.
- **pip-audit:** no known vulnerabilities.
- **The recorded Lint, Format and Type Check gates** exit with errors, because `src/`
  and `tests/` do not exist. That is the known gap. Test and Coverage exit with code 5.

**Accepted warnings:**
- **Records the setup re-run made out of date.** These still say CONTRIBUTING.md leaves
  the setup record alone, or that `gates.md` is unchanged:
  - contract C3's "Unaffected" bullet in `design/1b-contracts.md`;
  - the setup-record constraint in `requirements.md`;
  - the `gates.md` sentence in `design/1a-discovery.md`;
  - the `gates.md` risk row in `design/1c-operations.md`;
  - the Files to Modify list in `specs/integration.md`.

  The 2026-09-22 entry in `docs/decisions.md` supersedes all five.
- **Contract C4's error table** omits LinkTargetMismatch for `test_checklist_reachable.py`.
- **Deployment constraint 3 in `design/1c-operations.md`** names only README. The setup
  record now also hashes CONTRIBUTING.md, so whatever carries either file to `main` must
  carry a matching record.
- **Setup-record wording:**
  - `conventions.md`'s branch line says "pushed to this repository", which CONTRIBUTING.md
    does not say.
  - Its toolchain line still calls the gates the only invocation.
  - `gates.md`'s About paragraph says no verify run has executed the gates.
- **The integration check** has no failing sample for a missing title or for a directory
  as the link target.

A stray `.coverage` file, left by the orchestrator's Coverage-gate run, was removed before
close-out.

## Outcome

MAX-45, MAX-46 and MAX-47 are closed as Done. The feature's prototype is complete on the
`live-proof-2026-09-21` branch, uncommitted.

Max Adamsky owns the next actions: commit the change and open the handoff pull request, and
settle open question 3, the route to `main`, before 2026-10-05. That settlement includes
carrying a setup record that matches `main`'s README and CONTRIBUTING.md.
