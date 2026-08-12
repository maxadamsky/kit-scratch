## Council Response

**Evidence consulted:** https://mementoweb.org/robustlinks/spec/ (fetched); https://en.wikipedia.org/wiki/Template:Dead_link, https://en.wikipedia.org/wiki/Template:Citation_needed, https://en.wikipedia.org/wiki/Category:Citation_and_verifiability_maintenance_templates, https://en.wikipedia.org/wiki/Help:Maintenance_template_removal (searched); https://www.npmjs.com/package/linkinator, https://github.com/JustinBeckwith/linkinator, https://www.npmjs.com/package/markdown-link-check (searched); https://github.com/lycheeverse/lychee (searched); https://archive.org/help/wayback_api.php (searched); https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams (searched); https://glama.ai/mcp/servers/@tosin2013/documcp/blob/.../docs/how-to/documentation-freshness-tracking.md (searched)

### Candidate 1: Wikipedia's citation-and-verifiability inline template system

**What it is:** A ~50-template inline grammar maintained by the English Wikipedia community for annotating individual claims with their sourcing state — `{{citation needed}}` (with a `|date=` parameter), `{{dead link}}`, `{{permanent dead link}}`, `{{verify source}}`, `{{failed verification}}`, `{{better source needed}}`. Each renders human-readable text next to the claim and files the page into a dated maintenance category. `Help:Maintenance template removal` is the documented triage procedure: fix, re-source, or remove the claim.

**What it covers:** The four-pile sort, almost exactly, and it is the only precedent found that separates the piles the brief cares about. `{{dead link}}` is "was grounded, grounding gone" (pile 2). `{{citation needed}}` is "asserted with no source" (piles 3/4). `{{failed verification}}` is the case the brief says hashes miss — source still resolves, no longer supports the claim. Annotations are prose, readable with no network and no knowledge of the tooling. The dated variant plus the removal-help page is a documented precedent for the demote-or-delete move.

**What it does not cover:** It is a convention plus a template renderer, not something you install. It does not distinguish kit-asserted from human-asserted — Wikipedia has no such actor split. Critically, it is also the strongest available *evidence for the brief's own failure mode*: `{{citation needed}}` backlogs run to hundreds of thousands of tagged statements, many dated years back. Wikipedia sustains triage only via a paid-and-volunteer editor corps and bots (InternetArchiveBot) that no single repo has.

**Adoption cost:** Zero licensing friction (content CC BY-SA 4.0), zero hosting, zero lock-in — you adopt the grammar and the triage doc, not code. Cost is design translation work, and the discipline to avoid the backlog outcome.

**Evidence basis:** `searched — https://en.wikipedia.org/wiki/Template:Dead_link`, `searched — https://en.wikipedia.org/wiki/Help:Maintenance_template_removal`; backlog scale is `recalled`.

### Candidate 2: Robust Links (Memento / Los Alamos NDL) plus Wayback Save Page Now

**What it is:** A published specification from the Memento project (Herbert Van de Sompel et al., also behind RFC 7089 Memento) that decorates a link with three attributes: `data-originalurl`, `data-versiondate` (the datetime the link was made — the snapshot moment), and `data-versionurl` (a known-good archived copy). Internet Archive's Save Page Now API creates the snapshot, rate-limited to roughly 15 URLs per minute.

**What it covers:** The exact grammar for "this claim was grounded in *this state* of *this source* on *this date*," carried inside the artifact, interpretable offline by a human reading it. It also fixes a gap the brief does not name: if the source is snapshotted at verification time, an expired line is *recoverable* — a reader can go see what the source said when the convention was written, instead of only learning that it is gone. That converts demotion from a guess into a decision.

**What it does not cover:** No expiry semantics — `data-versiondate` records when, never asserts until-when; you supply the shelf-life policy. Nothing for never-grounded or human-authored lines. Snapshotting requires network at write time and introduces a third-party dependency (archive.org availability, rate limits, and pages that block archiving). The spec's canonical host `robustlinks.mementoweb.org` failed DNS resolution for me this session; only the `mementoweb.org/robustlinks/spec/` copy resolved, and it self-describes as under "ongoing explorative and experimental revision" — a spec worth copying, not depending on.

**Adoption cost:** No package to install and no license stated on the spec page. Wayback SPN is free, unauthenticated for basic use, rate-limited, and is a real external dependency you would be adding to a setup path.

**Evidence basis:** `fetched — https://mementoweb.org/robustlinks/spec/`; rate limit `searched — https://archive.org/help/wayback_api.php`.

### Candidate 3: linkinator (npm), with markdown-link-check as the smaller alternative

**What it is:** A TypeScript link checker by Justin Beckwith that ships a programmatic Node API (`import { LinkChecker } from 'linkinator'`) alongside its CLI, so it runs inside a Node script with no shell — the constraint that eliminates lychee, which is a Rust binary you would have to fetch and exec per-platform. `markdown-link-check` is the narrower npm equivalent, markdown-only, also with a programmatic API.

**What it covers:** Only the human-triggered re-verification pass, and only for docs-tier lines: does this URL still resolve. That is the 404 that shipped.

**What it does not cover:** Everything the brief already says link-rot tooling misses — model-knowledge lines, scaffold defaults, and sources that resolve while no longer supporting the claim. It has no concept of a claim, a tier, or an expiry; it reports URLs, so mapping results back to lines is yours. It requires network by definition.

**Adoption cost:** Permissive npm dependency (MIT, recalled — verify before adopting), meaningful transitive dependency weight from its crawler, and it is genuinely a build-vs-adopt toss-up against a ~40-line `fetch` loop.

## Strongest Statement

Adopt two things that are not code: Wikipedia's inline verifiability grammar for the four-pile sort, and Robust Links' `versiondate`/`versionurl` pair so an expired line points at what the source said when it was verified — that snapshot is what makes demotion a decision rather than a shrug. The only thing worth installing is a Node link checker for the explicit re-verification pass, and Wikipedia is simultaneously your best precedent and your loudest warning: its citation-needed backlog is the "forty expired lines nobody triages" outcome, already run for twenty years at scale.

Sources: [Robust Links spec](https://mementoweb.org/robustlinks/spec/), [Template:Dead link](https://en.wikipedia.org/wiki/Template:Dead_link), [Template:Citation needed](https://en.wikipedia.org/wiki/Template:Citation_needed), [Citation and verifiability maintenance templates](https://en.wikipedia.org/wiki/Category:Citation_and_verifiability_maintenance_templates), [Help:Maintenance template removal](https://en.wikipedia.org/wiki/Help:Maintenance_template_removal), [linkinator](https://github.com/JustinBeckwith/linkinator), [linkinator on npm](https://www.npmjs.com/package/linkinator), [markdown-link-check](https://www.npmjs.com/package/markdown-link-check), [lychee](https://github.com/lycheeverse/lychee), [Wayback Machine APIs](https://archive.org/help/wayback_api.php), [Swimm](https://swimm.io/blog/sync-dont-sink-why-we-built-swimm-for-dev-teams), [DocuMCP freshness tracking](https://glama.ai/mcp/servers/@tosin2013/documcp/blob/050216adf8c074d5cf30294bcf87772164788e0c/docs/how-to/documentation-freshness-tracking.md)

**END OF RESPONSE. Do not add anything after this line.**
