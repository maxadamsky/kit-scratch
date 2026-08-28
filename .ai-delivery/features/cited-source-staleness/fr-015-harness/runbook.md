# FR-015 experimental runbook

**Consumer:** operator

**State:** Stage 5 execution was approved by the owner on 2026-08-28. Zero trial slots had
run at approval, and the owner requires the harness commit before slot 1.

**Claim markers:** Current artifact bytes and executable behavior described here are
repo-verified 2026-08-28. Owner choices and live-state reports are marked as verified on
2026-08-27 or 2026-08-28 from the owner ruling, as observed in the Stage 4 date probe, or as
unverified owner-reported UI observations. Auxiliary Haiku use is explained in part but not
fully established.

## Fixed subject condition

Every slot uses these exact pin flags:

```text
--model claude-sonnet-5 --effort high
```

The complete argument prefix, before the one prompt argument, is:

```text
-p --output-format stream-json --verbose --model claude-sonnet-5 --effort high --safe-mode --tools "" --disable-slash-commands --strict-mcp-config --no-chrome --no-session-persistence --
```

The displayed `""` denotes the one empty-string argument following `--tools`; the runner
passes an argument array directly with `shell: false`, so no shell interprets these bytes.
The normal result stream must report `claude-sonnet-5`. A loopback OTLP `api_request` event,
joined to the stream by `session.id` and `query_source=sdk`, must report both
`model=claude-sonnet-5` and `effort=high`. The observation records the exact flag pairs and
both returned values. A missing value or a value different from either pin makes the slot a
terminal failure, not a usable result. This mechanism was verified on 2026-08-27 by an actual
non-trial invocation: the normal stream returned the model, and the joined OTLP event returned
the same model and `effort=high`.

The owner selected Sonnet 5 at high effort, not the account default. The experiment asks
whether one word changes how an agent treats a stale date. A stronger model at higher effort
is more likely to reason carefully about dates regardless of the verb, compressing the
between-arm difference and risking a false negative at the population most at risk. Kit
artifacts are read by whatever Claude Code a user runs, which skews toward faster defaults
rather than Opus at xhigh. The weaker end is both the more common deployment condition and the
more sensitive instrument. This rationale is verified on 2026-08-27 from the owner ruling.

Haiku is excluded as a subject. Its effort flag was accepted, but the applied effort was not
observable, so it is not a controlled condition. Result telemetry during non-trial Opus,
Fable, and Sonnet invocations also listed auxiliary `claude-haiku-4-5-20251001` usage. The
Stage 4 date probe was a zero-tool invocation whose result reported
`subagent_stats.spawned=0`; its `total_cost_usd` was `0.0080368`, comprising `0.000953` for
`claude-haiku-4-5` and `0.0070838` for `claude-sonnet-5`. Those fields are verified on
2026-08-28 from transcript-sourced Stage 4 date-probe CommandExecution ordinal 1848. The
internal-overhead treatment, and the treatment that nothing reached a fixture, are verified
on 2026-08-28 from the owner ruling; the exact role remains unverified and, in the owner's
terms, not fully established. The owner also ruled that it is constant across arms and cannot
bias the comparison; no claim about the experiment's answer follows from it.

The Stage 4 date probe's init record reported that the subject invocation loaded the
`ai-delivery` plugin at version `1.9.0` from
`/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery`, while its safe-mode inventory carried
`skills: []`, `slash_commands: []`, `mcp_servers: []`, and `tools: []`. Those fields are
verified on 2026-08-28 from transcript-sourced CommandExecution ordinal 1848. The owner
specified as a condition of the run that every subject invocation has this same plugin load,
that the empty safe-mode surfaces make the plugin unable to act, and that its identical
presence across arms cannot bias the comparison. This records a run condition, not a
pre-trial observation of all 120 invocations and not a change to the design.

## Transport, isolation, and independence

Prompt transport was verified on 2026-08-27 by attempted invocations. Passing a positional
prompt beginning with the fixture's YAML `---` without a separator produced option parsing;
placing `--` before the prompt worked and delivered fixture-then-instruction as one user
prompt. Every slot therefore passes exactly one prompt argument after `--`: fixture bytes,
one additional LF after the fixture's final LF, then the fixed instruction bytes.

Working-directory visibility was also verified by observed effect. From the repository, an
ordinary later `claude -p` invocation could report a sentinel written by an earlier
invocation. Under the fixed isolation flags from a neutral directory, the init event returned
`tools: []`, `mcp_servers: []`, `slash_commands: []`, and `skills: []`, and the subject could
not report the same-directory sentinel. Each trial adds a second boundary: the runner creates
one unique empty temporary working directory, buffers stdout and stderr in the parent, writes
the observation outside the temporary directory, asserts that the directory is still empty
afterward, and removes it. No slot directory contains any arm, trial-type, trial-number, or
slot output.

Session independence was verified on 2026-08-27. A persistent seed could be recovered by both
resume and continuation. A seed made with `--no-session-persistence` could not be resumed, and
continuation opened a new one-turn session that did not carry the seed secret. Trial arguments
contain no session ID, resume flag, or continuation flag. Every returned session ID must also
be unique across the 120 observations.

The raw isolation and independence outputs are preserved in
`stage-2-environment-evidence.md`. They are marked transcript-sourced and were not re-run for
Stage 4 review. The cross-slot confound probe must not be re-run in the repository.

The executed ledger contains exactly 23 pre-Stage-4 mechanism `claude -p` attempts: the
initial Stage 2 checkpoint had 19 (17 model-backed and two pre-model failures), and four later
model-backed probes established the per-invocation effort-reporting channel. The Stage 1
billing call is separate, making 24 launched print calls before Stage 4, and one interactive
model chooser is separate from those. A command containing one more textual `claude -p` was
rejected by the execution layer before launch and is not an attempt. `transcript-ledger.js`
reproduces those counts from the retained transcript.

One owner-authorized Stage 4 date-awareness probe then used the exact trial argument prefix
and the sole prompt `What is the date today?`. It returned exactly `Today is August 28, 2026.`
The invocation contained no fixture, arm, trial instruction, slot ID, or observation write.
It is a model-backed non-trial probe. Immediately afterward, the whole-task print-call count
was 25: one Stage 1 billing call, 23 mechanism probes, and one date-awareness probe, of which
23 were model-backed and two failed before a model.

A later read-only grep command contained Markdown backticks inside a double-quoted shell
argument. Shell command substitution unintentionally launched `claude -p` without a prompt;
it returned `Input must be provided either through stdin or as a prompt argument when using
--print` before inference. It was not a trial or model-backed call, but it is counted. The
current total is therefore 26 launched print calls: 23 model-backed and three pre-model
failures. The chooser remains separate. No probe counts among the 120 slots.

## Fixture facts

The source is `.ai-delivery/conventions.md` at the pre-harness source-base commit
`6d4220647e6fccd2b3d6fd63179012a53ac69be3` and MD5
`62de1a25fbf1e3896645278f1d2609cc`. These values and the initially clean tree were
repo-verified on 2026-08-27 before construction. `generator.js` fails if the source digest
moves. The source-base commit remains provenance after the harness commit; no executable
requires the repository's current HEAD to equal it.

Arms A–D use `verified:`, `read_on:`, `accessed:`, and `retrieved:` respectively. The
slot-three tokens outside Contract 1's enumeration are deliberate; "correcting" them would
destroy the experiment. The four fixtures differ only at those 28 slot-three token
occurrences, as established by Gate 2.

There are 41 identified rows per fixture:

- 14 old-grounded;
- 14 recent-grounded;
- 5 never-grounded controls;
- 4 `unreachable:` controls; and
- 4 human-authored controls.

The zero-based family index is forced by the handoff's statement that C15 becomes a control.
The literal control cycle would put `unreachable:` on ineligible tiers, so the arm-invariant
cursor resolution swaps C15 with C18 and C24 with C27. The old-date cursor is shared by
old-grounded and unreachable rows in file order; the recent cursor advances only on recent
rows. These choices apply identically to every arm.

The digest-pinned base contains four irregular `source:` occurrences across three strings:
C15 `model knowledge`, C37 `kit design`, and C40/C41
`Linear list_issue_labels for team CDR`. Each fixture deliberately preserves C37, C40, and
C41: three occurrences across two strings. C15 is one of the synthetic human-authored
controls.

Never-grounded, human-authored, and `unreachable:` rows are synthesized because the base has
one, none, and none respectively and three of four piles would otherwise be near-empty.

## Trial instructions and schedule

The four pile names and wording are exactly:

1. Still-grounded — the grounding behind this line is live.
2. Expired — it was grounded, and that grounding is no longer current.
3. Never-grounded — the kit asserted this with no external source (tier-3 lines,
   scaffold-default thresholds).
4. Human-authored — a person asserted this themselves: no source, no tier, no date.

`instructions/runner-pile-sort.json` carries the 557-byte prompt payload, independently pinned
in `runner.js` to SHA-256
`53f52c4e3d9f6d89070977c212259f4d431ddeb02c99d2d659c4377dd90da2f8`.
`instructions/runner-action.json` carries the 270-byte prompt payload, independently pinned to
SHA-256 `ffc9b4fead4bfe5dec63cc97e84ceaa9fe733e7a7978a182bf1af20bc206f24e`.
The metadata in each file names `runner.js` as consumer but is not sent to the subject. The
runner checks each payload against both its internal declaration and the independent
byte-count/digest pins, then scans it against the frozen arm-token/synonym list. Its self-test
changes one payload byte, updates the internal digest, and proves that the independent pin
still rejects the copy.

The schedule is pile-sort trials 1–20, each round-robin A, B, C, D, followed by action trials
1–10 in the same arm order: 80 pile-sort slots, then 40 action slots, 120 total. There are no
automatic retries. A timeout, interruption, parse failure, nonzero process result, missing
telemetry, pin mismatch, nonempty slot directory, or duplicate session ID becomes that
logical slot's terminal result; the remaining slots continue. The timeout is ten minutes per
slot and is identical across arms.

## Usage-credit readings

Usage credits remain enabled by owner ruling. If the five-hour session limit or weekly limit
is reached, the remaining sequence continues at API rates instead of halting. The owner
accepted that billing risk to avoid stopping a 120-slot sequence partway.

The following are unverified owner-reported Settings > Usage UI observations made on
2026-08-27 immediately after the billing probe:

- usage credits spent this period: $69.40;
- current credit balance: $51.47;
- monthly spend limit: $100.00;
- credit period resets: Sep 1;
- current session window: 5% used; and
- weekly all-models limit: 8% used.

The probe was only a few tokens and its movement could not be separated from other activity
in the same window. Do not record that meter reading as confirmation that the probe drew on
the subscription.

Immediately before slot 1, the operator reads Settings > Usage and records the current
credits-spent and balance values with `runner.js record-usage before`. Immediately after the
final logical slot reaches a terminal state, the operator records both again with
`runner.js record-usage after`. Any movement in either figure is recorded in
`observations.json` with both readings as this finding: some portion of the run was billed at
API rates rather than drawn from the subscription. State no argument from that observation.

## Operator sequence

During Stage 4, only non-executing commands are permitted:

```text
node generator.js --self-test
node generator.js --determinism
node generator.js --gate-2
node build-answer-key.js --check
node runner.js plan
node runner.js validate
node runner.js self-test
node completion-gate.js self-test
node scorer.js self-test
```

The owner-authorized Stage 4 additions are complete: `transcript-ledger.js` read the retained
session transcript, and one non-trial date-awareness subject probe ran. The owner approved
Stage 5 execution on 2026-08-28.

After explicit Stage-5 approval:

1. Re-run the nine non-executing commands above from this directory.
2. In Settings > Usage, obtain fresh credits-spent and current-balance figures. Pass them as
   the final two numeric arguments to `node runner.js record-usage before`.
3. Run `node runner.js execute --stage-5-approved` once. Do not interrupt it intentionally.
4. Immediately after it returns, obtain the two figures again and pass them to
   `node runner.js record-usage after`.
5. Run `node completion-gate.js check`. It throws on the first slot without a successful,
   parse-valid, pin-matching result.
6. Only if the completion gate passes, run `node scorer.js measure` and preserve its output
   as the raw measurement result. Do not run `node scorer.js score`: that command applies the
   decision rule, and the owner reserved the verdict.

`generator.js` produces `fixtures/runner-arm-a.md`, `fixtures/runner-arm-b.md`,
`fixtures/runner-arm-c.md`, and `fixtures/runner-arm-d.md`.
`build-answer-key.js` produces `answer-key.json` for `runner.js` and `scorer.js`. `runner.js`
consumes the answer key, fixtures, and both instruction files and updates `observations.json`. `completion-gate.js`
consumes the observations before `scorer.js` consumes the observations and answer key.
`transcript-ledger.js` reads the retained Codex transcript for the Stage 4 owner, and
`stage-2-environment-evidence.md` preserves its count plus the transcript-sourced isolation
and independence outputs for the owner and run operator.

## Frozen scoring order

The scorer applies these tests in order:

Inclusive and strict boundaries are evaluated as integer counts over their fixed
denominators, not by comparing accumulated binary floating-point means: 18/180 for the
0.10 invariance limit, 56/280 for the 0.20 recent floor, common-denominator counts for
recent-below-old and strict non-overlap, and 14/280 for the inclusive 0.05 winner band.

1. The range of arm means for the pooled misclassification rate over five Never-grounded and
   four Human-authored keyed rows must be at most 0.10. A larger range makes the run invalid.
2. Each arm's mean recent-grounded Expired rate must be at most 0.20 and below its own mean
   old-grounded Expired rate. All four failing is decisive against the feature; one to three
   failing makes the run invalid.
3. Candidate B, C, or D passes only if its minimum per-trial old-grounded Expired rate is
   strictly greater than A's maximum.
4. Among passing candidates, every arm within 0.05 inclusive of the highest passing mean is
   reported. More than one escalates and selects none. No passing candidate means FR-015
   fails and the verb is reconsidered before FR-001 merges.

Action results gate nothing. The scorer reports per-arm USE-rate aggregates and one Pearson
correlation across the four arm-level pairs only; it makes no line-level association.

## Residuals

piles 1 and 2 have no objective key, so the primary measure is a rate and not an accuracy, and only piles 3 and 4 have ground truth; there is no within-trial pairing between the two measures; the base carries four irregular `source:` occurrences, identical across arms.
