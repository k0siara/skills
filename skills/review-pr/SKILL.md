---
name: review-pr
description: "Code review of someone else's GitHub PR: detached worktree, `review-change` as the review core, CI read instead of rebuilt, GitHub comments published only after the user approves them. Triggers: review-pr <PR>, /review-pr <PR-link>, review PR, review this PR, zrób review, sprawdź PR."
---

# Review PR

Review someone else's PR: check it out read-only, run `review-change` on it as the lead, turn its verified findings into GitHub comments.

Needs `gh` (logged in), `review-change` and the `review` agent from `k0siara/skills`. Missing `review-change`: stop, tell the user to install it with `npx skills@latest add k0siara/skills -g`. Unknown `review` agent: stop, tell the user to run `setup-k0siara-skills`; never substitute another agent or your own review.

## Workspace instructions

Before the first Git, `gh` or GitHub operation, read `AGENTS.md` and `CLAUDE.md` in the repository and its parent workspace, plus the files they point to for Git, GitHub, tracker or review rules, and follow them for every operation, reads included. They win for: which PRs are reviewed (excluded: stop and tell the user); work directory (default `<main-checkout>/.work/review/pr-<N>/`, `<main-checkout>` being the main working tree, with the worktree in `worktree/` and artifacts next to it; add `.work/` to `$(git rev-parse --git-common-dir)/info/exclude` if missing); reading tasks from the tracker; PR comment rules (default English, no prefix).

Write the report and questions in the user's language. Keep a todo list with steps 1-4.

## 1. Check out the PR

1. Read the whole PR: number, author, state (draft, mergeable), head and base, head SHA, title, body, labels, and every CI check on the head SHA (name, status, conclusion, job link). Note running checks and move on; do not wait. Take the task ID from the title or branch.
2. Read every comment with its replies from all three sources: general PR comments, review bodies and inline threads (GraphQL `reviewThreads`: file, line, every comment, `isResolved`, `isOutdated`). Get 1-2 in one `gh api graphql` query (PR, head commit `statusCheckRollup`, `comments`, `reviews`, `reviewThreads` with comments); fetch further pages only where `hasNextPage`, to the end, comments inside a thread included.
3. Fetch `origin pull/<N>/head` and use a worktree at the instructed location, always detached at the head SHA, never on a local PR branch: no path → `worktree add --detach`; clean → `checkout --detach`; local changes → no reset, blocker. A worktree `HEAD` other than the head SHA is a blocker.
4. Base: `git merge-base <base SHA> <head SHA>`.

A missing task ID or an empty PR body does not block the review; pass it on as a fact.

## 2. Run review-change

Run the `review-change` skill yourself, not in a subagent: you did not write this code, so you are the independent lead it describes. Give it:

- the worktree, the base from step 1, the artifacts directory;
- the task ID from step 1, or none;
- the PR title and body as the PR description;
- the PR discussion from step 1;
- the CI checks from step 1 as test results;
- the `review` agent as the reviewer agent. It sets no reviewer count; `review-change` decides that.

CI on the head SHA is the test evidence: do not build, run tests, lint or scans locally. Report failed, still running and missing checks (no check covering a changed module) as they are; never re-run them locally.

It writes `pr.diff`, `business-context.md` and `review-change.md` in the artifacts directory and returns findings, the traceability table, tests, coverage, rejected findings and the earlier remarks.

## 3. Prepare the comments

1. **Earlier remarks.** An issue already raised on the PR, in any thread state (resolved or outdated included), gets no new comment. If the problem is still in the code, it stays on the findings list with a link to the thread and its state.
2. **CI.** Read once more, without waiting, the checks that were running in step 1. A failed check is a technical finding with the cause from the failed-step log only (`gh run view <run> --log-failed`) and a link; build or test failure is P0. No GitHub comment for checks, since the author sees them. List checks still running.
3. **Comments.** Write each in its final published form, following the workspace PR comment rules, so the user approves exactly what goes to GitHub. One comment per finding without an existing thread. An architecture comment names the document, the reference files or the principle and its effect. A `missing_justification` comment asks for the rationale instead of claiming the solution is wrong. A `design_suggestion` comment is worded as optional: the cost of the current code, the alternative and what it gives up, and that it does not block merge. Task vs PR description mismatches go into one general comment asking the author to correct the task or the description, at the highest priority among them.

Report the `review-change` result (traceability table, tests, coverage, rejected findings), then a **review summary**: two or three sentences on the PR's overall quality and one table of all findings sorted by priority, `# | priority | type (business/technical/architecture/design suggestion) | location | thread link | proposed GitHub comment`. Findings appear only in this table, not twice.

Ask which comments to publish (all, selected numbers or none) and whether to change any text. After each change, show the full final text of the changed comments again. Go to step 4 only after the user explicitly approves publishing the last version shown.

## 4. Publish and clean up

Publish only the selected comments, with the exact approved text and locations, without notifications: one review of type COMMENT, the general comment as its body, inline comments on their lines. An inline location that does not match the diff is not published; bring it back to the user. No other comments, code changes, commits, pushes or tracker changes. "None" publishes nothing.

Then remove the review artifacts: the review worktree with `git worktree remove` (not `rm`, which leaves an entry in `.git/worktrees`), and `pr.diff`, `business-context.md` and `review-change.md`. Leave other files and worktrees alone, such as the branch's working worktree. Cleanup does not authorize publishing. On a blocker, report the actual state instead of claiming success.

## STOP

- NEVER publish comments without the user's explicit approval.
- No application changes, commits, pushes, notifications or tracker writes. Allowed: reads, fetch, the review worktree and review artifacts.
