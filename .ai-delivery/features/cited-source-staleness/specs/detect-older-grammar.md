# Code Spec: Detect artifacts written under an older grammar

**Unit:** CDR-12 — Detect artifacts written under an older grammar
**Design Reference:** `design/1b-contracts.md` Contract 5 and ADR-004; `design/1c-operations.md` § Performance
**Date:** 2026-08-27
**Target repository:** `/Users/maxdamsky/Projects/ai-delivery-kit`

## Implementation Summary

- **Files to Create:** 0
- **Files to Modify:** 2
- **Assertions to Add:** 15 (numbers 1–15 in `design/1b-contracts.md` § Testing strategy)
- **Estimated Complexity:** S

This is the feature's only executable unit. It is small, and it sits next to a contract that
thirteen skills and a shipped test depend on — so the spec is tighter than its size suggests.

## Codebase Conventions

Read from `ai-delivery/scripts/setup-runtime.js` on 2026-08-27.

**File/Function Naming:** `'use strict'` at the top; module constants `SCREAMING_SNAKE_CASE`;
functions lowerCamelCase, declared as `function name(...)` at module scope, never arrow
constants.
**Import Order:** Node built-ins only, alphabetical (`crypto`, `fs`, `path`). **Zero runtime
dependencies** — do not add one, and do not reach for a YAML parser.
**Error Handling:** failure is a return value, never an exception. `provenanceMatches()` wraps
its read in `try`/`catch` and returns `false`; `fingerprintIsFresh()` returns `false` for a
malformed digest, a missing file, or a path escaping the root. Errors surface only from
`main()`, which writes to stderr and sets `process.exitCode = 1`.
**Module shape:** named exports in one object literal at the bottom; `require.main === module`
guard above it.
**Verification Framework:** `node:assert` in `ai-delivery/tests/portability-conformance.js`,
run directly with `node`. Scratch directories via `fs.mkdtempSync`, with the file's own
`scratch()` / `removeScratch()` / `write()` helpers.

## Technical Context

**Key Gotchas — read all four before writing anything**

1. **`evaluateGate()`'s return object is frozen.** Nine cases assert it with
   `assert.deepStrictEqual(evaluateGate(root), { status, exitCode })`. A third key fails all
   nine. The drift check therefore lives in `main()`, not in `evaluateGate()`.
2. **stdout is a contract; stderr is not.** `runGateClassProof()` asserts
   `result.stdout.trim()` equals the status word across all thirteen skills' gate commands and
   asserts their exit codes. It asserts nothing about stderr. That asymmetry is the entire
   reason this design works.
3. **CRLF is already exercised.** Existing fixtures write `\r\n` config files. The version
   regex needs `\r?` before the line end, and it is not defensive padding.
4. **`rubrics.md` gets read twice** per gate run — once by `provenanceMatches()`, once here.
   Accepted deliberately, to keep the two functions independent. Do not "optimise" it by
   threading a shared read through `evaluateGate()`; that is how the frozen return shape gets
   broken.

**Reusable Utilities:** `provenanceMatches()` (`setup-runtime.js:44`) is the shape to copy —
read, `try`/`catch`, return a value. `resolveInsideRoot()` is **not** needed and must not be
used: this unit joins fixed file names, so there is no caller-supplied path to validate.

**Integration Points:** `main()`'s `gate` branch only. No skill's gate stanza changes; no other
subcommand calls this.

## Contracts

**Component:** the schema-version drift reader in `ai-delivery/scripts/setup-runtime.js`.

| Operation | Purpose | Inputs | Output | Errors |
|---|---|---|---|---|
| `schemaVersionDrift` | Report which generated artifacts declare a grammar version other than the current one | `rootValue` — the same root string `evaluateGate` takes | An array of entries, one per artifact whose declared version differs from the current one, each naming the artifact, the declared version, and the current version. Empty array when everything matches, when nothing is readable, and in every failure case | **None.** Never throws |

**Data shape — the version map:** a module-level constant associating each annotated artifact
with its current grammar version — `conventions.md` 2, `gates.md` 2, `rubrics.md` 3.
`config.md` is deliberately absent: it carries values, not source annotations, so this grammar
change does not touch it and bumping it would assert a change that did not happen.

**Data shape — a drift entry:** the artifact's file name, the version it declares, and the
version current for it. An entry whose declared version is *above* current is distinguished
from one below, because "predates the grammar" is false for the former.

**Failure conditions, each named once:**
- *Absent or unparseable version line* → no entry. ADR-004. Every real artifact carries the
  key; absence means the file is not a generated artifact, and the absent-key migration signal
  is already owned by § 8's provenance check. Reporting it would fire on the conformance
  suite's own four-line `rubrics.md` stub.
- *Unreadable file* → no entry, no throw.
- *Missing `.ai-delivery/` directory* → empty array, with no special-casing needed.

**State/side effects:** one write to `process.stderr` from the call site when the array is
non-empty. **`process.stdout` and `process.exitCode` are byte-for-byte unchanged for every
input** — that is the invariant, and assertion 13 proves it by comparing two live spawns
rather than by inspecting the code.

**How it reads:** one anchored regex per file over the file's text — the declared version
captured as digits, anchored to a whole line, tolerant of a trailing carriage return. No
frontmatter parser, no multi-line state, no directory walk.

**Deviation from `provenanceMatches()`, recorded because it is one.** That function tests
exact full-line membership, which cannot distinguish "older than current" from "newer than
current" — a file at version 3 read by a kit expecting 2 would be reported as predating the
grammar, which is false. Reporting needs the declared number, so this reader captures it.
Everything else about the shape is preserved.

## Pre-Implementation Assertions

**Pattern file:** `ai-delivery/tests/portability-conformance.js`, `runStage1SemanticCases()`
(lines 89–140). Imitate: the `runCase(++number, 'name', root => {...})` structure, the
`configured(root)` / `write(root, path, content)` fixture helpers, `assert.deepStrictEqual`
for return values, and the scratch-directory lifecycle. For the spawn-based cases, imitate
`runGateCommand()` and the `gateCommand(skill)` helper at lines 205–246.

**Cases — reader behaviour**
- Empty root, no `.ai-delivery/` → empty array
- All three artifacts at current versions → empty array
- `conventions.md` at 1 → one entry naming it, 1, and 2
- `conventions.md` at 1 and `gates.md` at 1 → two entries
- `rubrics.md` at 4 → one entry marked as ahead of current, not as predating
- Artifact with no version line → empty array
- Artifact with a non-numeric version value → empty array, no throw
- Artifact that cannot be read → empty array, no throw
- CRLF artifact at version 1 → drift reported
- `config.md` at any version → never an entry

**Cases — contract preservation (the load-bearing ones)**
- The nine existing `deepStrictEqual(evaluateGate(...))` cases pass **unmodified**
- `runGateClassProof()` passes unmodified, 11 blocking / 2 advisory
- Spawn `gate` twice against the same root, once with drifting artifacts and once without:
  stdout byte-identical, exit code identical
- The drifting spawn's stderr is exactly one line and starts with the advisory prefix
- The non-drifting spawn's stderr is empty

**Integration scenarios**

| Scenario | Steps | Expected outcome |
|---|---|---|
| Old artifacts, blocking skill | 1. Set up a root at schema 1 with a stale fingerprint 2. Run a blocking skill's gate command | stdout `STALE`, exit 2, one advisory line on stderr |
| Old artifacts, advisory skill | Same root, run `convert`'s gate command | stdout `STALE`, exit 0, one advisory line on stderr |
| Current artifacts | Fresh root at current versions | stdout `FRESH`, exit 0, empty stderr |
| No config at all | Empty root | stdout `MISSING`, exit 2, empty stderr — no `.ai-delivery/` to read |

## Task Breakdown

### Task 1: Add the assertions (test-first)

**Dependencies:** None
**Files:** `ai-delivery/tests/portability-conformance.js` (modify)
**Pattern:** `runStage1SemanticCases()` and `runGateClassProof()`

Write all fifteen cases above before any change to `setup-runtime.js`. The reader-behaviour
cases fail; the four contract-preservation cases must **pass immediately** — they assert the
current behaviour, and if any fails before implementation, the baseline is not what this spec
assumes and the discrepancy is a stop.

### Task 2: Add the version map and the reader

**Dependencies:** Task 1
**Files:** `ai-delivery/scripts/setup-runtime.js` (modify)
**Pattern:** `provenanceMatches()` at line 44

Place the constant with the other module constants at the top, and the function near
`provenanceMatches()` rather than at the end of the file — it belongs with the other artifact
readers, not with the CLI plumbing.

### Task 3: Export it

**Dependencies:** Task 2
**Files:** `ai-delivery/scripts/setup-runtime.js` (modify)

Add one key to the existing `module.exports` object literal. Additive only — the test file
imports by destructuring, so nothing existing breaks.

### Task 4: Wire the call site

**Dependencies:** Tasks 2, 3
**Files:** `ai-delivery/scripts/setup-runtime.js` (modify)

In `main()`, in the `gate` branch only: after `process.stdout.write(result.status + '\n')` and
before `process.exitCode` is set, call the reader and, when the array is non-empty, write one
line to stderr.

**The line's shape** — one line total regardless of how many artifacts drifted, listing each
with its declared and current version, prefixed so it is distinguishable from a genuine error,
and naming where the grammar is defined. `design/1b-contracts.md` § The advisory line carries
the exact form.

The existing error prefix in this file is `ai-delivery setup runtime: `; the advisory extends
it rather than inventing a second vocabulary.

**Do not** wrap the call in a way that could throw past `main()`'s handler — the reader already
returns `[]` on every failure, so no additional guard is needed and adding one would hide a
real bug.

## Task Dependency Graph

```
Task 1 (assertions, test-first)
   └─→ Task 2 (map + reader) ──→ Task 3 (export) ──┐
                                                    └─→ Task 4 (call site)
```

## Pattern References

**Reader pattern:** `ai-delivery/scripts/setup-runtime.js:44` `provenanceMatches()` — imitate
the read-inside-try, return-a-value-on-failure shape and the single-line-match discipline.

**Assertion pattern:** `ai-delivery/tests/portability-conformance.js:89–140` and `205–246` —
imitate `runCase`, the fixture helpers, and the spawn-based gate proof.

## Implementation Notes

**Performance.** This runs on every invocation of thirteen skills. Hard limits: exactly three
file reads, exactly three regex executions, **zero** directory walks, **zero** network calls,
**zero** writes, and no file read twice within one execution. No caching or memoisation — the
gate is a short-lived process, and a cache would be central state, which the requirements' § 7
rules out.

**Security.** The reader takes a root and joins **fixed file names** onto it. It must not
accept, derive, or follow a caller-supplied path. `resolveInsideRoot()` exists in this file for
the case where a path *is* caller-supplied — the fingerprint list — and is deliberately not
used here because there is no path to validate. Giving this reader a path argument later would
hand it a traversal surface it does not have today; that would be a decision, not a refactor.

**Deployment.** No version bump for this unit alone; the bump is the integration unit's.

**Post-implementation verification.** Run the full conformance suite and confirm the nine
`deepStrictEqual` cases and `runGateClassProof()` were not edited. If either needed a change,
the invariant was broken and the change is wrong.

## Final Verification

**Functionality**
- [ ] All ten acceptance criteria in the skeleton met
- [ ] An artifact ahead of current is reported as newer, never as predating

**Quality**
- [ ] Zero new dependencies; Node built-ins only
- [ ] Failure returned as a value everywhere; the function cannot throw
- [ ] No directory walk, no glob, no second read of any file

**Contract preservation**
- [ ] `evaluateGate()`'s return object unchanged — nine cases pass unmodified
- [ ] `runGateClassProof()` passes unmodified, 11 blocking / 2 advisory
- [ ] stdout and exit code byte-identical with and without drifting artifacts (assertion 13)
- [ ] No skill's gate stanza edited

**Testing**
- [ ] Assertions 1–15 added and passing
- [ ] Full conformance suite passes
