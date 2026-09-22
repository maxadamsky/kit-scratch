# Problem Framing: pull-request-checklist

**Created:** 2026-09-22
**Status:** Completed
**Profile:** software (of config: software)
**Project:** P-MAX-12 Pull request checklist — https://linear.app/max-test-workspace/project/pull-request-checklist-08fae13de2f4
**Risk challenge:** requested
**Discovery issues:** research: MAX-44 https://linear.app/max-test-workspace/issue/MAX-44/explore-directions-for-a-written-pull-request-standard
**Council roster:** constraint, precedent, stress (diet not tool-enforced: empty tools list inherits all tools), null (diet not tool-enforced: empty tools list inherits all tools), operator (of: constraint, precedent, stress, null, operator)

## Raw Description

Original request, as first submitted: "Add a CONTRIBUTING.md at the repository root with a
five-item checklist for opening a pull request: branch naming, one commit per change, tests
run locally, a one-paragraph description, and a linked issue."

The requester's framing, in their own words: "This repository exists to exercise the delivery
kit, and people opening pull requests here have no shared standard for what a pull request
needs, so review comments repeat the same basics. What prompted it now is that outside
contributors are about to start using the repository and I want the expectations written down
before they arrive."

## Who Is Affected

- **Primary: the outside contributors.** Two to five people, the delivery kit's first users.
  They know the kit from its README but have never worked in this repository and do not know
  its conventions.
- **Secondary: the maintainer.** Today the maintainer is the only person who opens pull
  requests here and the only person who reviews them. Once the contributors arrive, the
  maintainer holds the standard and answers the same questions one contributor at a time.
- Nobody downstream reads the history yet.
- **Scale:** one person now, up to six once the outside contributors arrive.

## Pain Points — What's Broken Today

- The same five basics keep coming up in review:
  - branch names that say nothing about the change
  - several unrelated changes squeezed into one commit
  - pull requests opened before the tests were run locally
  - a one-line description that does not say why
  - no link to the issue the work came from
- The standard is unwritten. The maintainer knows the conventions because they set them. The
  conventions live in the maintainer's head and nowhere else, so a newcomer has no way to find
  them.
- It falls apart at the moment a pull request is opened. By then the branch is named, the
  commits are shaped and the description is written, so asking for changes means redoing work
  that was already done.

## The Opportunity

- A newcomer can open a pull request that meets the standard without asking the maintainer
  first, because the standard is written where they will look before they start.
- The maintainer stops writing the same five review comments and stops explaining conventions
  one contributor at a time.
- The outcome that matters most is newcomers getting it right the first time, because that is
  what removes the rework. Less review time follows from it.

## Constraints

- **Timeline:** the outside contributors arrive within two weeks. The date is fixed by when
  the kit ships.
- **Technical:** the repository is a small Python project managed with uv and tested with
  pytest. Anything proposed must fit that and need no new tooling.
- **Organizational:** the repository is the kit's test bed. Changes stay small and ordinary.
  Nothing may make it unrepresentative of a real project.
- **Effort:** a few hours at most.
- **Must not:** propose automated enforcement, or anything beyond a document, at this stage.
- **Must not:** propose changes to the kit itself.

## Prior Art and Context

- The repository has never had written contribution guidance, and nothing in it covers the
  five basics.
- The kit keeps a record of this repository's conventions. It is close to what is needed, but
  it was written for the kit's skills to read, not for a person opening a pull request.
- The requester is drawing on the ordinary shape of open-source contributing guides, nothing
  specific.
- Ruled out: automated enforcement and changes to the kit (see Constraints). Nothing else has
  been ruled out.

## Success Signal

- The first pull requests from outside contributors arrive with a branch name that says what
  changed, one commit per change, tests already run locally, a description that says why, and
  a linked issue, all without the maintainer asking.
- The five review comments disappear from the maintainer's reviews.
- **Threshold**, across the first ten pull requests from outside contributors:
  - at most one needs a comment asking for one of the five items: it worked
  - exactly two need such a comment: inconclusive
  - three or more need such a comment: it did not work
