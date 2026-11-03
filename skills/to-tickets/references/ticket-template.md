# Ticket template

Used when the project has no template of its own. Keep every section; write `None` where nothing applies.

```markdown
# <Title: the outcome this ticket delivers>

## Context
- Spec: <link>. Parent: <link, or "none">.
- Scenarios: <S1, S3 — the spec scenarios this ticket makes true>
- Repository: <repo>
- Why: <one or two sentences on what this unlocks for the user>

## What to build
<The end-to-end behaviour this ticket makes work, from the user's point of view. Name the modules, interfaces and contracts it adds or changes. No file paths or code.>

## Acceptance criteria
- [ ] <Observable result in a concrete situation>
- [ ] <Edge case or regression with a clear pass condition>

## How to verify
- Tests: <the seam where each criterion is tested; the existing tests to follow>
- Live: <how the result is shown in the running app or service, and what you should see>

## Decisions
- <Binding decision from the spec that constrains this ticket — date, who decided>

## Out of scope
- <What an agent could plausibly add here but must not>

## Blocked by
- <ticket reference>, or "None (can start immediately)"
```

For a ticket that only a person can complete, replace *What to build* with **Action** (what the person does) and *How to verify* with **Done when** (what confirms it, for example a store status or a dated sign-off).
