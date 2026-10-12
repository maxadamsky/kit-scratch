## Council Response

**Evidence consulted:** /Users/maxdamsky/Projects/kit-scratch/pyproject.toml, /Users/maxdamsky/Projects/kit-scratch/.gitignore, /Users/maxdamsky/Projects/kit-scratch/CONTRIBUTING.md, /Users/maxdamsky/Projects/kit-scratch/README.md, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/gates.md, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/config.md. I also searched every Python file outside `.venv` for logging, stderr or exit handling and found none. The repository has no `src/`, no `tests/`, no CI directory, no Makefile, no hooks beyond git's samples, and no monitoring config. `config.md` records `ci_system: null` and `cloud_provider: null`. `gates.md` says "No verify run has executed these gates yet" and marks Build as `unavailable`.

**Assumption:** The one person paged is the developer. The page is the shell prompt itself: they notice it misbehaving the next time they switch into a project. Nothing else would alert anyone.

### Scenarios

**Scenario 1: The prompt shows a wrong open count**
- **Detection:** Nothing detects this. The success signal in the framing is that the developer trusts the number without opening the file. So once the tool ships, the developer has stopped doing the cross-check that would catch a bad count.
- **Diagnosis at 3am:** Nothing to work from. The repository has no logging (the search found none), and the framing defines no way to list which lines were counted. The planned JSON output carries a count and headings but no line numbers. It also carries no version or commit, so the developer can't tell which build produced the number.
- **Recovery:** The count is computed on each call and nothing is stored, so there is nothing to backfill. Rolling back means going back to a specific git commit. But without a version in the output, the developer can't tell which commit to go back to.
- **On-call cost:** The developer quietly skips open items across about ten projects until one of them happens to count by hand.

**Scenario 2: The tool exits non-zero on every prompt draw**
- **Detection:** Nothing detects this, by design. The framing requires errors to go to stderr so the calling script can ignore them. So the prompt simply loses its count, which looks the same as a project with no notes file.
- **Diagnosis at 3am:** The prompt script drops stderr, and there is no log file or error record anywhere. To see the error, the developer has to run the command by hand in each affected project.
- **Recovery:** Switch it off in the shell prompt config, which lives outside this repository. Nothing here documents that step.
- **On-call cost:** It is found late, only when the developer notices the count has been missing. The failed runs have left no trace.

**Scenario 3: The tool hangs or runs slowly inside the prompt**
- **Detection:** Loud. Every new prompt stalls.
- **Diagnosis at 3am:** The repository defines no timeout for the calling script, no timing output, and no debug flag.
- **Recovery:** The developer has to edit their shell startup file from a shell that is stalling on every prompt. No documented off switch (for example, an environment variable) exists.
- **On-call cost:** High. The terminal is barely usable until the prompt config is fixed by hand.

**Scenario 4: A change to the JSON output breaks the prompt script**
- **Detection:** Nothing detects this. The prompt script is the only consumer, and it lives outside this repository, so no test here exercises it. The test gate `uv run pytest` currently exits with code 5, meaning "no tests ran" (`CONTRIBUTING.md` item 3).
- **Diagnosis at 3am:** The JSON has no schema version field. The developer has to compare the old output with the new one by hand.
- **Recovery:** Check out an earlier commit. No version number or release tag records which JSON shape the prompt script expects.
- **On-call cost:** Moderate. The failure itself is quiet, but tracing it back to the change that caused it is manual work.

**Scenario 5: A notes file was changed**
- **Detection:** Nothing detects this. The tool is required never to write, but nothing records what it touched.
- **Diagnosis at 3am:** There is no audit trail, and nothing records which of the roughly ten files, spread across other projects, were affected.
- **Recovery:** Only possible if each of those projects has the notes file under git. That is not guaranteed and cannot be checked from this repository.
- **On-call cost:** The developer's personal notes may be lost for good. Of all these scenarios, this is the only one that can't be undone.

**Scenario 6: A bad change reaches the running tool**
- **Detection:** None before it runs. There is no CI (`ci_system: null`), no gate has ever run, and `gates.md` lists Build as `unavailable`.
- **Diagnosis at 3am:** Git history only.
- **Recovery:** `pyproject.toml` defines no command-line entry point (no `[project.scripts]` section) and there is no build step. So the prompt most likely runs the tool straight from this repository's working copy. That means whichever branch is checked out is the version the prompt runs. This repository is a test fixture for the delivery kit, and its `live-proof-*` branches change often, so every branch switch silently changes the tool. Rolling back means checking out a different branch, which also rolls back unrelated work.
- **On-call cost:** It breaks every time the developer switches branches here, and the break shows up in other projects' terminals, far from its cause.

## First-Night Page

Scenario 2, compounded by Scenario 6. The first night, the prompt runs the tool from this repository's checked-out branch. The branch changes, or the tool errors, and the error goes to stderr, which the prompt script throws away as the framing requires. The open count disappears from every project's prompt. Nothing records why, and nothing tells the developer that "no count" means "broken" rather than "no notes file". They find out only when they realise the number is missing, then have to run the tool by hand in each project to see the error.

## Strongest Statement

The framing asks for two things at once: errors must be invisible to the prompt, and the prompt's count must be trusted without checking. Those two together mean every failure is silent unless the tool leaves some visible signal. The decision to make is whether to add three things:
- a visible failure marker in the prompt
- a version stamp in the JSON output
- a fixed, installed copy of the tool (via a declared entry point) instead of running from whatever branch this repository has checked out

The developer who owns this repository makes that call.

**END OF RESPONSE. Do not add anything after this line.**
