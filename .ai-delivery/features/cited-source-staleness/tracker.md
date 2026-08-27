# Tracker — cited-source-staleness

- linear_project: 3511d0f6-1685-461a-8da8-2519de2e9b58
- linear_project_url: https://linear.app/cdrun-metrics/project/honest-source-annotations-in-generated-artifacts-7f75229508e5
- team: CDR
- created_on: 2026-08-12

## Units

- define-annotation-states: CDR-10 https://linear.app/cdrun-metrics/issue/CDR-10/define-the-four-annotation-states-and-what-each-claims
- setup-emits-annotations: CDR-11 https://linear.app/cdrun-metrics/issue/CDR-11/write-honest-annotations-when-setup-generates-artifacts
- detect-older-grammar: CDR-12 https://linear.app/cdrun-metrics/issue/CDR-12/detect-artifacts-written-under-an-older-grammar
- convert-existing-artifacts: CDR-13 https://linear.app/cdrun-metrics/issue/CDR-13/convert-existing-artifacts-to-the-new-grammar-on-a-re-run
- report-grounding-age: CDR-14 https://linear.app/cdrun-metrics/issue/CDR-14/report-grounding-age-when-a-finding-cites-an-artifact-line

## Build

Decomposition confirmed 2026-08-27. The five tracked units above match implementation grain
one-to-one — no sub-issues were needed, and none were created.

**Spec skeletons** (Phase 2 output, completed by Phase 3):

- define-annotation-states: `specs/define-annotation-states.md` → CDR-10
- setup-emits-annotations: `specs/setup-emits-annotations.md` → CDR-11
- detect-older-grammar: `specs/detect-older-grammar.md` → CDR-12
- convert-existing-artifacts: `specs/convert-existing-artifacts.md` → CDR-13
- report-grounding-age: `specs/report-grounding-age.md` → CDR-14
- integration: `specs/integration.md` → **not yet created in Linear**

**Pending Linear write — owner: kit maintainer.** The integration issue was specced but
deliberately not created; the maintainer declined the tracker write on 2026-08-27. When it is
created it must be a top-level issue in this project, carrying the `integration` label,
assigned to the final milestone ("Existing projects and agent findings"), and blocked-by
CDR-10, CDR-11, CDR-12, CDR-13, and CDR-14. Record its identifier here immediately.

**No issue state was changed by this build invocation.** All five units remain in Backlog,
because this invocation produces design and specifications only — implementation is deferred
to `/Users/maxdamsky/Projects/ai-delivery-kit`, which has no delivery configuration of its
own yet. See `design/1a-discovery.md` § Scope of this build invocation.
