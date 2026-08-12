## Council Response

**Evidence consulted:** `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/conventions.md`, `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/rubrics.md`, `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/gates.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/artifact-schemas.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/source-catalog.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/SKILL.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/scripts/setup-runtime.js`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/critique/SKILL.md`, `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/rubric-generation.md`

### Direction 1: Grammar-only — expiry on grounded lines, `verified:` deleted from ungrounded ones

**Approach Summary**
Change only the annotation grammar defined in `artifact-schemas.md` §1 and the skeletons in §3/§4/§5, plus the About-This-File prose the generated files already carry. Three edits. (a) Grounded tiers `1-docs` and `2-context7` gain one field: `[source: … · tier: 1-docs · verified: 2026-08-12 · expires: 2027-08-12]` — an explicit certificate expiry, evaluated by comparing to today's date, needing no network, no catalog and no kit internals. (b) `3-model` lines and scaffold-default thresholds stop carrying `verified:` at all and read `· ungrounded` instead — `.ai-delivery/gates.md:83` currently says `tier: 3-model · verified: 2026-08-12`, which asserts verification of a number nobody verified. Deleting that claim is the honest fix and removes a field rather than adding one. (c) Every line the kit writes must carry an annotation, which is not true today: `conventions.md:172-173`, `:179-180`, `:181-189` and `gates.md:85-90` are kit-written and bare, and the §4 skeleton itself ships them bare. Once that hole is closed, "no annotation" means "a person wrote this" **by construction**, which is the only way pile 4 survives hand-editing. Bump `schema_version` (conventions/gates 1→2, rubrics 2→3); the migration path already exists as the "Artifact `schema_version` vs current" row in `SKILL.md:261`.

Expiry attaches per source URL, not per line — one date per distinct source, so the scratch file's ~30 `1-docs` lines triage as five sources, and re-verifying one URL re-dates all its lines.

For the agent half, add one clause to `artifact-schemas.md` §8 ("Contract for other skills"), the paragraph every skill's `## Setup Gate` stanza already copies verbatim (see `critique/SKILL.md:42-45`): a finding that cites a conventions or rubric line whose `expires:` is past must state the expiry date in the finding rather than citing the line as current.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| Zero new files, zero new scripts, zero new hooks, no network anywhere | The check runs only in a reader's head or an agent's context — nothing mechanically enforces it |
| Piles 3 and 4 become distinguishable without any per-line human marker | Requires the kit to annotate lines it currently ships bare; skeleton edits in §3 and §4 |
| Deletes a false claim (`verified:` on scaffold defaults) rather than adding machinery | Existing schema-1 files keep the dishonest form until a re-run |
| Demotion becomes a grammar-legal move: rewrite a `1-docs` annotation as `· ungrounded` | Nothing prompts it; demotion depends on the person choosing it |

**Risks**
- **Synchronized expiry cliff:** setup writes every line on one day, so every source expires on one day. Per-source grouping shrinks the triage to a handful of URLs, but a mature project still sees one bad morning per year. This is the failure mode the framing names as fatal.
- **Agent compliance is prose, not a check:** the §8 clause depends on the model reading and honouring it. Nothing verifies that a critique run actually flagged the expired citation.
- **Expiry length is invented:** 12 months for `1-docs`, 6 for `2-context7` has no grounding beyond judgment, and the kit would be stamping a date it cannot justify — the same category of sin it is trying to fix, at lower stakes.

**Estimated Complexity**
`Low` — three markdown edits in one reference file plus the frontmatter bump; no code changes at all.

---

### Direction 2: Direction 1 plus one offline subcommand in the existing runtime

**Approach Summary**
Everything in Direction 1, plus an `annotations` subcommand added to `scripts/setup-runtime.js` — a fourth branch in the existing `main()` dispatcher alongside `gate`, `detection-files` and `fingerprint`, reusing `parseCli`'s `--root`. It reads the three artifacts, regex-matches the annotation form the grammar already fixes, and prints each line's pile: `grounded`, `expired`, `ungrounded`, `unannotated`, exiting 2 when anything is expired. It fetches nothing — expiry is pure date arithmetic against the artifact's own text, so it behaves identically offline. It then replaces the weakest existing mechanism, the "`verified:` dates older than ~6 months → offer, never force" row at `SKILL.md:265`, with a row that reads the subcommand and offers exactly three moves per expired source: re-verify, delete, demote.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| The check can actually fail, and fails deterministically | ~80 lines of new parsing code and its own correctness burden |
| A parser gives the agent a mechanical answer instead of prose compliance | The parser now has opinions about hand-edited lines it must not reject |
| The re-run path stops being an offer nobody accepts | Any skill wiring it as blocking would gate work on documentation freshness |

**Risks**
- **The parser becomes a second grammar:** a hand-edited line that the regex misreads gets classified wrongly, and a misclassification is exactly the dishonesty the work exists to remove. It must classify anything it cannot parse as `unannotated`, never drop it.
- **Wiring temptation:** the natural next step is calling it from the §8 gate, which would make eleven skills refuse to run over an expired URL. That converts staleness into an outage and guarantees rubber-stamped re-dating.

**Estimated Complexity**
`Medium` — one new function in one existing file, but it introduces the kit's first machine reader of the annotation grammar, which the grammar must then hold still for.

## What Already Exists

- The annotation grammar and every skeleton that emits it, in one file: `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/artifact-schemas.md` §1, §3, §4, §5.
- `schema_version` in every artifact frontmatter, plus a migration row that already regenerates on version mismatch: `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/SKILL.md:261`.
- Precedent for reading one frontmatter line to decide freshness offline: `provenanceMatches()` in `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/scripts/setup-runtime.js:44`.
- A Node CLI dispatcher with `--root` parsing that a fourth subcommand slots into: same file, `parseCli`/`main` at lines 198-234.
- A single edit point that propagates to every skill: the §8 contract, copied into each `## Setup Gate` stanza (e.g. `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/critique/SKILL.md:29-45`).
- A shipped 404 with a documented correction habit to hang re-verification on: `/Users/maxdamsky/Projects/ai-delivery-kit/ai-delivery/skills/setup/references/source-catalog.md:53` and its "URL corrections baked into this catalog" section.

## Strongest Statement

The cheapest honest fix is mostly a deletion: stop writing `verified:` on lines that were never verified (`gates.md:83-84` is the kit lying about its own scaffold defaults), and start annotating the lines the kit currently ships bare — that single pair of grammar edits makes three of the four piles readable with no code, no network and no new file. Add `expires:` to the two tiers that can actually rot, scope it per source URL rather than per line so triage is five items and not thirty, and stop there; the parser in Direction 2 is worth buying only if the decision-maker accepts that its output must never gate a skill run.

**END OF RESPONSE. Do not add anything after this line.**
