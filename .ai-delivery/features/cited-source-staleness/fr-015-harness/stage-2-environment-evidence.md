# FR-015 Stage 2 environment evidence

**Consumer:** Stage 4 owner and run operator

**Claim markers:** Stage 2 execution facts below are verified on 2026-08-28 from the retained
transcript and explicitly marked transcript-sourced; those probes were not re-run. Current
file and reader-script facts are repo-verified 2026-08-28; other on-disk facts are verified on
2026-08-28 by read-only filesystem checks. The date-awareness section is verified on
2026-08-28 by its one newly run Stage 4 probe.

## Provenance and extraction boundary

The retained source is:

    /Users/maxdamsky/.codex/sessions/2026/08/27/rollout-2026-08-27T21-39-40-01a04605-cb3a-7621-8bee-5200a099ff39.jsonl

Its timestamps are UTC; the Stage 2 commands ran locally on 2026-08-27. For JSON-format
Claude output, each indented value below is the subject result string copied exactly from the
raw stdout object. Surrounding cost and token telemetry is not repeated because it is not
part of the isolation or independence observation. For the final isolation probe, the init
record is reproduced as an exact raw NDJSON line.

All Stage 2 temporary directories and the sentinel are gone. Transcript output ordinal 600
records exit 0 for each directory removal and absent=true for all five paths. Therefore the
isolation and no-persistence results below are available only from the transcript. The
persistence-enabled positive-control session also remains separately on disk at:

    /Users/maxdamsky/.claude/projects/-private-tmp-fr015-stage2-independence-control-daTrW5/5087d7ae-0c12-4fa1-b9f6-280b22450bec.jsonl

## Isolation — transcript-sourced, not re-run

### Repository working-directory visibility

Transcript CommandExecution/custom-output ordinals 301/302 ran from
/Users/maxdamsky/Projects/kit-scratch. Raw subject result:

    CWD=/Users/maxdamsky/Projects/kit-scratch
    FIRST_HEADING=# Requirements Document — Honest source annotations in generated artifacts

### Neutral directory and cross-invocation visibility

The first neutral-directory staging attempt at ordinals 307/308 was permission-denied and
created nothing. Its raw subject result was:

    CWD=/private/tmp/fr015-stage2-shared.stEhGc
    REPO_FILE=UNAVAILABLE
    WROTE=FAILED

    I can't report the third line as requested: the write to `prior-slot-output.txt` was blocked by the permission system, so the file was not created. `.ai-delivery/features/cited-source-staleness/requirements.md` does not exist in this directory.

    Approve the write permission and I'll create the file and return the three lines as specified.

The corrected sentinel-staging invocation at ordinals 321/322 used
--dangerously-skip-permissions only to stage the probe file. That flag is not part of the
trial configuration. Its raw subject result was:

    CWD=/private/tmp/fr015-stage2-shared.stEhGc
    REPO_FILE=UNAVAILABLE
    WROTE=CROSS_SLOT_OUTPUT_91C4E

A later ordinary invocation in that same working directory, ordinals 327/328, returned this
raw subject result:

    CROSS_SLOT_OUTPUT_91C4E

### Final isolation configuration

The final probe at ordinals 351/352 used:

    --safe-mode
    --tools ""
    --disable-slash-commands
    --strict-mcp-config
    --no-chrome
    --no-session-persistence

Its raw init NDJSON line was:

    {"type":"system","subtype":"init","cwd":"/private/tmp/fr015-stage2-shared.stEhGc","session_id":"dee37e32-61fc-4a07-83b0-9434dec4f4c3","tools":[],"mcp_servers":[],"model":"claude-opus-5[1m]","permissionMode":"default","slash_commands":[],"apiKeySource":"none","claude_code_version":"2.1.247","output_style":"default","agents":["claude","Explore","general-purpose","Plan"],"skills":[],"plugins":[{"name":"ai-delivery","path":"/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery","source":"ai-delivery@ai-delivery-kit","version":"1.9.0"}],"capabilities":["interrupt_receipt_v1","interrupt_cancel_queued_v1","msg_lifecycle_v1"],"analytics_disabled":false,"product_feedback_disabled":false,"uuid":"7fe3f3ad-4ebc-4e9b-aafb-01d7a6abc06f","messaging_socket_path":"/tmp/cc-socks/39081.sock","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required"}

With the sentinel still in the working directory, its raw subject result was:

    NO_FILESYSTEM_TOOL_AVAILABLE

The transcript-sourced observed effect is that ordinary invocations can read repository files
from a repository working directory and can read an earlier invocation's file when they share
a neutral directory. Under the final flag set, the subject received no filesystem tool, MCP
server, slash command, or skill capable of reading the adjacent sentinel. The trial runner
adds one unique empty working directory per slot.

## Independence — transcript-sourced, not re-run

### Persistence-enabled controls

The seed, explicit resume, and continuation outputs at transcript ordinals 360, 366, and 372
were exactly:

    {"exit_code":0,"session_id":"5087d7ae-0c12-4fa1-b9f6-280b22450bec","result":"CONTROL_STORED"}
    {"exit_code":0,"session_id":"5087d7ae-0c12-4fa1-b9f6-280b22450bec","result":"PERSIST_CONTROL_42B7"}
    {"exit_code":0,"session_id":"5087d7ae-0c12-4fa1-b9f6-280b22450bec","result":"PERSIST_CONTROL_42B7"}

### No-session-persistence test

The seed output at transcript ordinal 378 was exactly:

    {"exit_code":0,"session_id":"ee15dc0e-54ec-47f9-956b-ff6cae2415e3","result":"NO_PERSIST_STORED"}

Explicit resume at ordinal 384 exited 1 with exactly:

    No conversation found with session ID: ee15dc0e-54ec-47f9-956b-ff6cae2415e3

Continuation at ordinals 389/390 created session
5de62a38-666f-436e-b1bc-b39fdc0f918b, reported num_turns=1, and returned exactly:

    There's no such token — this is the first message in our conversation, and nothing earlier asked me to remember one. If you paste the token (or the message containing it), I'll hold onto it for the rest of the session.

The transcript-sourced observed effect is that the persistence-enabled controls preserved the
same session and token, while --no-session-persistence made explicit resume unavailable and
made continuation open a distinct one-turn session without the token. Trial invocations carry
neither --resume nor --continue, and the completion gate also requires distinct returned
session IDs.

## Exact pre-Stage-4 probe ledger

The repo-owned reader is transcript-ledger.js. The command run on 2026-08-28 was:

    node transcript-ledger.js /Users/maxdamsky/.codex/sessions/2026/08/27/rollout-2026-08-27T21-39-40-01a04605-cb3a-7621-8bee-5200a099ff39.jsonl

Its final raw summary was:

    {"mechanismAttempts":23,"modelBacked":21,"preModel":2,"chooserInvocations":1,"separateStage1BillingAttempts":1,"rejectedBeforeLaunch":1}

The initial Stage 2 checkpoint comprised 19 attempts: 17 model-backed and two pre-model
failures. Four later model-backed mechanism probes established the effort-reporting channel,
making the exact pre-Stage-4 mechanism total 23: 21 model-backed and two pre-model. The Stage 1
billing call is separate, so the whole-task pre-Stage-4 print-call total was 24: 22
model-backed and two pre-model. The interactive chooser is separate from those print calls.

Transcript ordinal 792 contained one additional textual claude -p command, but the execution
layer rejected the enclosing command before Claude launched. The ledger records it as
rejectedBeforeLaunch=1 and excludes it from attempt counts.

## Stage 4 date-awareness probe — newly run once

This probe ran once on 2026-08-28 after owner authorization. It contained no fixture, arm,
trial instruction, slot ID, or observations-file write and is not one of the 120 trial slots.
It used the exact 16-element trial argument prefix:

    ["-p","--output-format","stream-json","--verbose","--model","claude-sonnet-5","--effort","high","--safe-mode","--tools","","--disable-slash-commands","--strict-mcp-config","--no-chrome","--no-session-persistence","--"]

The only prompt was:

    What is the date today?

The raw assistant text and terminal result were both:

    Today is August 28, 2026.

The raw init record reported model=claude-sonnet-5, tools=[], mcp_servers=[],
slash_commands=[], and skills=[]. The process exited 0, stderr was empty, and its unique
working directory was empty before and after the invocation and then removed.

The following fields are transcript-sourced from the same raw CommandExecution ordinal 1848
and were not re-run:

    plugins=[{"name":"ai-delivery","path":"/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery","source":"ai-delivery@ai-delivery-kit","version":"1.9.0"}]
    tools=[]
    mcp_servers=[]
    slash_commands=[]
    skills=[]
    total_cost_usd=0.0080368
    modelUsage.claude-haiku-4-5-20251001.canonicalModel=claude-haiku-4-5
    modelUsage.claude-haiku-4-5-20251001.costUSD=0.0009530000000000001
    modelUsage.claude-sonnet-5.costUSD=0.0070837999999999995
    subagent_stats.spawned=0

The displayed runbook figures `0.000953` and `0.0070838` are decimal presentations of those
two raw telemetry values. The owner ruled on 2026-08-28 that the zero-tool,
zero-subagent observation explains the auxiliary Haiku use in part as Claude Code internal
overhead rather than anything reaching a fixture. Its exact role remains unverified and, in
the owner's terms, not fully established.

Immediately after this one authorized probe, the whole-task count was 25 launched print
calls: the Stage 1 billing call, 23 mechanism probes, and this date-awareness probe. Of those,
23 were model-backed and two were pre-model failures. The one interactive chooser remained
separate.

## Stage 4 audit instrumentation failure

After the date probe, a read-only grep command placed Markdown backticks around the text
claude -p inside a double-quoted shell argument. The shell interpreted those backticks as
command substitution and launched one unintended print command with no prompt. Transcript
CommandExecution ordinal 2041 records this exact output:

    Error: Input must be provided either through stdin or as a prompt argument when using --print

The command reached no model and was not a trial, but it was a launched print attempt. The
current whole-task count is therefore 26 launched print calls: 23 model-backed and three
pre-model failures, plus the separate interactive chooser. The pre-Stage-4 reconciliation
remains 23 mechanism attempts: 21 model-backed and two pre-model failures.
