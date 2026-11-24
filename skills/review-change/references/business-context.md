# business-context.md

Write it before you open the diff or the changed code. Every rule, decision and claim has a source (comment or thread link, `task <ID> description`, `task <ID> comment <link>`, `PR description`, `files`) and a status: `source` when stated explicitly, `interpretation` when it is your inference. Requirements outside the acceptance criteria are recorded the same way.

An entry that prescribes a mechanism, a configuration, a code shape or a test-only parameter (e.g. "use pattern X", "short timeout in the test") has the type `implementation hint` and names, in the same row, the effect it serves. A hint justifies only that effect, never the code shape or production configuration.

```markdown
# Business context: <repo> <branch or PR #N>
## Sources
- sources read, with links and the number of comments/threads; sources unavailable
## Goal and non-negotiables
- concise user-visible goal and every binding behavior, compatibility, security, accessibility and scope constraint, with source/rule IDs; distinguish missing information from established facts
- effects required by implementation hints, not the hints' proposed code shape; include binding constraints even when they make simplification harder
- this is the simplification reviewer's starting context, not an implementation plan; it checks the full context after inspecting code and before reporting
## Problem and value
- the problem, for whom, the value of the change [source]
## Behavior before and after
- before: ... / after: ... [source]
## Rules and scenarios
| ID | rule or scenario | type (criterion / rule / constraint / exception / excluded scenario / implementation hint) | source | quote | status |
## Decisions
| ID | decision | type (effect / implementation hint) | rationale | source | quote | status |
## Scope and exclusions
- declared scope (task / PR) and explicit exclusions, each with its source; none -> "none"
## Ambiguities, gaps and contradictions
- ...
## Task vs PR description mismatches
| priority | location (`task <ID>` / `PR description`) | description | suggested correction |
```
