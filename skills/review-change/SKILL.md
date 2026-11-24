---
name: review-change
description: "Use to get an independent, read-only review of a finished change: task traceability, technical and architecture checks, and a separate skeptical simplification reviewer that challenges unnecessary code. Returns verified findings and PASS, ISSUES or INCONCLUSIVE. Review core of `review-pr` and the pre-PR review in `deliver-pr`. Triggers: review-change, /review-change, review my branch before the PR, pre-PR review, independent review of this change."
---

# Review change

Review a finished change for correctness, architecture and the simplest complete solution. The lead establishes intent before reading code; a separate simplification reviewer challenges the implementation rather than treating the task's design sketch as the answer. A finding counts only when confirmed in code or sources. Nothing in this skill edits code, commits, pushes, publishes comments or writes to a tracker.

## Independence

The author checks what it meant to build, so the review comes from someone else.

- Prefer running this whole skill in an agent that did not write the change, such as `review` (`deliver-pr` does this). The workspace instructions may name another.
- If the author runs it, the author only gathers inputs, fills the traceability table and verifies findings. Technical, architecture and simplification assessments still come from independent reviewers, not from the author.
- **Reviewers:** how many and which are set in step 3. The default is `review` agents, started by name with your harness's subagent tool (in OMP `task` with `agent: "review"`, in Claude Code the Agent tool with `subagent_type: "review"`). `setup-k0siara-skills` creates that agent and decides its model; never pass a model yourself. If it does not exist or the tool cannot select it by name, start independent read-only subagents instead, preferably on a different model family than the author's. Never use a harness's bundled generic reviewer instead.
- If a required reviewer or pass is unavailable, stop with `INCONCLUSIVE` and report the blocker. Do not replace it with your own review or silently omit simplification.

## Inputs

- Worktree and base ref. Review the committed `HEAD`; uncommitted changes are a blocker to report.
- Task brief `task.md`, or a task ID or link to read.
- Optional: the draft or published PR title and body, the latest `verify-changes` report, CI check results.
- Optional, for an existing PR: its discussion (general comments, review bodies, inline threads with replies).
- Artifacts directory: the one in `task.md` or given by the caller, else the parent of the worktree when it is `<main-checkout>/.work/<purpose>/<id>/worktree`, else `<main-checkout>/.work/review-change/<branch>/`, inside `<main-checkout>/.work/` (`<main-checkout>` is the repository's main working tree; add `.work/` to `$(git rev-parse --git-common-dir)/info/exclude` if it is not there).

## 1. Collect the change

1. Write `git diff <base>...HEAD` to `pr.diff` in the artifacts directory.
2. Note the changed files with a one-line summary each, the diffstat and the head SHA. Do not paste the full diff into your context.

## 2. Business context, before the diff

Write `business-context.md` in the artifacts directory with [`references/business-context.md`](references/business-context.md), before you open the diff or the changed code. Do not fit the intent to the implementation.

1. **Sources, complete and read-only:** the task (title, description, acceptance criteria, status, every comment including resolved threads), its parent and project, relations, and linked documents that explain requirements or scope. The PR body and the commit messages (`git log <base>..HEAD`) are sources too. Without a task ID, look for one only in the PR body and the issues the PR links; never search for the task by its content, since you may attach the wrong one. A missing task is a mismatch; intent and scope then come from the PR body, the linked issue and the commits.
2. **Classify the PR discussion**, when there is one. Decisions, requirement clarifications, scope changes and design rationale, whoever wrote them, go into the context with source and quote. Remarks about the code (bugs, style, suggestions) go on an "earlier remarks" list for the caller and never to the reviewers, so their assessments stay independent. Split a mixed entry. Never hide a business decision for the sake of independence.
3. **Compare** the task, the PR body and the changed-file list: goals described differently, criteria missing from the PR body, scope wider or narrower than the task, repository areas the task does not explain, and gaps such as an empty PR body or no criteria.

The reviewers check this file's quotes and may dispute your interpretation (`context_challenges`). The simplification reviewer first reads only its **Goal and non-negotiables** section, examines code and alternatives, then checks the full context before reporting; it does not perform task traceability.

## 3. Review

**Project knowledge** (for you and every reviewer): in the worktree, `AGENTS.md` and `CLAUDE.md` at the repository root and in each directory on the path of a changed file, plus the documents, checklists and architecture decisions they point to for those file types. Conditional sections about any stage of a change (planning, implementation, hand-off, review) apply to the review too. Do not look for documents beyond these references. Read it while the reviewers work; step 4 needs it.

**Common reviewer input:** the project-knowledge rule above, verbatim; the worktree path; the `pr.diff` path; the `business-context.md` path; the changed files with summaries; areas needing attention. Follow each checklist's context-reading order. Never pass earlier remarks or another reviewer's results to any reviewer. Reviewers only read and never touch Git or GitHub.

**Classify the change, before starting any reviewer.** A change is *small and safe* when both hold:

- It has at most 200 changed lines (added + removed) in `pr.diff`, not counting lockfiles, generated files (marked as generated or in build/dist directories) and binary files. `git diff --numstat <base>...HEAD` gives the counts per file; binary files show `-`.
- It touches no risk area, judged by paths and diff content: public API and contracts (`*Request`/`*Response`, endpoints, schemas, events), migrations and database schema, authorization and authentication, secrets and keys, deployment and CI configuration (`.github/workflows`, deploy files, infrastructure), permissions and personal data. A risk area is a part of the change where a mistake breaks working clients, data or security.

When in doubt, the change is risky. Anything not small and safe is risky.

**Precedence:** workspace instructions or the caller may override the technical/architecture split with an explicit reviewer count or named checklist assignments. Simplification always has a separate reviewer who takes neither other checklist. Two reviewers means combined Technical + Architecture and separate Simplification; three means one per checklist. A count below two cannot satisfy independence: report `INCONCLUSIVE` rather than dropping a pass. Naming an agent only chooses who reviews, not the count.

1. **Start all reviewers together**, in one subagent call when the tool allows. Pass each the full text of its checklist(s), read by you and passed verbatim, plus the common input:
   - **Small and safe: two reviewers.** One takes [`references/technical.md`](references/technical.md) then [`references/architecture.md`](references/architecture.md), returning separate Technical and Architecture reports with coverage rows kept separate. The other takes [`references/simplification.md`](references/simplification.md).
   - **Risky: three reviewers.** Separate Technical, Architecture and Simplification reviewers, each taking its reference above.
   - **Simplification is mandatory for both classes**, including changes with no suspected bug. Use another fresh instance of the configured `review` agent, not a new agent type, model override or optional roast mode.

   In OMP: one `task` call, one entry per reviewer with `agent: "review"` and its checklist's scope as `solutionSpace`.

   Missing report, section, required field or coverage row: ask that reviewer to complete it before step 4. If unavailable, keep the missing pass `unverified`; never report full `PASS`.
2. **Traceability, while the reviewers work.** For every rule and scenario in `business-context.md`, including those outside the criteria, fill: `rule | source | implementation (file:line or none) | test and the condition its assertion checks (or none) | result (met / partial / not met / cannot assess) | gap`. When the `verify-changes` report or the PR body has an acceptance-criteria evidence table, check that each piece of evidence exists and proves its criterion instead of interpreting the criterion anew. Judge whether each test would fail if the rule were implemented wrongly: an inverted condition, a shifted boundary, a skipped branch. Trace important callers, dependencies and consumers outside the diff for broken existing behavior. List changes beyond the agreed scope and requirements without an implementation.
3. **Tests.** Keep test code quality separate from test results. Take results from the `verify-changes` report and the CI checks; run tests yourself only when neither a `verify-changes` report for this `HEAD` SHA nor CI results on the head SHA exist, only the affected ones, in the worktree, without external effects. Mark anything not run. Green CI or high coverage does not prove a rule is implemented.
4. **Observations outside your areas.** Write down every architecture, pattern or technical remark you notice while reading, with `file:line` and what you compare it to. Do not judge it yet.

Your coverage areas: `business context`, `rules → implementation`, `rules → tests`, `scope`, `existing behavior`, `test execution`.

## 4. Verify the findings

1. Confirm each reviewer finding in the code and sources, or reject it. For `documented` and `convention`, open the document or the reference files; for `principle`, confirm the stated effect in the code; for `missing_justification`, confirm the justification is absent from the sources and the docs; for `test_gap`, confirm the missing test or weak assertion; for `observability_gap`, confirm the project uses the named tool; for `design_suggestion`, confirm the stated cost in the code and that the alternative still meets every rule in `business-context.md` and no binding decision or constraint requires the current code. Reject behavior the business context or the docs explicitly allow. Correct wrong priorities or lines. Reject what you cannot confirm.
2. Match your observations against the findings and merge duplicates. Send uncovered observations to the responsible reviewer in one message per reviewer: bugs to Technical, boundaries/contracts/rule deviations to Architecture, unnecessary code and naming clarity to Simplification. Route the simplification report's out-of-scope observations the same way; do not discard a potential defect because its discoverer owns only design suggestions. Wait for judgment; if that reviewer is gone, judge the observation yourself under the same evidence criteria. Every observation ends as a finding or a rejected finding with the reason.
3. Check each `context_challenge` in the sources. Fix accepted ones in `business-context.md` and recompute the affected table rows; list rejected ones with the reason.
4. Merge findings with the same root cause into one with the higher priority (lower number) and all sources. Different problems on the same line stay separate.
5. Merge coverage from all three passes, including every Simplification area even when it found nothing. Missing coverage is `unverified`, with the reason "missing from the reviewer's result". A `lean` or `simplification_opportunities` verdict says nothing about correctness; only this lead assigns the overall review verdict.
6. **Blocking or follow-up,** for every confirmed finding and table gap. It blocks only when it shows an acceptance criterion broken or not implemented (without criteria: behavior the PR body, the linked issue or the commits promise), failed verification, red CI or failing tests, a regression of existing behavior, or a security problem or data loss. A blocking finding names the criterion or behavior it breaks and is P0–P2 (raise a P3 to P2). Everything else (edge cases outside the scope, style, improvements, test, justification or description gaps, design suggestions) is a follow-up and P3. A missing task, criteria table or evidence table, or a PR body in another format, never blocks by itself. Mark a finding whose pattern a linter or static check could catch with `[LINT?]` and one sentence proposing the rule.

Priorities: P0 blocks release, P1 fix in the next cycle, P2 fix eventually, P3 nice to have.

## 5. Report

Verdict:

- `PASS`: no blocking finding, every area covered.
- `ISSUES`: at least one blocking finding.
- `INCONCLUSIVE`: a required reviewer was unavailable or an area stayed unverified.

Write `review-change.md` in the artifacts directory, starting with the reviewed `HEAD` SHA, verdict and classification: `Classification: <small and safe|risky> (<N> lines, risk areas: <list|none>), <2|3> reviewers`, or `set by caller` instead of the parenthesis. Name the Technical, Architecture and Simplification assignments so a skipped pass cannot hide behind the count.

1. **Blocking findings.** Each has priority, location (`file:line`, `task <ID>` or `PR description`), the criterion or behavior it breaks, description, evidence, suggested fix, source reviewer (architecture findings also their `reference`), and a handling class for the author: `fix`, `out of scope`, `justify or simplify` (for `missing_justification`), `fix PR description` or `tracker correction` (for task vs PR mismatches), `author's call` (for `design_suggestion`), or `ask user` (needs a breaking change or contradicts the task).
2. **Follow-up:** every other finding, with the same fields except the broken criterion, in four groups. This skill only proposes them; the caller decides what to fix or file as issues.
   - Problems: `defect`, `observability_gap`, rules not met.
   - Gaps in requirements, tests and justification: `test_gap`, table gaps, `missing_justification`, ambiguities, task vs PR mismatches.
   - Architecture deviations: `deviation`.
   - Design suggestions: `design_suggestion`, from any reviewer; retain the current cost, concrete alternative, behavior preserved and trade-off. Being correct does not make unnecessary complexity exempt from review.
3. **Traceability table.**
4. **Tests:** read, run (command and result), confirmed by CI, not run.
5. **Coverage:** `area | reviewer | result | evidence or reason`, where the result is `checked`, `issue found`, `not applicable` or `unverified`. List unverified parts under the table as verification limits.
6. **Rejected findings,** one line each with the reason.
7. **Earlier remarks,** when there was a PR discussion: the list from step 2, for the caller.
8. **Summary:** two or three sentences on overall quality. Include the simplification result: worthwhile changes proposed, none found, or unverified. No quota of criticism and no invented line-saving estimates.
