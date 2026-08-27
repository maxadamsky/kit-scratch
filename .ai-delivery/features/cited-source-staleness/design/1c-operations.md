# Honest source annotations: operations, release, and risk

**Feature:** cited-source-staleness
**Phase:** 1C — Production Readiness
**Date:** 2026-08-27
**Version:** 1.0
**Profile:** software (of config: software)
**Requirements:** `.ai-delivery/features/cited-source-staleness/requirements.md` v1.0 (approved 2026-08-12)
**Preceded by:** `design/1a-discovery.md`, `design/1b-contracts.md`

---

## What this document settles

This document covers what happens to the annotation grammar after it is written: how
artifacts already in other people's repositories move onto it, what the one new failure path
is allowed to say out loud, how the change actually reaches an installed plugin, and what is
being deliberately left unmeasured.

It matters because this feature's whole subject is a record that was trusted for longer than
it was true. A release plan that lets the change sit uninstalled, or a conversion that never
fires, would reproduce exactly that shape one level up — a fix that is believed to have
shipped and has not.

The standard operational sections of this phase — database migrations, authentication,
request-rate scalability, health checks, dashboards — mostly do not apply, and each is
recorded below as not-applicable with its reason rather than dropped. What replaces them is
specific: artifact conversion, one fetch-failure path, plugin distribution, and a hand audit.

---

## Conversion and backfill strategy

This feature's analogue of a data migration is Unit 4: bringing artifacts written under the
old grammar onto the new one. The mapping itself is Contract 4 in `design/1b-contracts.md`;
what follows is when it runs, in what order, and what happens when it is wrong.

### Ordering

| Step | What | Why this order |
|---|---|---|
| 1 | Unit 1 lands the grammar | Nothing can convert to a grammar that is not written |
| 2 | Unit 2 lands the emitter | Conversion runs *through* setup's diff-and-propose path, so that path must already emit the new grammar |
| 3 | Unit 4 lands the conversion | — |

**Units 2 and 4 both modify `ai-delivery/skills/setup/SKILL.md`.** Under the profile's
*Dependency rule* they therefore cannot run in the same parallel batch — this is a file
conflict, not a preference, and it is the reason Unit 4 serialises behind Unit 2 in Phase 4's
batching. The requirements' § 10 Dependencies states the same constraint.

### Rollback

There is no migration to reverse, because nothing is written without a human accepting a
diff. If a conversion is accepted and regretted, the artifact is a tracked file in the user's
own repository and `git checkout -- .ai-delivery/conventions.md` restores it. This is the
whole rollback story, and it is adequate precisely because the conversion is a text edit to a
committed file rather than a state change anywhere else.

The property that makes this true is worth stating as a constraint rather than an
observation: **the conversion must never write outside `.ai-delivery/`, and must never write
anything that is not a tracked file.** A conversion that touched an untracked or generated
location would lose its rollback path.

### The backfill gap, stated plainly

Conversion runs only when someone re-runs setup, and setup re-runs are prompted by a stack
change. **A repository whose stack does not change will never be offered the conversion**, so
its artifacts keep `verified:` indefinitely while declaring an older `schema_version`.

This is the same defect the requirements criticise in the *existing* mitigation — setup's
re-run offering re-verification past six months "fires on stack change rather than on a
schedule, so artifacts rot fastest in the repositories whose code moves least." Unit 4
inherits that trigger unchanged.

Three things make this acceptable rather than a repeat of the original failure, and the third
is the one that carries the weight:

1. The unconverted artifact is not silently misread — Unit 3's advisory names it on the next
   gate run, which is every skill run, not every stack change.
2. A `verified:` line under `schema_version: 1` is now *identifiable* as old-grammar, which is
   exactly what it was not before.
3. Nothing here claims the conversion is complete. No count, no progress claim, no "migrated"
   status — the artifact declares its own grammar and the reader decides.

**No automatic, scheduled, or forced conversion is in scope**, per the requirements' § 3. This
gap is recorded as a known limitation with the maintainer as owner, not as work.

### Not applicable

- **Database migrations, DDL, zero-downtime checklists.** No database, no schema, no service.
  The `schema_version` integer names a text grammar, not a stored one.
- **Data backfill jobs.** No data store to backfill.

---

## Security design

The requirements' § 7 sets one security constraint for this feature and it is narrow, so this
section is short and specific rather than a generic checklist.

### The trust boundary that actually exists

There is one, and it is not a network boundary: **artifact text is read as authoritative by
every later agent run.** Anything that reaches a generated artifact — or an operator message
that a person may paste into one — is instruction-shaped input to future sessions. That is the
surface worth defending here.

### FR-009's operator message, and what it may not contain

FR-009 requires setup to tell the operator which sources did not resolve. The requirements
add: the message **must not embed content derived from a fetch response.**

The rule, stated so an implementer cannot get it subtly wrong:

- Report the **requested** URL, exactly as it appeared in the source catalog or the user's
  input.
- Report the failure **class** — a transport failure, or an HTTP status code as an integer.
- Report **nothing else from the response**: not the body, not a response header, not a title,
  not an error page's text, and **not the final URL after redirects**.

The redirect clause is the one an implementer would most plausibly skip. A redirect target is
chosen by the remote host, so echoing the resolved URL hands a hostile or compromised host a
short string in the operator's terminal — and from there, plausibly, into an artifact. The
requested URL came from the kit or the user and is safe to repeat; the resolved one did not.

Shape of the message:

```
2 sources did not resolve and were recorded as unreachable:
  https://example.invalid/ops-guide — HTTP 404
  https://docs.example.com/style — connection failed
These lines carry `unreachable: <date>` instead of a source annotation. Re-run setup to retry,
or edit them by hand.
```

Nothing in that output originates from a response body.

### Retry policy

One retry before recording `unreachable:`, per FR-009. A single transient failure — a
rate-limit, a momentary DNS failure — should not permanently mark a line as unreachable in a
committed file. One retry is the requirement's number and it is not raised here: a retry loop
inside a setup run is a way to make a network partition look like a hang.

The residual risk is real and is carried in the risk register: a sustained outage during one
setup run leaves lines labelled `unreachable:` with that date. The mitigation is that the
label is honest — a fetch was attempted on that date and failed — and that a re-run offers to
retry it.

### The version reader's input surface

`schemaVersionDrift(rootValue)` takes a root and joins **fixed file names** onto it. It must
not accept, derive, or follow a caller-supplied path. `setup-runtime.js` already has
`resolveInsideRoot()` for the case where a path *is* caller-supplied — the fingerprint file
list — and the reader deliberately does not need it, because there is no path to validate.

If a later change gives the reader a path argument, it acquires a traversal surface it does
not have today. Recorded here so that change is a visible decision rather than a quiet one.

### Not applicable

- **Authentication, authorization, session handling, security headers.** No service, no
  requests, no users to authenticate.
- **Secrets management.** No credentials are read, written, or transmitted. The kit's fetch
  path is unauthenticated public documentation.
- **Input validation of user-supplied payloads.** The only inputs are files in the user's own
  repository, already trusted at the same level as their source code.
- **New outbound network paths.** None. The single existing fetch path in setup's research
  phase gains failure recording and no new capability.

---

## Performance

Not a runtime system, so the honest framing is not throughput but **what got added to a path
that already runs constantly.**

### The one path that matters

The setup gate runs at the start of every invocation of thirteen skills. Unit 3 adds to it:

| Added work | Bound |
|---|---|
| File reads | Exactly 3 — `conventions.md`, `gates.md`, `rubrics.md` |
| Regex executions | Exactly 3, one anchored match per file |
| Directory walks | **Zero** |
| Network calls | **Zero** |
| Writes | **Zero** |

Against what the gate already does — reading `config.md`, reading `rubrics.md`, and a SHA-256
over every fingerprinted file — three small text reads are not measurable. `rubrics.md` is
read twice (once by `provenanceMatches`, once by the drift reader); the duplicate read is
accepted in exchange for keeping the two functions independent, which is what keeps
`evaluateGate()`'s contract untouched.

### The performance constraints that are real

These are constraints on the implementation, not observations:

- **The reader must not glob, walk, or enumerate directories.** Three fixed names, joined onto
  the root. A directory walk in a path that runs on every skill invocation is how a fast tool
  becomes a slow one in a large repository.
- **The reader must not read a file twice** within its own execution.
- **No caching, no memoisation, no state file.** The gate is a short-lived process; a cache
  would be a central-state mechanism, which the requirements' § 7 rules out.

### Not applicable

- **Load, stress, and soak testing; scaling plans; capacity models.** No request rate to
  model. The read/write asymmetry Phase 1A identified — one write, unbounded reads — is a
  *trust* asymmetry, not a load one; the reads are humans and agents opening a file.

---

## Release and distribution

This is the section with a real, already-diagnosed failure mode, and it is the one most likely
to make the whole feature invisible.

### The failure

The kit is distributed as a plugin. `ai-delivery/.claude-plugin/plugin.json` currently declares
`"version": "1.9.0"`. **A content-only commit — which is what almost all of this feature is —
leaves that number unchanged, and an install then reports "already at the latest version."**
The change is committed, merged, and not installed anywhere.

The requirements name this as a risk and make the version bump a Definition-of-Done stage
rather than a step in a checklist. This document does not soften that.

### The release gate

| Step | Action | Fails if |
|---|---|---|
| 1 | FR-015 has run and its result is recorded | The verb was never validated |
| 2 | Every unit verified; no `verified:` in newly generated output; every kit-written line annotated | The grep criteria in FR-010 do not hold |
| 3 | `ai-delivery/tests/portability-conformance.js` passes, including assertions 11–15 | The gate contract moved |
| 4 | **Bump `version` in `ai-delivery/.claude-plugin/plugin.json`** | Installs silently do not receive the change |
| 5 | Install from the marketplace into a scratch repository and confirm the new version is what arrives | Step 4 was done but the marketplace still serves the old build |
| 6 | Record the audit date | The measurement stage has no date to fire on |

**Step 5 is not ceremony.** Step 4 changes a number in a file; step 5 is the only thing that
proves the number had the intended effect. Given that the failure mode being guarded against is
precisely "believed to have shipped, did not," verifying the belief is the point.

### Which number

A **minor** bump — 1.9.0 → 1.10.0 — is the recommendation. The reasoning: the gate's stdout
vocabulary, exit codes, and `evaluateGate()`'s return shape are unchanged, no skill's gate
stanza is edited, and old artifacts remain readable. What changes is the *generated output
format*, and that break is already signalled where it belongs — in each artifact's own
`schema_version`. The kit maintainer owns the final call.

### Rollout approach

Single-step. There is no staged rollout, no canary, and no feature flag, because there is no
running system to roll out to — a plugin version is either installed or it is not, per
repository, at the user's initiative.

**Feature flags are deliberately not used.** A flag would mean two annotation grammars alive
at once, which is the ambiguity this feature exists to remove.

### Post-release verification

In a scratch repository, on the newly installed version:

1. Run setup. Confirm by grep: zero `verified:` in the three generated artifacts, and every
   kit-written line matches `[source:`.
2. Confirm the legend is present in all three files.
3. Run any gated skill against artifacts carrying `schema_version: 1`. Confirm stdout is one
   status word, the exit code is unchanged, and the advisory appears on stderr.

### Not applicable

- **Deployment pipelines, health checks, blue-green, canaries.** Nothing is deployed to a
  running environment.
- **CI changes.** Out of scope by requirement — the requirements' § 3 excludes changes to CI.

---

## Observability

**There is none, and that is a decision rather than an omission.**

The requirements' § 7 forbids central state: these artifacts live in other people's
repositories, and there is no registry, no database, and no kit-side record. That rules out
logs, metrics, traces, dashboards, and alerting — every one of them requires somewhere to send
data, and there is nowhere to send it.

What exists instead:

| Instrument | What it tells you | Who reads it |
|---|---|---|
| The annotation itself | What grounding a line has, and as of when | Any reader of the artifact, offline |
| Unit 3's stderr advisory | That this artifact predates the current grammar | Whoever ran the command |
| FR-009's operator message | Which sources did not resolve during this run | Whoever ran setup |
| The dated hand audit | Whether readers act on annotations at all | The kit maintainer, once |

All four are read by a person or an agent at the moment they occur. None accumulates.

### The audit is the only instrument that answers the deferral

The requirements deferred the mechanical classifier "pending evidence that readers act on the
annotation at all," and the no-central-state constraint makes that evidence uncollectable
across installs. The dated hand audit is the named substitute: count lines demoted or deleted
versus re-dated across maintainer-controlled repositories. A non-zero demote-or-delete count
says readers act; zero says the annotation alone does not prompt action, which is itself the
evidence that the classifier is needed.

It sees only repositories the maintainer controls. That is a limitation of the evidence, and
it is stated rather than corrected.

**The interval is open.** Requirements Q2 asks whether six months is right, owns it to the kit
maintainer, and targets the decision at release. Six months is the proposed default. This
design does not settle it, because release is when it is decidable and release has not
happened. What this design does require is that **the date is recorded at release time** — an
audit with no date is an audit that never happens, and the risk register carries that.

---

## Risk assessment

Carried from the requirements' § 10 and the discovery risk pass, with the Phase 1B and 1C
findings added. Likelihood and impact are the design's judgment.

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | **The change ships but is not installed.** A content-only commit reports "already at the latest version" | High without the gate | Total — the feature is invisible | Release gate steps 4 and 5; step 5 verifies the bump had effect | Kit maintainer |
| R2 | **The conversion never fires.** Setup re-runs are triggered by stack change, so stable repositories keep the old grammar indefinitely | High | Medium — artifacts stay old but are now *identifiable* as old | Unit 3's advisory on every gate run; stated as a limitation, not claimed as solved | Kit maintainer |
| R3 | **The verb change is an untested bet.** No model has been shown both versions | Certain until FR-015 runs | High if wrong — the grammar's central choice | FR-015 as a merge gate; conformance assertion 22 keeps the verb substitutable | Kit maintainer |
| R4 | **A human edits an annotated line's text and leaves the annotation.** The original failure re-created inside the new grammar | Medium | High — a false record that reads as authoritative | FR-005 states the editor's obligation in the artifact's own legend and admits the heuristic. **Nothing detects a violation** — accepted, not solved | Unowned by design |
| R5 | **Transient fetch failure mislabels a line.** A rate-limit during one run leaves `unreachable:` in a committed file | Medium | Low — the label is honest, and a re-run retries | One retry; `unreachable:` keeps the state separable from `ungrounded`; the operator is told at run time | Setup operator |
| R6 | **The audit date is never recorded**, so the measurement stage silently does not happen | Medium | Medium — the classifier deferral loses its only trigger | Release gate step 6; requirements Q2 owns the interval | Kit maintainer |
| R7 | **An emitter omits an annotation**, making a kit line indistinguishable from a human's | Low | Medium — erodes the absence rule | Conformance assertion 21 greps the § 4 skeleton for unannotated bullets; the grammar admits the failure mode | Kit maintainer |
| R8 | **`1-kit` becomes the tier of convenience** for lines nobody wants to ground | Low | Medium — a new dishonesty in new vocabulary | The tier requires a path, and a path that does not resolve is visible to any reader | Kit maintainer |
| R9 | **The stderr advisory is lost** where stderr is redirected to `/dev/null` | Medium | Low — the requirement is to report, not to enforce | Accepted in Phase 1A's ADR-002 | Accepted |
| R10 | **Content drift goes undetected** — a source that still resolves but no longer supports the claim | Certain | High, and it is the assumed dominant failure mode | **None.** Out of scope by the requirements' § 3 and stated as the document's most important caveat | Unowned by design |

R10 is the one a reader should carry away. This feature fixes the record's *honesty about what
happened*; it does not, and the deferred classifier would not, detect a source whose content
moved underneath a still-live URL. The requirements state that as their single most important
caveat and this design does not improve on it.

### Risk monitoring

There is no monitoring, for the reason given above. R1, R3, and R6 are gated at release; R2,
R4, and R10 are permanently accepted; the rest are visible to whoever is at the terminal when
they occur.

---

## Definition of Done, mapped

| Stage | Done when | Where it is specified |
|---|---|---|
| Requirements | Approved 2026-08-12 | ✅ Complete |
| UX Ideation | Not applicable — not UI-facing | ✅ N/A |
| Validation gate | FR-015 has run and its result is recorded | **Open** — see Actions |
| Implementation | FR-001..FR-014 met; no `verified:` in generated output; every kit-written line annotated; `schema_version` read | `design/1b-contracts.md` Contracts 1–6 |
| Release | Plugin version bumped and the bump verified by installing | Release gate steps 4–5 above |
| Measurement | Audit date recorded at release; audit performed on it | Release gate step 6; interval open at Q2 |

---

## Open items

**The audit interval is open, and release is when it becomes decidable.** Requirements Q2 asks
whether six months is right for the audit that triggers the classifier decision. Six months is
the proposed default; the kit maintainer owns the answer and the target date is release. This
design does not pre-empt it, but it does require that the chosen date be written down at
release time.

**FR-015 has not run**, carried from `design/1b-contracts.md`. `read_on` remains provisional
in this document too. The kit maintainer owns it.

**Nothing else in this document is unsettled.**

---

## Actions this document surfaces

- **Bump `version` in `ai-delivery/.claude-plugin/plugin.json` at release, then install from
  the marketplace and confirm the new version is what arrives.** The bump alone is not
  evidence; the install is. 1.10.0 is the recommendation. The kit maintainer owns this.
- **Record the audit date at release time, and confirm or change the six-month interval**
  (requirements Q2). An audit with no recorded date does not happen, and it is the only
  instrument answering whether the deferred classifier is needed. The kit maintainer owns this.
- **Run the FR-015 validation gate before implementation begins.** Carried from Phase 1B and
  still open. The kit maintainer owns this.
- **Run `/ai-delivery:setup` in `/Users/maxdamsky/Projects/ai-delivery-kit`.** Carried from
  Phase 1A and still open. The developer responsible for that repository owns this.

---

## Next Steps

- **Phase 2 — decomposition.** Confirm the five units in `tracker.md` against the Phase 1B
  contracts, check them against the profile's *Dependency rule* — Units 2 and 4 share
  `skills/setup/SKILL.md` and cannot batch together — and create the integration unit in
  Linear with the `integration` label.
