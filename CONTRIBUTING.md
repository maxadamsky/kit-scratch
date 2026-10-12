# Pull request checklist

Every pull request to this repository must include the five things below, whichever tool
opens it.

1. Name the branch `<GitHub handle>/<short topic>`; the `codex/` prefix is reserved for
   branches made by an agent.

   Example: `octocat/fix-readme-typo`

2. Make one commit per logical change, so a pull request may hold several commits.

   Example: a typo fix and a new section are two logical changes, so they go in as two
   commits in the same pull request.

3. Run `uv run pytest` before opening a pull request; until the first test module lands,
   "no tests ran" with exit code 5 is the expected result.

   Example: `uv run pytest` prints "no tests ran" and exits with code 5 today.

4. Write a one-paragraph pull request description that says why the change was made.

   Example: New contributors could not tell which command runs the tests. This change
   names the command near the top of the page, so it is the first thing a newcomer
   reads.

5. Link a GitHub issue on this repository in the description, filed or picked before you
   start work; the maintainer adds any Linear link at review.

   Example: Related to #12.
