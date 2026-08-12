## Council Response

**Evidence consulted:** none — reasoning from framing only

**Stated assumptions** (the framing does not settle these): 100x is read as ~4,000 annotated lines per project and/or thousands of projects sharing one curated source catalog, versus the ~40 URLs the framing implies; sources are fetched over HTTP by the human-triggered pass; artifacts live in git.

### Failure Modes

**Failure mode 1: Throttled fetches read as dead sources**
- **Trigger:** The human-triggered re-verification pass runs over thousands of lines, most citing a handful of vendor documentation hosts, from one IP with whatever concurrency the runtime defaults to.
- **Mechanism:** The host rate-limits. Responses come back as 429, 403, a bot-challenge page served with status 200, or a connection timeout. A checker written against the framing's motivating case — the 404 — has one dead/alive axis and folds every non-200 (and every 200 whose body is a challenge) into "dead."
- **Consequence:** Mass wrongful expiry. Because the framing's expected response to an expired line is demotion or deletion, the throttle converts into humans stripping grounding from lines whose sources are alive and unchanged. The artifact becomes less honest as a direct result of running the honesty pass, and the success metric (non-zero demotions) is satisfied by an artifact of the network, not of judgement.
- **Likelihood:** High
- **Impact:** High

**Failure mode 2: The source URL is attacker-controlled input to the only networked step**
- **Trigger:** Hand editing is invited, files live in repositories that take contributions, and the re-verification pass is the one component that makes outbound requests — from a maintainer's machine, on a corporate network, with ambient credentials.
- **Mechanism:** A line is added or edited with a source URL pointing at internal or metadata addresses, `file://`, or a public URL that 302-redirects inward. The pass fetches it. Separately, if the pass records anything derived from the response — a title, a snippet, a reason string — attacker-controlled bytes land inside the artifact that every subsequent agent run reads as authoritative team convention, unbounded in read count.
- **Consequence:** The conventions file is a request-forgery trigger and a durable instruction-injection channel aimed at every future agent run. The write happens once; the reads never stop.
- **Likelihood:** Medium
- **Impact:** High

**Failure mode 3: Malformed annotations that fail open**
- **Trigger:** 100x lines means every hand-editing pathology appears somewhere: truncated annotations, `verified: 9999-99-99`, `+275760-09-13`, unicode-lookalike digits, a byte-order mark, mixed line endings, a 200KB single line, a date field present but empty.
- **Mechanism:** Date parsing yields NaN or a far-future value; the comparison against now is false; the line classifies as still-grounded. A permissive annotation regex on a huge line backtracks catastrophically and the offline check — which runs on every tool run, the unbounded side of the asymmetry — hangs or taxes each run.
- **Consequence:** Directly violates the framing's own must-not: a check that cannot fail. The garbage lines are precisely the ones most likely to be wrong, and they are the ones certified clean. The reader's four piles silently absorb bad lines into "still-grounded."
- **Likelihood:** High
- **Impact:** High

**Failure mode 4: Synchronized expiry cliff**
- **Trigger:** Every line is written in one setup run, so every line carries the same verified date and the same shelf life. At 4,000 lines, one day flips all of them.
- **Mechanism:** Expiry is a step function, not a distribution — and it is correlated across every project set up in the same period. Triage is per-line human judgement and does not scale with line count.
- **Consequence:** The file returns to being a single all-or-nothing trust object, now labelled expired instead of unlabelled. Agent-side, a review run emits thousands of expiry notices in its own output; volume alone makes the notice unreadable, which is the half the framing says matters more.
- **Likelihood:** High
- **Impact:** High

**Failure mode 5: Verified dates laundered through merges**
- **Trigger:** Two branches, or a pass running while someone hand-edits. The pass rewrites the date on every line it checked, so a run touches thousands of lines in one commit.
- **Mechanism:** Line-level conflicts across the whole file. Resolution is done wholesale — take-ours or take-theirs — because per-line review of 4,000 mechanical changes does not happen. A freshly stamped date from one side lands beside claim text from the other.
- **Consequence:** A line asserts verification of text nothing ever verified. This is the exact dishonest act the framing forbids, reached through version control rather than through code, and with no central state there is nothing outside the artifact that could contradict it.
- **Likelihood:** Medium
- **Impact:** High

**Failure mode 6: Two grammars inside one file**
- **Trigger:** The grammar changes, as the framing anticipates. At 100x, partial hand migration is certain: someone converts the lines they touched and leaves the rest.
- **Mechanism:** The version marker is per-file, but the state is per-line. The parser reads the whole file under the declared version and confidently misreads the minority-grammar lines — most dangerously by reading an old-grammar date field as absent, or a new-grammar field under old rules.
- **Consequence:** Silent misreading, which the framing forbids explicitly. Lines move between the reader's piles for no reason the reader can see from inside the file.
- **Likelihood:** Medium
- **Impact:** Medium

## Strongest Statement

The mechanism's failures under load are not slowdowns; they are lies in the artifact, and they run in both directions — throttled fetches expire live sources, malformed dates certify garbage as grounded, and merge resolution stamps fresh dates onto unverified text. Any direction chosen must treat unreachable as a third state distinct from dead and from alive, must fail closed on unparseable annotations rather than defaulting them to fine, and must not let one pass rewrite dates on thousands of lines in one commit. The chosen direction's designer owns closing all three before anything ships.

**END OF RESPONSE. Do not add anything after this line.**
