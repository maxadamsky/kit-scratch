## Council Response

**Evidence consulted:** `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/hooks/hooks.json`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/hooks/path-guard.js`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/scripts/setup-runtime.js`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/scripts/legibility-check.js`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/tests/portability-conformance.js`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/SKILL.md` (§ Re-runs and staleness), `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/artifact-schemas.md` §1, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/source-catalog.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/CLAUDE.md` (§ Testing the plugin), `/Users/maxdamsky/Projects/ai-delivery-kit/.claude-plugin/marketplace.json`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/.claude-plugin/plugin.json`, `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/{config.md,gates.md,conventions.md,stack-fingerprint}`, `/Users/maxdamsky/Projects/kit-scratch/.claude/settings.local.json`. **No `.github/` exists in either tree; `ci_system: null` in config.md. There is no CI, no deploy pipeline, no log file, no alerting, and no telemetry anywhere in this repository.** The only automatic execution is two PreToolUse hooks plus one SessionStart hook.

### Scenarios

**Scenario 1: The expiry verdict is wired into the shared preflight gate, and every skill stops**
- **Detection:** Immediate and loud, but uninformative. Thirteen skills open with `setup-runtime.js gate --root "." --policy blocking` (`skills/build/SKILL.md:23`, `verify:24`, `discover:23`, and ten more); `evaluateGate` returns `exitCode: 2` for anything not `FRESH` and `main()` prints one word to stdout.
- **Diagnosis at 3am:** One word. `STALE` does not say which line, which URL, or which check produced it — no reason string, no per-entry output, no file written. The user must read `setup-runtime.js` to learn that `STALE` covers four disjoint causes (missing fingerprint, profile-provenance mismatch, changed hashes, and now expiry).
- **Recovery:** Re-run setup — which is a conversational interview, not a command. There is no `--policy advisory` escape at the call site; the policy is hard-coded per skill in SKILL.md, so a user cannot downgrade without editing plugin files inside the install cache.
- **On-call cost:** Total loss of the kit in that repo until a human completes a setup interview, from a signal that names nothing.

**Scenario 2: The re-verification pass crashes or half-writes `conventions.md`**
- **Detection:** Silent. Nothing validates the artifact after a write; `evaluateGate` never hashes setup's own outputs (`artifact-schemas.md`: "Setup's own outputs are never fingerprinted").
- **Diagnosis at 3am:** The pass leaves no run record. `docs/decisions.md` and the per-feature `qa-log.md` are the only narrative artifacts and neither is written by a checker. Nothing distinguishes "annotation absent because the pass dropped it" from "absent because a human wrote the line" — which is exactly the fourth pile the framing demands.
- **Recovery:** `git checkout` only, and `auto_push: off` means the last good copy may be uncommitted. Repair by agent is blocked: H5 in `path-guard.js:275` denies any subagent Write/Edit to `conventions.md`. Setup's own re-run diff-and-proposes against the corrupted file, so the damage becomes the standing baseline it proposes from.
- **On-call cost:** Manual, line-by-line reconstruction of a 200-line file with no reference copy.

**Scenario 3: The fix ships and is not installed**
- **Detection:** None. `CLAUDE.md` § Testing the plugin: `claude plugin update` on a local marketplace compares `plugin.json` versions, so a content-only commit "reports 'already at the latest version' — a false success… the only one that reports success while doing nothing."
- **Diagnosis at 3am:** No version is stamped into the artifacts by the mechanism. `schema_version: 1` in `kit-scratch/.ai-delivery/conventions.md` is written by setup and, per the framing, read by nothing. There is no way to ask an install which kit version produced its annotations.
- **Recovery:** Bump `ai-delivery/.claude-plugin/plugin.json` (currently `1.7.0`) and re-update every install by hand. There is no install registry.
- **On-call cost:** Hours spent debugging a checker that was never running.

**Scenario 4: The checker throws inside the hook path**
- **Detection:** Loud and total, if it lives in `path-guard.js`: the outer catch at line 348 denies with exit 2 on any internal error, by design. Every `Write` and `Edit` in every kit-rooted repo fails.
- **Diagnosis at 3am:** A stderr string. `casePolicyForPath` already throws on undeterminable filesystems; a second throwing subsystem is indistinguishable from the first in the message the user sees.
- **Recovery:** Only by removing the hook from the plugin cache or deleting `.ai-delivery/config.md` to escape the scope guard (`findKitRoot`, line 476). Both are surgery on a cache directory.
- **On-call cost:** The user cannot edit files at all, including the file they would edit to fix it. Note also the inverse: if node is absent the hook fails *open* silently (header lines 15–19).

**Scenario 5: The check works on macOS and misbehaves on Windows**
- **Detection:** Nothing runs `tests/portability-conformance.js` — no CI invokes it, and it is not referenced by any hook or skill preflight. It runs when a human remembers.
- **Diagnosis at 3am:** No platform is recorded in any artifact. `config.md` records `hook_runtime: v22.22.1` and nothing else about the machine.
- **Recovery:** None available to the reporter; the maintainer has no Windows box in evidence.
- **On-call cost:** An install where annotations silently stop expiring, which reads exactly like an install where nothing is stale.

**Scenario 6: Forty lines expire at once and nobody can triage them from the file**
- **Detection:** By definition working; the failure is the flood.
- **Diagnosis at 3am:** No prioritisation signal exists in the artifact. `gates.md` `## Threshold Provenance` is the only place the kit groups by grounding, and it is hand-maintained prose. A reader cannot sort `3-model` (never grounded, cannot expire) from `1-docs` without reading every bracket by eye.
- **Recovery:** Re-date everything — the exact rubber-stamp the framing names as the failure signal, and the only move that is cheap.
- **On-call cost:** Low per incident, fatal to the mechanism.

## First-Night Page

Scenario 1. Expiry is a status, and this repository has exactly one status channel: `setup-runtime.js gate`, whose entire vocabulary is `FRESH`/`STALE`/`MISSING` and whose failure mode is exit 2 into thirteen blocking skill preflights. If expiry reaches that gate, the first night is every install losing every skill over a six-month-old date, diagnosed from one word, with recovery only through a conversational setup interview.

## Strongest Statement

This system has no CI, no logs, no alerts, and no rollback except the user's own git — the artifact is the only channel, so whatever the mechanism knows it must say *in the file*, per line, in plain words. Any design that routes an expiry verdict into `evaluateGate` or into `path-guard.js` converts a trust problem into an outage with a one-word error message. Give the pass its own dated, human-readable run record inside the artifact — what was checked, what was unreachable, what was never grounded — because without it, "expired" and "never checked" are the same string at 3am.

**END OF RESPONSE. Do not add anything after this line.**
