# Ticket templates

Used when the project has no template of its own. A project template may change the format; the content these sections carry stays required, because a ticket plus its parent (or a standalone ticket alone) must be the complete brief (see the self-containment rule in `SKILL.md`). Keep every section; write `None` where nothing applies.

## Parent

```markdown
# <Title: the outcome of the whole effort>

## Problem and goal
<What is wrong or missing today, for whom, and what is true when the effort is done.>

## Target architecture
<How the parts fit after the change: components, ownership, lifetimes, data flow. A short diagram when more than two parts move.>

## Decisions
- <Decision>. Why: <reason>.

## Rejected alternatives
- <Alternative>. Rejected because: <reason>.

## Terms
- <Term>: <meaning in this effort>.

## Facts about today's code
- <Behaviour, class or module several children rely on, as it is on the default branch.>

## Constraints and out of scope
- <What must not change; what the whole effort leaves out.>

## Children and order
- <child reference>: <one line>. Blocked by <references>.
<Order or dependency picture; phases if any.>
```

## Child

```markdown
# <Title: the outcome this ticket delivers>

Read the parent <reference> first. Repository: <repo>.

## Context
<How the code behaves today where this change lands (classes, modules, flows, existing tests), and why the change is needed now. The spec scenarios it makes true, stated in words.>

## What to build
<Behaviour, contracts, names and steps, precise enough that two agents would build the same thing.>

## Decisions
- <Decision that constrains this change>. Why: <reason>.

## Rejected approaches
- <Route an agent could plausibly take>. Not this, because: <reason>.

## Out of scope
- <What an agent could plausibly add here but must not>

## Acceptance criteria
- [ ] <Observable result in a concrete situation>
- [ ] <Edge case or regression with a clear pass condition>

## How to verify
- Tests: <tests to add or extend; the existing tests to follow as a pattern>
- Commands: <build, test and lint commands that must pass>
- Live: <how the result is shown in the running app or service, and what you should see>

## Blocked by
- <ticket reference>: <what it provides>, or "None (can start immediately)"
```

## Standalone ticket

A single ticket with no parent. It is the child template with the parent's sections folded in, so it is the complete brief on its own.

```markdown
# <Title: the outcome this ticket delivers>

Repository: <repo>.

## Problem and goal
<What is wrong or missing today, for whom, and what is true when this ticket is done.>

## Context
<How the code behaves today where this change lands (classes, modules, flows, existing tests).>

## What to build
<Behaviour, contracts, names and steps, precise enough that two agents would build the same thing.>

## Decisions
- <Decision>. Why: <reason>.

## Rejected approaches
- <Route an agent could plausibly take>. Not this, because: <reason>.

## Terms
- <Term>: <meaning>, or None.

## Out of scope
- <What an agent could plausibly add here but must not>

## Acceptance criteria
- [ ] <Observable result in a concrete situation>

## How to verify
- Tests: <tests to add or extend; the existing tests to follow as a pattern>
- Commands: <build, test and lint commands that must pass>
- Live: <how the result is shown, and what you should see>

## Blocked by
- <ticket reference>: <what it provides>, or "None (can start immediately)"
```

For a ticket that only a person can complete, replace *What to build* with **Action** (what the person does) and *How to verify* with **Done when** (what confirms it, for example a store status or a dated sign-off).
