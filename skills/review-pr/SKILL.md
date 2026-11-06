---
name: review-pr
description: "Code review of someone else's GitHub PR: detached review worktree, then the `review-change` review core (business context from the task and the PR discussion before the diff, rule-to-implementation-and-test traceability, `review` reviewers per its change classification, verified findings, coverage), then proposed GitHub comments published only after the user approves them. Triggers: review-pr <PR>, /review-pr <PR-link>, review PR, review this PR, zrób review, sprawdź PR."
---

# Review PR

Review someone else's PR. You check it out read-only, run the `review-change` skill on it as the lead, and turn its verified findings into GitHub comments. Nothing is published until the user approves the exact text.

Needs `gh` (logged in), the `review-change` skill and the `review` agent, both from `k0siara/skills`. If `review-change` is missing, stop and tell the user to install it with `npx skills@latest add k0siara/skills -g`. If the subagent tool does not know `review`, stop and tell the user to run `setup-k0siara-skills`; do not replace the reviewers with another agent or your own review.

## Workspace instructions

Before the first Git, `gh` or GitHub operation, read the instructions that apply to the repository: `AGENTS.md` and `CLAUDE.md` in the repository and its parent workspace, plus the files they point to for Git, GitHub, tracker or review rules. Follow them for every operation, reads included. Where they set something below, they win:

- which repositories or PRs are reviewed at all; for an excluded PR, stop and tell the user;
- work directory; default `<main-checkout>/.work/review/pr-<N>/`, inside `<main-checkout>/.work/` (`<main-checkout>` is the repository's main working tree; add `.work/` to `$(git rev-parse --git-common-dir)/info/exclude` if it is not there);
- worktree location; default `worktree/` in the work directory;
- artifacts directory; default the work directory itself, next to the worktree;
- how to read tasks from the tracker;
- PR comment rules (language, required prefix or marker); default English, no prefix.

Write the report and questions in the user's language. Keep a todo list with steps 1-4.

## 1. Check out the PR

Allowed: reads, fetch, the review worktree and review artifacts. Not allowed: application changes, commit, push, publishing, notifications, tracker writes.

1. Read the whole PR: number, author, state (draft, mergeable), head and base, head SHA, title, body, labels, and every CI check on the head SHA (name, status, conclusion, job link). Note running checks and move on; do not wait. Take the task ID from the title or branch.
2. Read every comment with its replies from all three sources: general PR comments, review bodies and inline threads (GraphQL `reviewThreads`: file, line, every comment, `isResolved`, `isOutdated`). Paginate every list to the end, comments inside a thread included.
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

It writes `pr.diff`, `business-context.md` and `review-change.md` in the artifacts directory and returns findings, the traceability table, tests, coverage, rejected findings and the earlier remarks.

## 3. Prepare the comments

1. **Earlier remarks.** An issue already raised on the PR, in any thread state (resolved or outdated included), gets no new comment. If the problem is still in the code, it stays on the findings list with a link to the thread and its state.
2. **CI.** Read once more, without waiting, the checks that were running in step 1. A failed check is a technical finding with the cause from the job log and a link; build or test failure is P0. No GitHub comment for checks, since the author sees them. List checks still running.
3. **Comments.** Write each in its final published form, following the workspace PR comment rules, so the user approves exactly what goes to GitHub. One comment per finding without an existing thread. An architecture comment names the document, the reference files or the principle and its effect. A `missing_justification` comment asks for the rationale instead of claiming the solution is wrong. Task vs PR description mismatches go into one general comment asking the author to correct the task or the description, at the highest priority among them.

Report the `review-change` result (findings with their thread links, traceability table, tests, coverage, rejected findings), then a **review summary**: two or three sentences on the PR's overall quality and one table sorted by priority, `# | priority | type (business/technical/architecture) | location | proposed GitHub comment`.

Ask which comments to publish (all, selected numbers or none) and whether to change any text. After each change, show the full final text of the changed comments again. Go to step 4 only after the user explicitly approves publishing the last version shown.

## 4. Publish and clean up

Publish only the selected comments, with the exact approved text and locations, without notifications: one review of type COMMENT, the general comment as its body, inline comments on their lines. An inline location that does not match the diff is not published; bring it back to the user. No other comments, code changes, commits, pushes or tracker changes. "None" publishes nothing.

Then remove the review artifacts: the review worktree with `git worktree remove` (not `rm`, which leaves an entry in `.git/worktrees`), and `pr.diff`, `business-context.md` and `review-change.md`. Leave other files and worktrees alone, such as the branch's working worktree. Cleanup does not authorize publishing. On a blocker, report the actual state instead of claiming success.

## STOP

- NEVER publish comments without the user's explicit approval.
