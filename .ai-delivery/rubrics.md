---
schema_version: 2
generated_on: 2026-08-12
regenerated_on: 2026-09-07
generated_under_profile: software
---

# Review Rubrics

## About This File

Consumed by verify (gate decisions), critique and tidy (evaluation), and fix
(regression scope). `blocking` items fail verification when unmet; `advisory` items are
reported, never gate. Every item is checkable in a single review pass and cites its source.

## Severity Scale

- blocking — verification fails while this is unmet
- advisory — reported with a recommendation; never fails a gate

## Core Rubric

### Functionality

- [ ] Every acceptance criterion in the spec has corresponding implemented behavior; any deviation is named in the handoff, never silent — severity: blocking
- [ ] Edge cases behave as specified: empty, boundary, and null-class inputs — severity: blocking
- [ ] Error paths behave as specified: invalid input fails fast with the documented error; no silent failure, fallback, or partial result — severity: blocking

### Testing

- [ ] New behavior has a check, under the profile's verification method, that can fail — severity: blocking
- [ ] Checks exercise the shipped artifact, not a stand-in — severity: blocking
- [ ] Adverse cases are checked, not only the expected path: error paths and empty, boundary, and malformed inputs — severity: blocking
- [ ] No check-only branches in the shipped artifact: no paths that exist solely so checks can pass — severity: blocking

### Security

- [ ] Input crossing a trust boundary is validated on arrival; validation failures reject and stop processing — severity: blocking
- [ ] No secrets, credentials, or tokens in code, configuration, or history — severity: blocking
- [ ] No injection paths: queries, commands, and markup built from untrusted data use parameterized or safe APIs, or context-correct escaping — severity: blocking
- [ ] Authorization is checked at every new or changed surface — severity: blocking
- [ ] No PII or sensitive values in logs or error output beyond the documented contract — severity: blocking
- [ ] Dependencies are free of known-critical vulnerabilities — severity: blocking

### Performance

- [ ] No unbounded growth: collections, queries, and result sets are bounded or paginated — severity: advisory
- [ ] Hot paths are free of avoidable I/O and of repeated work a single pass could do — severity: advisory
- [ ] Anything opened is deterministically closed: files, connections, handles, subscriptions — severity: blocking

### Maintainability

- [ ] The change follows conventions.md: structure, naming, error handling — severity: blocking
- [ ] No dead code, commented-out blocks, or debug leftovers introduced — severity: blocking
- [ ] Public surfaces are documented where conventions.md requires it — severity: blocking

## Stack Rubric: python

- [ ] Test files, test functions, and test classes match the patterns pytest discovers, and test classes define no constructor — a file that misses them is silently never collected, so the suite reports green while the behavior is unchecked — severity: blocking
      [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Tests reach the package under test as an installed distribution, never by mutating the interpreter path from inside test code — severity: blocking
      [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Shared fixtures live in a conftest module at the narrowest scope that serves them, rather than being copied into each test module — severity: advisory
      [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Names match the PEP 8 category for their kind: lowercase modules and packages, CapWords classes with acronyms fully capitalized, underscore-separated functions and variables, all-caps module constants — severity: advisory
      [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- [ ] Exception classes end in the word Error — severity: advisory
      [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- [ ] Non-public methods and attributes carry a single leading underscore; a double leading underscore appears only where subclass name mangling is genuinely wanted — severity: advisory
      [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- [ ] A deliberate departure from PEP 8 is justified by one of the four reasons PEP 8 itself allows, and that justification is visible in the diff or the module — severity: advisory
      [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- [ ] Public function signatures carry type annotations, so the type-check gate has a contract to check rather than inferring one — severity: advisory
      [source: model knowledge · tier: 3-model · verified: 2026-08-12]

## Project Rubric

- [ ] Anything added to this repository is reachable from the test command in gates.md; a module no test run can reach is not verified here, whatever the coverage number says — severity: blocking
      [source: README.md · tier: 1-code · verified: 2026-09-07]
- [ ] Runtime dependencies are declared in the project manifest rather than assumed present in the environment; a run that needs an undeclared package is a defect in the manifest, not a machine to fix — severity: blocking
      [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Untrusted string input is checked against an allowlist with explicit length bounds, and numeric input against explicit ranges, before it reaches any sink — severity: blocking
      [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Regular expressions applied to untrusted input anchor the entire value and contain no nested quantifier that admits catastrophic backtracking — severity: blocking
      [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Rejected input is logged as a validation failure, so a run of them is visible as an attack signal rather than lost as user error — severity: advisory
      [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Configuration read from the environment is validated at process start and fails loudly when a required value is missing, rather than defaulting silently — severity: blocking
      [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- [ ] Secrets reach the process by runtime injection or a secrets manager — never a committed configuration file, never a container image build argument or baked environment value — severity: blocking
      [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]

## Accessibility Rubric

Not applicable — no UI surface detected (`ui_facing: false`).

## Software Rubric

- [ ] Tests assert an outcome or resulting state; a test whose only assertion is that a mock was called does not count as coverage of the behavior — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · verified: 2026-08-12]
- [ ] A test that asserts something merely exists also verifies its content or its behavior — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · verified: 2026-08-12]
- [ ] Tests are isolated: no shared mutable state couples one test's outcome to another's, and integration tests isolate that state per test — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Test-first meaning · tier: 1-profile · verified: 2026-08-12]
- [ ] The whole suite passes, not only the tests touching this change — the suite is what catches cross-unit regressions — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · verified: 2026-08-12]
- [ ] Tests follow an arrange, act, assert structure with names that state the behavior under test — severity: advisory
      [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · verified: 2026-08-12]
- [ ] A contract consumed across a unit boundary is defined as an interface or protocol rather than a concrete class, so the implementation can be swapped without changing any consumer — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · verified: 2026-08-12]
- [ ] Each unit is testable with mock dependencies alone, requiring no running database, network, filesystem, or particular environment — severity: blocking
      [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · verified: 2026-08-12]

## Infrastructure Rubric

Not applicable — software profile, and no infrastructure code is owned by this repository.

## Data Rubric

Not applicable — software profile.
