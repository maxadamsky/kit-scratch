## Council Response

**Evidence consulted:**
- fetched: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
- fetched: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
- fetched: https://github.com/nayafia/contributing-template
- fetched: https://github.com/bttger/contributing-gen
- fetched: https://conventionalbranch.org/ (the old address, conventional-branch.github.io, redirects here)

**Stated assumption:** The brief doesn't say where the repository is hosted. Candidates 1 and 2 assume GitHub. On GitLab or Bitbucket the same approach works, but the file paths differ.

### Candidate 1: GitHub's pull request template file, with CONTRIBUTING.md placed where GitHub already shows it

**What it is:** A plain Markdown file named `pull_request_template.md`, placed at the repository root, in `docs/`, or in `.github/`. GitHub, which runs the feature, says contributors "will automatically see the template's contents in the pull request body." GitHub also links to a CONTRIBUTING.md file whenever someone opens a pull request or an issue, and shows it on a "Contributing" tab and in the repository sidebar.

**What it covers:** Three of the five items: the description that says why, the linked issue (a `Closes #` line in the template), and a "tests run locally" checkbox. Contributors see them while writing the pull request, without looking for them. CONTRIBUTING.md at the root gets the automatic link at the moment a pull request is opened.

**What it does not cover:** The template shows up when the pull request is opened. By then the branch is named and the commits are made, and the framing names that timing as the cause of rework. So branch naming and one commit per change still need CONTRIBUTING.md, read before work starts. The template only takes effect once it is merged into the default branch. It checks nothing: a contributor can delete the text. That fits the "document only" constraint, but it adds nothing beyond that.

**Adoption cost:** Free, one extra Markdown file, about 15 minutes. It needs no new tools and doesn't touch Python, uv or pytest. The lock-in is small: the path is GitHub's convention, and GitLab uses a different folder for the same idea. One scope question for the requester: the request names a single CONTRIBUTING.md. A second file is still only a document, not enforcement, but it goes beyond the literal request.

**Evidence basis:** `fetched — https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository`; `fetched — https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors`

### Candidate 2: Conventional Branch specification (a published branch-naming standard)

**What it is:** A published branch-naming standard, maintained by Xianpeng Shen under the CC BY 4.0 license. The format is `<type>/<description>`. The types are `feature/` or `feat/`, `bugfix/` or `fix/`, `hotfix/`, `release/` and `chore/`. Descriptions use lowercase letters, digits and hyphens only. Version 1.1.0 adds prefixes for AI agents, such as `claude/` and `codex/`.

**What it covers:** The branch-naming item. CONTRIBUTING.md can cite it in one line ("branches follow Conventional Branch") instead of defining a new rule, and newcomers can look it up on their own.

**What it does not cover:** The other four items. It may also conflict with how this repository already names branches. The current branch, `live-proof-2026-09-21`, has no type prefix, so adopting the spec as written would change the maintainer's own practice. Its companion standard for commit messages (Conventional Commits) is about message format, not "one commit per change."

**Adoption cost:** Free. CC BY 4.0 requires credit if the spec text is copied; a link covers that. The spec comes with tooling, but the constraints rule tooling out, so adopt only the written rule.

**Evidence basis:** `fetched — https://conventionalbranch.org/`

### Candidate 3: nayafia/contributing-template (CC0), or bttger/contributing-gen (MIT), as a starting skeleton

**What it is:** nayafia/contributing-template is a checklist-style CONTRIBUTING template, built from a review of 40 open-source projects and released under CC0 (public domain). bttger/contributing-gen is an MIT-licensed generator that produces a full CONTRIBUTING.md, drawing on the guides of Rails, Atom, Bootstrap, Ember and Celery. It runs with `npm run gen`, or in a browser at contributing-gen-web.

**What it covers:** The overall structure and tone of a contributing guide ("welcoming language, explain unfamiliar terms"). This matches the requester's "ordinary shape of open-source contributing guides."

**What it does not cover:** The five items themselves. Neither fetched page shows specific guidance on branch naming, commit granularity, running tests, or linking issues. Both produce far more than a five-item checklist: code of conduct, security reporting, roadmap. Trimming that back takes about as long as writing five bullets. contributing-gen needs Node through npm; the web version avoids that, but it is still tooling outside a uv/pytest project.

**Adoption cost:** Free (CC0 or MIT). The real cost is trimming the content back down to fit the "small and ordinary" constraint. This is a weak fit, listed only as a reference for shape.

**Evidence basis:** `fetched — https://github.com/nayafia/contributing-template`; `fetched — https://github.com/bttger/contributing-gen`

## Strongest Statement

There is no product to adopt here, and the one worth adopting is a convention: GitHub's built-in places for these files. It costs nothing and puts the standard in front of contributors when they open a pull request. It still can't prevent the rework the framing is worried about, because branches and commits are finished before any pull request exists. So CONTRIBUTING.md has to be where newcomers look before they start work, and the pull request template can only back it up. Before the contributors arrive in two weeks, the requester needs to decide two things: whether a second template file is within scope, and whether to adopt Conventional Branch prefixes, which would change their own current branch naming.

**END OF RESPONSE. Do not add anything after this line.**
