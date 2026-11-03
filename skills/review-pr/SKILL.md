---
name: review-pr
description: "Code review of someone else's GitHub PR: detached review worktree, source-backed business context from the task and PR discussion, rule-to-implementation-and-test traceability, technical and architecture reviewers (two `review` subagents from setup-k0siara-skills, each prompted with its checklist), verified findings, a review coverage report and GitHub comments published only after the user approves them. Triggers: review-pr <PR>, /review-pr <PR-link>, review PR, review this PR, zrób review, sprawdź PR."
---

# Review PR

## Roles

Three agents run the review:

| Agent | Instructions | Responsibility |
|---|---|---|
| Lead (you) | this skill | sources and business context, rule implementation and test coverage, scope, test and CI results, verifying and merging findings, every Git/GitHub operation and every user approval |
| Technical | `references/technical.md` | correctness, edge cases, error paths, test quality, reliability, security, performance, logging and monitoring |
| Architecture | `references/architecture.md` | project instructions and docs, responsibility boundaries, patterns, design principles including KISS, error architecture, contracts, justification of new or changed patterns |

The reviewer checklists and report formats live only in `references/`; this skill describes the process, inputs, outputs and the lead's duties. Do not use a harness's bundled generic reviewer instead.

Order: shared business context first (step 2), then both reviewers in parallel and independently of each other, while the lead checks business fit and tests (step 3).

## Workspace instructions

Before the first Git, `gh` or GitHub operation, read the instructions that apply to the repository: `AGENTS.md` and `CLAUDE.md` in the repository and its parent workspace, plus the files they point to for Git/GitHub, tracker or review rules. Follow them for every Git/`gh`/GitHub operation, reads included (PR data, diff, fetch, worktree, publishing, cleanup). Where they set something below, they win:

- which repositories or PRs are reviewed at all; for a PR they exclude, stop before step 1 and tell the user;
- worktree location; default `<main-checkout>/../<repo-name>.worktrees/pr-<N>`;
- artifacts directory; default `$TMPDIR/review-pr/<repo>-pr-<N>/`;
- how to read tasks from the tracker;
- PR comment rules (language, required prefix or marker); default English, no prefix.

Write descriptions, the report and questions in the user's language.

Every finding has a priority: P0 blocks release, P1 fix in the next cycle, P2 fix eventually, P3 nice to have.

Keep a todo list with steps 1-5.

## Reviewers

Both reviewers run in the `review` agent, which `setup-k0siara-skills` creates and whose model it pins; never pass a model in the call. `review` has no instructions of its own: each reviewer's prompt is the full text of its file in `references/` (relative to this skill's directory), read by you and passed verbatim, plus the common input (step 3). When the subagent tool does not know `review`, stop before step 3 and report the blocker to the user (`setup-k0siara-skills` creates it); do not replace it with another agent or your own review.

## 1. Check out the PR

Prepare the review yourself. Allowed: reads, fetch, the review worktree and writing review artifacts. Not allowed: application changes, commit or push, publishing, notifications, tracker writes.

1. Read the whole PR: number, author, state (draft, mergeable), head and base, head SHA, title, body, labels, and every CI check on the head SHA (name, status, conclusion, job link). Note checks still running and move on; do not wait for them. Take the task ID from the title or branch.
2. Read every PR comment with its replies, from three sources: general PR comments, the body of every review, and inline threads (GraphQL `reviewThreads`: file, line, every comment in the thread, `isResolved`, `isOutdated`). Paginate every list to the end, comments inside a thread included. You classify them in step 2.
3. Worktree only at the location from the workspace instructions. Fetch `origin pull/<N>/head`. The worktree is always detached at the head SHA, never on a local PR branch: no path → `worktree add --detach`; clean → `checkout --detach`; local changes → no reset, blocker. Worktree HEAD different from the head SHA → blocker.
4. Write the full PR diff to `pr.diff` in the artifacts directory (overwrite). In that directory you create and overwrite only `pr.diff` and `business-context.md` (step 2); leave every other file alone.
5. Record: PR metadata, the PR body verbatim, the task ID (or that there is none), checks (name, status, conclusion, link), threads and comments one line per thread (location, author, issue raised, replies, state, link), the worktree path, whether it was created now, the head SHA (and the previous SHA when reusing a worktree), the changed files, the diffstat, the `pr.diff` path, blockers. Do not paste the full diff into your context.

Read code from that worktree path. A missing task ID or an empty PR body does not block the review: pass it on as a fact.

## 2. Business context, before the diff

Intent first, then code: write `business-context.md` before you open the diff or the changed code. Do not fit the intent to the implementation.

1. **Sources, complete and read-only** (no status changes, comments, relations or other tracker writes), read the way the workspace instructions describe for the tracker:
   - the task: title, description, acceptance criteria, status and every comment including resolved threads; list comments separately when the task view may not show all of them;
   - its parent and project, if any: the higher-level goal;
   - its relations and the documents and links in the task description, only those that explain requirements or scope.

   No task ID from step 1: look for one only in the PR body. Do not search for the task by its content, since you may attach the wrong one; a missing task is a mismatch. From the PR: the body and the comments and threads from step 1.
2. **Classify the discussion** (task comments, general PR comments, review bodies, inline threads with replies):
   - decisions, requirement clarifications, scope changes and design rationale, whoever wrote them → business context, with source and quote;
   - remarks about the code (bugs, style, suggestions) → the "earlier remarks" list, used only in step 4; do not pass it to the reviewers, so their first assessments stay independent.

   Split a mixed entry: the decision goes to the context, the code remark stays separate. Never hide business decisions for the sake of review independence.
3. **Compare** the task, the PR body and the changed files and diffstat: goals described differently, acceptance criteria missing from the PR body, PR scope wider or narrower than the task, repository areas the task does not explain, gaps (empty PR body, no task, no acceptance criteria).
4. **Write** `business-context.md` in the artifacts directory. Every rule, decision and claim has a source (comment or thread link, `task <ID> description`, `task <ID> comment <link>`, `PR description`, `files`) and a status: `source` (stated explicitly) or `interpretation` (your inference). Requirements inside and outside the acceptance criteria are recorded the same way.

   Separate the required effect from how it is achieved. An entry that prescribes a mechanism, configuration, code shape or a test-only parameter (e.g. "use pattern X", "short timeout in the test") gets the type `implementation hint` and names, in the same row, the effect it serves. A hint justifies only that effect, never the code shape or production configuration.

```markdown
# Business context: <repo> PR #<N>
## Sources
- sources read, with links and the number of comments/threads; sources unavailable
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

The reviewers read this file, check the quotes and may dispute your interpretation (`context_challenges`).

## 3. Review

**Project knowledge** (the lead and both reviewers): in the worktree, `CLAUDE.md` and `AGENTS.md` at the repository root and in each directory on the path of a changed file (each only if it exists), plus the documents, checklists and architecture decisions they point to for the changed file types. Conditional sections about any stage of a change (planning, implementation, completion, hand-off to review, review) apply to the review too, with the checklists they point to. Do not look for documents beyond these references. The lead reads this knowledge before starting the reviewers, because step 4 needs it.

**Common input** for each reviewer (`context`): the project-knowledge rule (verbatim, the paragraph above), the worktree path, the `pr.diff` path, the `business-context.md` path, the changed files with a short description of each change, and the areas needing attention from the business context and the file list. Do not pass the earlier PR remarks or the other reviewer's results. Reviewers only read and never touch Git/GitHub; they return missing Git/GitHub data to the lead.

1. Read `references/technical.md` and `references/architecture.md`, then start both reviewers in parallel in one subagent call, each with its file's full text as the task. In OMP:

```javascript
task({
  i: "Running PR review",
  context: "<COMMON INPUT>",
  tasks: [
    { name: "ReviewArchitecture", agent: "review", solutionSpace: "Architecture, project rules, boundaries, patterns, design principles incl. KISS, error architecture, contracts, pattern-change justification; findings open",
      task: "<full text of references/architecture.md>" },
    { name: "ReviewTechnical", agent: "review", solutionSpace: "Technical correctness, edge cases, error paths, test quality, reliability, security, performance, logging and monitoring; findings open",
      task: "<full text of references/technical.md>" }
  ]
})
```

   When a report lacks a section, a field the format requires or a coverage row, ask that reviewer for it (`write agent://<name>`) before step 4.

2. **Business fit and tests (lead).** Without waiting for the reviewers, read `pr.diff` and the code in the worktree and, for every rule and scenario in `business-context.md` (those outside the acceptance criteria too), fill the table:

   `Rule/scenario | source | implementation | test and the asserted condition | result | gap`

   - implementation: `file:line` or `none`;
   - test: `file:line` and the condition its assertion checks, or `none`; judge whether the test would fail if the rule were implemented wrongly (inverted condition, shifted boundary, skipped branch);
   - result: `met` / `partial` / `not met` / `cannot assess`, with evidence or the reason;
   - gap: what is missing in the code, the test or the sources.

   Choose scenarios by the domain and risk of the change. Trace the important callers, dependencies and consumers outside the diff: does the change break existing behavior? List changes beyond the agreed scope and requirements without an implementation.

   **Tests:** keep the assessment of test code separate from its results. Record the tests read, the tests run (command and result; only in the review worktree, locally, without external effects; mark tests not run explicitly) and what the CI checks from step 1 confirm. Green CI or high coverage does not prove a rule is implemented.

   **Observations outside your areas:** write down every remark about architecture, patterns, KISS or technical correctness you notice while reading, at once, on the "lead observations" list (`file:line`, what you noticed, what you compare it to, e.g. a reference file path). Do not judge them in this step and do not dismiss them in your head; step 4 decides.

   Your coverage areas: `business context`, `rules → implementation`, `rules → tests`, `scope`, `existing behavior`, `test execution and CI`, with the statuses from step 4.

## 4. Verify and present the results

1. **Verify the reviewers' findings** in the code and sources: reject false alarms and behavior the business context or the docs explicitly allow; correct a wrong priority or line. For architecture findings check `reference`: for `documented` and `convention`, open the document or the reference files and confirm the rule or pattern exists; for `principle`, confirm the stated effect in the code; for `missing_justification`, confirm in `business-context.md` and the docs that the justification is absent. For `test_gap`, confirm the missing test or weak assertion; for `observability_gap`, confirm the project uses the named tool. Reject what you cannot confirm.
   **Lead observations:** compare each with the reviewers' findings. Merge a covered one into its finding. Send an uncovered one to the right reviewer (`write agent://ReviewArchitecture` or `agent://ReviewTechnical`) asking for a judgment per its checklist, and wait for the answer; when the reviewer is gone, judge it yourself with the same criteria (`reference`, confirmation in the code). Every observation ends as a finding or under "Rejected findings" with the reason.
2. **`context_challenges`:** check each in the sources. Fix accepted ones in `business-context.md`, recompute the affected rows of the step 3 table and list the change in the summary; list rejected ones with the reason.
3. **Merge:** findings with the same root cause are one finding, whatever the line and whichever agent reported them; different problems on the same line stay separate. A merged finding takes the higher priority (lower number) and all sources.
4. **Earlier remarks:** compare the findings with the "earlier remarks" list from step 2. An issue already raised on the PR, in any thread state (resolved or outdated included), gets no new comment; if the problem is still in the code, it stays on the findings list with a link to the existing thread and its state.
5. **CI:** read once more, without waiting, the checks that were running in step 1. A failed check is a technical finding with the cause from the job log and a link; priority by effect (build or tests fail → P0). Propose no GitHub comment for checks, since the author sees their status. List checks still running in the summary.
6. **Coverage:** merge the coverage of all three agents. An area a reviewer did not report is `unverified` with the reason "missing from the reviewer's result".

Write proposed comments in their final published form, following the workspace PR comment rules (language, prefix), so the user approves exactly the text that goes to GitHub.

Report:

1. **Findings** in three groups; each: priority (P0-P3), location (`file:line`, `task <ID>`, `PR description` or the check name), description, evidence, suggested fix, source agent; architecture findings also the source from `reference`; already raised: the thread link and its state.
   - **Confirmed problems:** `defect`, `observability_gap`, rules `not met`, failed CI checks.
   - **Gaps in requirements, tests and justification:** `test_gap`, gaps from the step 3 table, `missing_justification`, ambiguities and contradictions in the sources, task vs PR description mismatches.
   - **Architecture suggestions:** `deviation`.
2. **Rule table** from step 3.
3. **Tests:** read / run (command, result) / confirmed by CI.
4. **Review coverage:** `Area | agent | result | evidence or reason`, where the result is `checked` (with evidence), `issue found` (with evidence and impact), `not applicable` (with the reason) or `unverified` (with the reason and the missing information). List the unverified part of an area (evidence starting with `Unverified:`) under the table as a verification limit.
5. **Rejected findings** from the reviewers and rejected lead observations, one sentence each with the reason.
6. **Review summary:** 2-3 sentences on the PR's overall quality, then one table sorted by priority: `# | priority | type (business/technical/architecture) | location | proposed GitHub comment`. Only findings without an existing thread. The comment column holds the exact text to publish; a comment on an architecture finding names the document, the reference files or the principle and its effect from `reference`; a `missing_justification` comment asks for the rationale instead of claiming the solution is wrong; task vs PR description mismatches go into one general comment asking the author to correct the task or the PR description, in one row with the highest priority among those merged.

Ask the user:

- which comments to publish (all / selected numbers / none);
- whether to change any comment text.

Handle changes in the same conversation: after each change, show the full final text of the changed comments again. Go to step 5 only after the user explicitly approves publishing, with the last version shown.

## 5. Publish and clean up

After approval, publish only the selected comments yourself, without notifications, following the workspace PR comment rules. Use **the exact approved text** (the last version shown to the user) and the approved file/line locations for inline comments. Publish as one review of type COMMENT: the general comment as the body, inline comments on their lines. An inline location that does not match the diff → do not publish it; bring it back to the user for approval again. Add no new comments, application changes, commits, pushes or tracker changes. "None" means nothing is published.

After the review, also without publishing, remove the `review-pr` artifacts yourself: the review worktree with `git worktree remove` (not `rm`, which leaves an entry in `.git/worktrees`) and `pr.diff` and `business-context.md` from the artifacts directory. Do not delete the artifacts directory, other files in it or other worktrees (such as the branch's working worktree). Cleanup does not authorize publishing; on a blocker, report the actual state instead of claiming success.

## STOP

- NEVER publish comments without the user's explicit approval.
