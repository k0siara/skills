# Spec template

Required sections are marked *(required)*. Keep them even when short. The others are written when they apply.

```markdown
# <Title: the outcome, not the implementation>

- Status: Draft | Approved
- Owner: <who decides>
- Date: <YYYY-MM-DD>
- Links: <task, discussion, designs, related specs>

## Problem (required)
Who has the problem, what goes wrong for them today, and how we know (data, feedback, support tickets).

## Goal and success measure (required)
What changes for the user or the business, and the signal that shows it worked: a metric, an event or an observable behaviour. No threshold yet: say when it is set.

## Solution (required)
The solution from the user's point of view, in a few sentences. No implementation.

## Scenarios (required)
- S1. <actor> <does what> → <observable result>
- S2. Edge case: ...
- S3. Failure: <what goes wrong> → <what the user sees, what the system does>

## Current state
How the system behaves today in the parts this change touches, by module and contract name. What already exists of this goal, and earlier decisions this spec replaces. The prior art this design follows.

## Design decisions (required)
- <decision>: <why> (<YYYY-MM-DD>, <who>)
- Contracts: API, schema, events, stored data that change, with their shape.
- State: which module owns each new or changed piece of state.
- Alternatives considered: <shape> — rejected because <reason>.

## Compatibility and rollout (required, `None` when nothing applies)
- Clients already installed: what an old app version sees with the new backend, and what a new app sees with the old backend.
- Stored data: migration, backfill, what happens to existing records.
- Reversibility: can the change be rolled back; what cannot be undone once released.
- Release order: which part ships first; waits such as store review.
- Flags: feature flag or kill switch, and its default.
- Also check: analytics events, translations and markets, permissions and privacy, cost or limits of external services.

## Testing decisions (required)
- Seams: where each scenario is tested, at the highest seam that can observe it.
- Prior art: the existing tests the new ones follow.
- Live check: how the change is proven in the running app or service.

## Out of scope (required)
- <what someone could expect but will not get, and where it goes if it is planned later>

## Risks
- <risk> → <mitigation or the signal that shows it is happening>

## Open questions (required, `None` when empty)
- [blocking | non-blocking] <question> — answers: <who>
```
