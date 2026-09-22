# Design operations: Pull request checklist

This document covers what it takes for the pull request checklist to reach contributors
safely: security, the route to `main`, rollback, what is watched, and the risks. It
matters because GitHub shows the checklist only from `main`, which has not changed since
2026-08-28, and contributors arrive by 2026-10-05.

**Date:** 2026-09-22
**Feature directory:** `.ai-delivery/features/pull-request-checklist/`
**Builds on:** `design/1a-discovery.md` and `design/1b-contracts.md`

> **Terms used here.** MAX-45 and MAX-46 are the Linear issues for the two units:
> `CONTRIBUTING.md`, and the README sentence. "Question N" is open question N in
> `requirements.md`. The *setup check* is the kit's staleness check, which reads FRESH or
> STALE; the *setup record* is `.ai-delivery/stack-fingerprint`, the hashes it compares.
> C1 to C4 are the contracts in `1b-contracts.md`.

## Database migration strategy

Not applicable: no data changes. The feature adds one Markdown file, one README
paragraph and three check modules, and stores nothing.

## Security design

- **Authentication and authorization:** not applicable; there is no service. Anyone with
  write access to the repository can change both files. `main` has no branch protection,
  and whether it needs any before contributors arrive is question 9.
- **Input handling:** the checks read two files from the repository and nothing else.
  They make no network, subprocess or git calls and read no environment variables (C4).
  The checklist asks contributors for nothing secret, and links nothing outside the
  repository.
- **Data protection:** no personal data. Branch names carry contributors' public GitHub
  handles, and the checklist's example uses GitHub's own sample account, `octocat`.
- **Secrets:** none are introduced. The secret-detection gate, gitleaks, runs over the
  change as verification evidence.
- **Static analysis:** bandit runs on the checks directory at medium severity and above,
  as the recorded SAST gate does for `src/`.
- **Dependencies:** unchanged. The checks use the standard library only, so the
  dependency-scan gate has nothing new to audit.

## Performance and scalability

There is no runtime to load. The checklist reads in under two minutes at about 30 lines.
At ten times the stated scale, 20 to 50 contributors, both documents hold unchanged. The
part that does not scale is the maintainer's manual count of review comments, which is
question 7.

## Deployment strategy

### Where the prototype lands

The prototype's sandbox is the working tree of branch `live-proof-2026-09-21`. The
implementers write files there and commit nothing. Max Adamsky commits and opens the
pull request at handoff, through the ship skill or by hand. The handoff is a draft pull
request with test evidence in its description, which is the Prototype review's
criterion.

### The proof chain

```
unit checks (MAX-45, MAX-46)
  → per-unit verification
  → integration: setup re-run, integration check, setup check FRESH,
    plain `uv run pytest` still exits 5
  → handoff: draft pull request with this evidence
  → Build stage: engineering merges to main
  → GitHub shows the Contributing tab and sidebar link
```

There is no CI. Every step before the merge runs locally.

### Ordering constraints on the route to `main`

The route itself is question 3, which Max Adamsky owns and must settle before
2026-10-05. Whatever the route, three constraints hold:

1. **`CONTRIBUTING.md` reaches `main` together with, or after, `pyproject.toml` and
   `uv.lock`.** Otherwise item 3 tells contributors to run `uv run pytest` on a branch
   with no project to run it in.
2. **The README sentence fits whichever README it lands on.** C2's shape is a new last
   paragraph, so it holds whether `main` has its two-line README or the MAX-16 rewrite.
   Discovery wanted the sentence on `main` ahead of MAX-16, with MAX-16 rebasing onto it.
3. **The setup record on `main` matches `main`'s README.** Otherwise every kit session on
   `main` reads STALE. Whatever carries the sentence carries a matching record.

### Rollback

1. Delete `CONTRIBUTING.md`, or revert the commit that added it.
2. Remove the README's last paragraph, or revert its commit.
3. Re-run setup, so that the setup record matches the restored README.

There is nothing to restore beyond the files. A rollback takes minutes.

### Post-deployment checks

- **In prototype:** all three check modules pass, the setup check reads FRESH, and a plain
  `uv run pytest` still exits with code 5.
- **On `main`, in the Validate stage:** the repository page shows the Contributing tab
  and sidebar link, and the new-issue and new-pull-request pages link the checklist.

## Observability

- **Logs, metrics and traces:** none; these are static documents.
- **The feature's one measure** is the success count. For each outside pull request, the
  maintainer records which of items 1, 2, 4 and 5 needed a review comment. Where the count
  is kept, and when the verdict is read, is question 7, needed before the first outside
  pull request.
- **The setup check** is the health signal for the setup record, and every kit skill runs
  it first.

## Risk assessment

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| The files do not reach `main` before 2026-10-05, so the timing measure fails | Medium | High | Settle the route early; constraints 1 to 3 above apply to any route | Max Adamsky (question 3) |
| Item 3 is wrong on `main` because the toolchain files have not arrived | Medium | High | Deployment constraint 1 | Max Adamsky (question 3) |
| Contributors keep ship's branch, description and link despite the introductory sentence | Medium | Medium | The tool-neutral sentence (question 1); the count shows it per item | Max Adamsky |
| The setup re-run changes more than the setup record | Medium | Low | C3: every change is listed at integration, and anything beyond the expected is reported | The prototype orchestrator, this session |
| An interrupted session leaves the setup check STALE after the README edit | Low | Medium | The re-run happens in the same session as the edit; after an interruption, setup runs before any other kit skill | The prototype orchestrator; then Max Adamsky |
| The recorded lint, format and type-check gates cannot pass here, because `src/` and `tests/` do not exist | Certain | Low | Verification runs the same tools on the checks directory by name; `gates.md` is setup's record and is unchanged | Max Adamsky, at a later setup re-run |
| Exit code 5 later hides tests that failed to collect | Medium | Medium | Rewrite item 3 when the first test module lands | Max Adamsky (question 8) |
| Contributor pull requests carry changes to `.ai-delivery/` and `docs/decisions.md` | High | Medium | Decide whether they may | Max Adamsky (question 6) |
| A direct push to the unprotected `main` skips all five items | Low | High | Decide on protection before contributors arrive | Max Adamsky (question 9) |
| Contributions arrive with no licence covering them | Medium | Medium | Decide before the first outside pull request | Max Adamsky (question 10) |
| The checks are mistaken for enforcement on contributors | Low | Low | ADR-001 in `1a-discovery.md` states they check this feature's files only | The prototype orchestrator |

## Final sign-off

- [x] Database migration strategy: not applicable.
- [x] Security reviewed: no secrets, no personal data, no service; gitleaks and bandit
  run as evidence.
- [x] Performance targets: not applicable to static documents; the scaling limit is
  named.
- [x] Deployment plan: the sandbox, the proof chain, three ordering constraints and a
  rollback.
- [x] Observability: the success count and the setup check.
- [x] Risks identified, each with a mitigation and an owner.

Two actions come out of this document, both owned by Max Adamsky. The first is to settle
question 3, the route to `main`, before 2026-10-05, so that deployment constraints 1 to 3
can be met. The second is to decide, at a later setup re-run, whether the recorded lint,
format and type-check gates should name paths that exist.
