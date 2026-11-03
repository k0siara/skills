---
name: pre-pr-review
description: "Use before opening a PR for a change on a local branch, to get an independent review against its task: business context from the task source, rule-to-implementation-and-test traceability, technical and architecture review by reviewers who did not write the code, verified findings and a PASS, ISSUES or INCONCLUSIVE verdict. Read-only: it never edits, commits, pushes or publishes; the author applies fixes. Triggers: pre-pr-review, /pre-pr-review, review my branch before the PR, independent review before PR."
---

# Pre-PR review

Review a finished local change before it becomes a PR. Intent comes first, then code. A finding counts only when it is confirmed in the code or the sources.

## Independence

The author checks what it meant to build, so the review comes from someone else.

- Prefer running this whole skill in an agent that did not write the change, such as `k0siara-reviewer` (`deliver-pr` does this). The workspace instructions may name another.
- If the author runs it, the author only gathers inputs, fills the traceability table and verifies findings. The technical and architecture reviews still come from separate reviewers.
- Reviewers: the ones the workspace instructions name (agent definitions, templates, another harness). Otherwise two `k0siara-reviewer` agents, started by name with your harness's subagent tool (in OMP `task` with `agent`, in Claude Code the Agent tool with `subagent_type`). `setup-k0siara-skills` creates that agent and decides its model; never pass a model yourself. If it does not exist or the tool cannot select it by name, spawn two independent read-only subagents, preferably on a different model family than the author's.
- If the instructions name reviewers and they are unavailable, stop with `INCONCLUSIVE` and report the blocker. Do not replace them with your own review.

Nothing in this skill edits code, commits, pushes, publishes comments or writes to a tracker.

## Inputs

- Worktree and base ref. Review the committed `HEAD`; uncommitted changes are a blocker to report.
- Task brief `task.md`, or a task ID or link to read.
- Optional: draft PR title and body (`pr-body.md`) and the latest `verify-changes` report.
- Artifacts directory: the one in `task.md`, else `$TMPDIR/pre-pr-review/<repo>-<branch>/`.

## 1. Collect the change

1. Write `git diff <base>...HEAD` to `pr.diff` in the artifacts directory.
2. Note the changed files with a one-line summary each, the diffstat and the head SHA. Do not paste the full diff into your context.

## 2. Business context, before the diff

Write `business-context.md` before you open the diff or the changed code. Do not fit the intent to the implementation.

1. **Sources, complete and read-only:** the task (title, description, acceptance criteria, all comments including resolved threads), its parent and project, relations, and linked documents that explain requirements or scope. The draft PR body is a source too.
2. **Compare** the task, the draft PR body and the changed-file list: goals described differently, criteria missing from the PR body, scope wider or narrower than the task, repository areas the task does not explain, and gaps such as an empty PR body or no criteria.
3. **Record** each rule, decision and claim with its source and a status: `source` when stated explicitly, `interpretation` when it is your inference. Separate the required effect from how to achieve it: an entry that prescribes a mechanism, a code shape or a test-only parameter is an `implementation hint` and names the effect it serves.

```markdown
# Business context: <repo> <branch>
## Sources
- each source read, with a link; sources unavailable
## Problem and value
- the problem, for whom, the value of the change [source]
## Behavior before and after
- before: ... / after: ... [source]
## Rules and scenarios
| ID | rule or scenario | type (criterion / rule / constraint / exception / excluded scenario / implementation hint) | source | quote | status |
## Decisions
| ID | decision | type (effect / implementation hint) | rationale | source | quote | status |
## Scope and exclusions
- declared scope and explicit exclusions, each with its source; none -> "none"
## Ambiguities, gaps and contradictions
- ...
## Task vs PR description mismatches
| priority | location (task / PR description) | description | suggested correction |
```

## 3. Review

**Project knowledge** (for you and every reviewer): `AGENTS.md` and `CLAUDE.md` at the repository root and in each directory on the path of a changed file, plus the documents, checklists and architecture decisions they point to for those file types. Conditional sections about any stage of a change (planning, implementation, hand-off, review) apply to the review too.

**Common reviewer input:** the project-knowledge rule above, verbatim; the worktree path; the `pr.diff` path; the `business-context.md` path; the changed files with summaries; areas needing attention. Never pass one reviewer's results to the other.

1. Start both reviewers in parallel. Each reads only and reports in its own declared schema when it has one; otherwise in this one: findings with `kind` (`defect`, `test_gap`, `observability_gap`, `deviation`, `missing_justification`), priority (P0 blocks release, P1 fix in the next cycle, P2 fix eventually, P3 nice to have), `file:line`, evidence, `reference` (`documented`, `convention` or `principle`), suggested fix; coverage per area; `context_challenges` (disputes with business-context.md); a verdict.
   - **Technical:** correctness, edge cases, complete error paths, test quality, reliability, security, performance, logging and monitoring with the tools the project uses.
   - **Architecture:** project instructions and documentation, responsibility boundaries, consistency with at least two files of the same role and with existing precedents for the same mechanism, design principles including KISS, error architecture, contracts, and justification for new or changed patterns.
2. **Traceability, while the reviewers work.** For every rule and scenario in `business-context.md`, including those outside the criteria, fill: `rule | source | implementation (file:line or none) | test and the condition its assertion checks (or none) | result (met / partial / not met / cannot assess) | gap`. Judge whether each test would fail if the rule were implemented wrongly: an inverted condition, a shifted boundary, a skipped branch. Trace important callers, dependencies and consumers outside the diff for broken existing behavior. Keep test code quality separate from test results; take results from the `verify-changes` report and mark anything not run.
3. Write down every observation outside your areas (architecture, patterns, technical correctness) as you read, with `file:line` and what you compare it to. Do not judge it yet.

## 4. Verify the findings

1. Confirm each reviewer finding in the code and sources, or reject it. For `documented` and `convention`, open the document or the reference files; for `principle`, confirm the stated effect in the code; for `missing_justification`, confirm the justification is absent from the sources and the docs; for `test_gap`, confirm the missing test or weak assertion; for `observability_gap`, confirm the project uses the named tool. Correct wrong priorities or lines. Reject what you cannot confirm.
2. Match each of your own observations against the findings. Merge the covered ones. Send each uncovered one to the right reviewer for a judgment; if that reviewer is gone, judge it yourself with the same criteria.
3. Check each `context_challenge` in the sources. Fix accepted ones in `business-context.md` and recompute the affected table rows.
4. Merge findings with the same root cause into one with the higher priority and all sources. Different problems on the same line stay separate.
5. Merge coverage. An area a reviewer did not report is `unverified`.

## 5. Report

Verdict:

- `PASS`: no confirmed defect, no unmet rule, every area covered.
- `ISSUES`: at least one confirmed finding or table gap.
- `INCONCLUSIVE`: a required reviewer was unavailable or an area stayed unverified.

Write the report to `pre-pr-review.md` in the artifacts directory, starting with the reviewed `HEAD` SHA and the verdict, and return it:

1. **Findings** in three groups. Each has priority, location, description, evidence, suggested fix, source reviewer, and a handling class for the author: `fix`, `out of scope`, `justify or simplify` (for `missing_justification`), `fix PR description` or `tracker correction` (for task vs PR mismatches), or `ask user` (needs a breaking change or contradicts the task).
   - Confirmed problems: `defect`, `observability_gap`, rules not met.
   - Gaps in requirements, tests and justification: `test_gap`, table gaps, `missing_justification`, ambiguities, task vs PR mismatches.
   - Architecture suggestions: `deviation`.
2. **Traceability table.**
3. **Tests:** read, run (command and result), not run.
4. **Coverage:** `area | reviewer | result | evidence or reason`.
5. **Rejected findings,** one line each with the reason.
6. **Summary:** two or three sentences on the change's overall quality.
