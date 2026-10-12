## Council Response

**Evidence consulted:** none — reasoning from framing only

## The Case Against

**Core argument: the stated pain has not happened yet, so the five items are a forecast of newcomer mistakes, not an observed record of them.** The framing describes the pain in the present tense: "the same five basics keep coming up in review." It also says that "today the maintainer is the only person who opens pull requests here and the only person who reviews them." Both cannot describe outside contributors, because none have arrived. The five items are either the maintainer's notes on their own pull requests, or a guess at what strangers will get wrong. Either way, nobody who is actually unfamiliar with the repository has produced this pain yet.

Supporting points:

1. **The five items come from the one person who least needs them.** The maintainer set the conventions, and a list of what the maintainer notices is not the same as a list of what trips up newcomers. The primary users already "know the kit from its README." It is an **assumption**, but a reasonable one, that their real friction will be something the list does not name. Examples include how to run the test suite with uv, which issues are open to take, and what this test-bed repository is for. If so, the pain the list targets is not the pain that actually arrives.

2. **The success signal has no baseline, so the result cannot be read.** The threshold covers the first ten outside pull requests: at most one needing a comment means it worked, three or more means it did not. But no outside pull request has ever been reviewed here. If the first ten arrive clean, nobody can tell whether the document did it or these particular contributors would have done it anyway. With two to five people, ten pull requests may also take a long time to accumulate (**assumption**: the framing gives no expected rate). The decision would be judged against a counterfactual that can never be observed.

3. **"The standard lives only in the maintainer's head" is partly false by the framing's own account.** The kit already keeps a record of this repository's conventions, described as "close to what is needed." The honest statement of the pain is narrower: a written standard exists, but a newcomer would not find or read it. That is a discoverability problem, not a missing-standard problem. A second written copy of the same conventions creates two sources that can drift apart in a repository whose job is to stay representative.

4. **At this scale, the rework being prevented is small and bounded.** Two to five people, a small Python project, first contributions. Renaming a branch, splitting a commit, rewriting a paragraph and adding a link each take minutes (**assumption**: the framing does not size the rework). Paying for those minutes once gives the maintainer something the document cannot: evidence of what these contributors actually get wrong.

**Honesty check:** this case is weaker than usual. The proposed cost is a few hours, the constraints already rule out anything beyond a document, and the timing is fixed. I am not arguing that the idea is harmful. I am arguing that it rests on a forecast presented as an observation, and that waiting briefly would replace the forecast with evidence.

## What To Do Instead

**Wait until a named condition changes: the first three pull requests from outside contributors have been reviewed.**

Until then:
- The maintainer reviews those first three pull requests as normal.
- For each one, the maintainer records which of the five items needed a comment.
- The maintainer also records any recurring problem that is not among the five.

Once the third review is done, decide from what was recorded:
- If the five items recur, the premise is confirmed and the case for writing them down is proven.
- If different problems recur, the premise was the wrong pain, and the decision should be made against the observed ones.
- If nothing recurs, the pain was the maintainer's alone, and doing nothing was correct.

## Steelman

The framing's central pain point is timing: mistakes surface at the moment a pull request is opened, after the work is already shaped. Waiting guarantees that exact failure for the kit's very first outside users, on their first contact with the project. It also turns the maintainer's reviews into the first-impression correction the requester explicitly wants to avoid. Against a cost of a few hours and a fixed arrival date, deliberately letting three first pull requests fail in order to gather evidence may cost more goodwill than the evidence is worth. A test bed's first users are also the people whose early experience of the kit matters most.

## Strongest Statement

Every pain point in this framing describes newcomers, yet no newcomer has opened a pull request here, so the five-item list is the maintainer's prediction, not a record of what went wrong. Before choosing a direction, the maintainer should answer one question: were these five comments ever written to anyone other than themselves? If the answer is no, you, the maintainer and requester, own deciding whether to act on a forecast or wait three pull requests for evidence.

**END OF RESPONSE. Do not add anything after this line.**
