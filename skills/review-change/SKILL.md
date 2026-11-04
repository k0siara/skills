---
name: review-change
description: "Use to get an independent review of a change against its task, such as a local branch before opening a PR: business context from the task source, rule-to-implementation-and-test traceability, technical and architecture review by reviewers who did not write the code, verified findings and a PASS, ISSUES or INCONCLUSIVE verdict. Also the review core that `review-pr` runs on someone else's PR. Read-only: it never edits, commits, pushes or publishes; the author applies fixes. Triggers: review-change, /review-change, review my branch before the PR, pre-PR review, independent review of this change."
---

# Review change

Review a finished change against its task. Intent comes first, then code. A finding counts only when it is confirmed in the code or the sources. Nothing in this skill edits code, commits, pushes, publishes comments or writes to a tracker.

## Independence

The author checks what it meant to build, so the review comes from someone else.

- Prefer running this whole skill in an agent that did not write the change, such as `review` (`deliver-pr` does this). The workspace instructions may name another.
- If the author runs it, the author only gathers inputs, fills the traceability table and verifies findings. The technical and architecture reviews still come from separate reviewers.
- **Reviewers:** the ones the workspace instructions name. Otherwise two `review` agents, started by name with your harness's subagent tool (in OMP `task` with `agent: "review"`, in Claude Code the Agent tool with `subagent_type: "review"`). `setup-k0siara-skills` creates that agent and decides its model; never pass a model yourself. If it does not exist or the tool cannot select it by name, start two independent read-only subagents, preferably on a different model family than the author's. Never use a harness's bundled generic reviewer instead.
- If the instructions or the caller require reviewers that are unavailable, stop with `INCONCLUSIVE` and report the blocker. Do not replace them with your own review.

## Inputs

- Worktree and base ref. Review the committed `HEAD`; uncommitted changes are a blocker to report.
- Task brief `task.md`, or a task ID or link to read.
- Optional: the draft or published PR title and body, the latest `verify-changes` report, CI check results.
- Optional, for an existing PR: its discussion (general comments, review bodies, inline threads with replies).
- Artifacts directory: the one in `task.md` or given by the caller, else `$TMPDIR/review-change/<repo>-<branch>/`.

## 1. Collect the change

1. Write `git diff <base>...HEAD` to `pr.diff` in the artifacts directory.
2. Note the changed files with a one-line summary each, the diffstat and the head SHA. Do not paste the full diff into your context.

## 2. Business context, before the diff

Write `business-context.md` in the artifacts directory with [`references/business-context.md`](references/business-context.md), before you open the diff or the changed code. Do not fit the intent to the implementation.

1. **Sources, complete and read-only:** the task (title, description, acceptance criteria, status, every comment including resolved threads), its parent and project, relations, and linked documents that explain requirements or scope. The PR body is a source too. Without a task ID, look for one only in the PR body; never search for the task by its content, since you may attach the wrong one. A missing task is a mismatch.
2. **Classify the PR discussion**, when there is one. Decisions, requirement clarifications, scope changes and design rationale, whoever wrote them, go into the context with source and quote. Remarks about the code (bugs, style, suggestions) go on an "earlier remarks" list for the caller and never to the reviewers, so their assessments stay independent. Split a mixed entry. Never hide a business decision for the sake of independence.
3. **Compare** the task, the PR body and the changed-file list: goals described differently, criteria missing from the PR body, scope wider or narrower than the task, repository areas the task does not explain, and gaps such as an empty PR body or no criteria.

The reviewers read this file, check its quotes and may dispute your interpretation (`context_challenges`).

## 3. Review

**Project knowledge** (for you and every reviewer): in the worktree, `AGENTS.md` and `CLAUDE.md` at the repository root and in each directory on the path of a changed file, plus the documents, checklists and architecture decisions they point to for those file types. Conditional sections about any stage of a change (planning, implementation, hand-off, review) apply to the review too. Do not look for documents beyond these references. Read this knowledge before starting the reviewers; step 4 needs it.

**Common reviewer input:** the project-knowledge rule above, verbatim; the worktree path; the `pr.diff` path; the `business-context.md` path; the changed files with summaries; areas needing attention. Never pass the earlier remarks or one reviewer's results to the other. Reviewers only read and never touch Git or GitHub.

1. **Start both reviewers in parallel**, in one subagent call when the tool allows. Each reviewer's task is the full text of its reference file, read by you and passed verbatim, plus the common input:
   - **Technical:** [`references/technical.md`](references/technical.md)
   - **Architecture:** [`references/architecture.md`](references/architecture.md)

   In OMP, one `task` call with both reviewers, each with the scope of its checklist as `solutionSpace`:

   ```javascript
   task({
     context: "<common input>",
     tasks: [
       { name: "ReviewTechnical", agent: "review", task: "<full text of references/technical.md>",
         solutionSpace: "Technical correctness, edge cases, error paths, test quality, reliability, security, performance, logging and monitoring; findings open" },
       { name: "ReviewArchitecture", agent: "review", task: "<full text of references/architecture.md>",
         solutionSpace: "Architecture, project rules, boundaries, patterns, design principles incl. KISS, error architecture, contracts, pattern-change justification; findings open" }
     ]
   })
   ```

   When a report lacks a section, a required field or a coverage row, ask that reviewer for it before step 4.
2. **Traceability, while the reviewers work.** For every rule and scenario in `business-context.md`, including those outside the criteria, fill: `rule | source | implementation (file:line or none) | test and the condition its assertion checks (or none) | result (met / partial / not met / cannot assess) | gap`. Judge whether each test would fail if the rule were implemented wrongly: an inverted condition, a shifted boundary, a skipped branch. Trace important callers, dependencies and consumers outside the diff for broken existing behavior. List changes beyond the agreed scope and requirements without an implementation.
3. **Tests.** Keep test code quality separate from test results. Take results from the `verify-changes` report and the CI checks; run tests yourself only in the worktree, locally, without external effects. Mark anything not run. Green CI or high coverage does not prove a rule is implemented.
4. **Observations outside your areas.** Write down every architecture, pattern or technical remark you notice while reading, with `file:line` and what you compare it to. Do not judge it yet.

Your coverage areas: `business context`, `rules → implementation`, `rules → tests`, `scope`, `existing behavior`, `test execution`.

## 4. Verify the findings

1. Confirm each reviewer finding in the code and sources, or reject it. For `documented` and `convention`, open the document or the reference files; for `principle`, confirm the stated effect in the code; for `missing_justification`, confirm the justification is absent from the sources and the docs; for `test_gap`, confirm the missing test or weak assertion; for `observability_gap`, confirm the project uses the named tool. Reject behavior the business context or the docs explicitly allow. Correct wrong priorities or lines. Reject what you cannot confirm.
2. Match each of your observations against the findings. Merge the covered ones. Send each uncovered one to the right reviewer for a judgment and wait; if that reviewer is gone, judge it yourself with the same criteria. Every observation ends as a finding or a rejected finding with the reason.
3. Check each `context_challenge` in the sources. Fix accepted ones in `business-context.md` and recompute the affected table rows; list rejected ones with the reason.
4. Merge findings with the same root cause into one with the higher priority (lower number) and all sources. Different problems on the same line stay separate.
5. Merge coverage. An area a reviewer did not report is `unverified`, with the reason "missing from the reviewer's result".

Priorities: P0 blocks release, P1 fix in the next cycle, P2 fix eventually, P3 nice to have.

## 5. Report

Verdict:

- `PASS`: no confirmed defect, no unmet rule, every area covered.
- `ISSUES`: at least one confirmed finding or table gap.
- `INCONCLUSIVE`: a required reviewer was unavailable or an area stayed unverified.

Write the report to `review-change.md` in the artifacts directory, starting with the reviewed `HEAD` SHA and the verdict, and return it:

1. **Findings** in three groups. Each has priority, location (`file:line`, `task <ID>` or `PR description`), description, evidence, suggested fix, source reviewer (architecture findings also their `reference`), and a handling class for the author: `fix`, `out of scope`, `justify or simplify` (for `missing_justification`), `fix PR description` or `tracker correction` (for task vs PR mismatches), or `ask user` (needs a breaking change or contradicts the task).
   - Confirmed problems: `defect`, `observability_gap`, rules not met.
   - Gaps in requirements, tests and justification: `test_gap`, table gaps, `missing_justification`, ambiguities, task vs PR mismatches.
   - Architecture suggestions: `deviation`.
2. **Traceability table.**
3. **Tests:** read, run (command and result), confirmed by CI, not run.
4. **Coverage:** `area | reviewer | result | evidence or reason`, where the result is `checked`, `issue found`, `not applicable` or `unverified`. List unverified parts under the table as verification limits.
5. **Rejected findings,** one line each with the reason.
6. **Earlier remarks,** when there was a PR discussion: the list from step 2, for the caller.
7. **Summary:** two or three sentences on the change's overall quality.
