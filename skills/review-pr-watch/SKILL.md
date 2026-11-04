---
name: review-pr-watch
description: "Reviews someone else's GitHub PR with the review-pr skill (once, unless you already reviewed it), then watches the PR in the background until you approve, it merges or it closes. When the author pushes commits, replies or requests your review again, it re-checks each of your remarks in code, drafts replies for remarks not fixed and asks before approving. Triggers: review-pr-watch <PR>, /review-pr-watch <PR-link>, watch the PR I reviewed, follow up my review, re-review, check the author's fixes."
---

# Review PR Watch

Keeps your review of someone else's PR alive. It runs `review-pr` once if you have no review on the PR yet, watches the PR with `scripts/review-wait`, and runs a follow-up round when the author acts. Nothing is published, approved or pushed without the user's approval (see Notify and ask).

Needs `gh` (logged in), `python3`, and the `review-pr` skill with its dependencies (`review-change`, the `review` agent) from `k0siara/skills`. If `review-pr` is missing, stop: `REVIEW-WATCH: BLOCKED <pr-url> review-pr is not installed, install it with npx skills@latest add k0siara/skills -g`.

## Project rules

Before the first Git, `gh` or GitHub operation, read the workspace instructions that apply to the repository (`AGENTS.md`, `CLAUDE.md` and the files they point to for Git, GitHub and review rules). Follow them for every operation, reads included. They win for: worktree location, artifacts directory, PR comment language and any required prefix or marker, which PRs are reviewed at all. Defaults: English, no prefix. For a PR the rules exclude, stop and tell the user.

Write the report and questions in the user's language. Keep a todo list with the steps below.

## Notify and ask

- Talk to the user in the chat. Use a desktop notification only if the user asked for one.
- Ask only when the user must decide: publishing a reply, approving, a remark you cannot judge. Each question contains the status, the links and the exact text.
- Interactive is the default. An explicit instruction from the user or the caller about publishing or approving is the user's approval. Then act within exactly what it allows, using the approved text.

## Status line

When the skill stops, the last line of the final message is:

`REVIEW-WATCH: <APPROVED|MERGED|CLOSED|BLOCKED> <pr-url> <short reason>`

- `APPROVED`: your review is approved.
- `MERGED`: the PR merged.
- `CLOSED`: closed without merging.
- `BLOCKED`: stopped without the above (user asked to stop, `review-wait` stopped, a blocker in a round, review-pr not installed or published nothing).

## State

File: `~/.local/state/review-pr-watch/<owner>__<repo>__<N>.json`. Written after the first review is recognized and at the end of every round. Shape:

```json
{
  "repo": "owner/name",
  "pr": 123,
  "viewer": "your-login",
  "review_ids": ["PRR_..."],
  "remark_ids": ["PRRC_...", "PRR_..."],
  "head": "<head SHA the last round checked>",
  "checked_at": "2026-01-01T12:00:00Z",
  "rounds": 0
}
```

- `review_ids`: your submitted reviews (not `PENDING`).
- `remark_ids`: node ids of your thread root comments and of your review bodies that contain remarks.
- `checked_at`: UTC time taken before the round's first GitHub read. Author activity created after it is new.
- Recognize your remarks by your login and these ids, never by a text prefix.

Build it from GitHub, never from the text you wrote: your submitted reviews (`gh api graphql`, `reviews` with `author`, `state`, `id`, `body`, `commit.oid`), the threads whose first comment is yours (`reviewThreads`, paginated), and the review bodies that are not empty. The `review-pr` skill writes no state.

## Start

1. Read the PR: `gh pr view <N> --repo <owner>/<repo> --json url,state,author,headRefOid,reviews`, and your login with `gh api user --jq .login`.
   - `MERGED` or `CLOSED`: report the status and stop.
   - You already have an `APPROVED` review: report `APPROVED` and stop.
2. Your submitted reviews exist: skip the first review. None exist: run the `review-pr` skill for this PR. Read its `SKILL.md` and follow it unchanged. Do not copy its steps here. Afterwards read your reviews again. None: stop with `BLOCKED` (nothing to follow up).
3. No state file: create it from GitHub (see State). Set `head` to the current head SHA and `checked_at` to the read time.
4. Run the follow-up round once when the head moved since `head` or the author has activity after `checked_at`. Otherwise go on.
5. Start the watcher (see Watcher).

## Watcher

One per PR. It runs in the background and wakes you with its output when it exits, so you never poll or sleep.

Command, from this skill's directory: `scripts/review-wait <pr-url> [--interval 60] [--quiet 900]`.

- OMP: `bash` with `async: true`, `timeout: 0`. Stop it with `proc://<job-id>/kill`.
- Other harnesses: their background facility, with the same command.
- Exit 2 with `already watches`: another watcher runs for this PR. Do not start a second one.

The watcher keeps its own state in `~/.local/state/review-wait/`, with no age limit. A restarted watcher reports what arrived after its last report. Start it after every review publication and after every round that does not stop.

The watcher prints one line per event, with a `#<N> ` prefix:

| Line (after `#<N> `) | Meaning | Action |
|---|---|---|
| `approved: <url>` | You approved. | `REVIEW-WATCH: APPROVED`, stop. |
| `merged: <url>` | Merged. | `REVIEW-WATCH: MERGED`, stop. |
| `closed without merging: <url>` | Closed. | `REVIEW-WATCH: CLOSED`, stop. |
| `review requested again: <url>` | Author asked for a new review. | Run the round. |
| `new commits on <sha7>` | Author pushed (after the quiet window). | Run the round. |
| `author comment`, `author new thread`, `author thread reply`, `author review (...)` | Author replied (after the quiet window). | Run the round. |
| `comment from`, `new thread from`, `thread reply from`, `review (...) from` (no `author` prefix) | Someone else wrote. | Tell the user the line. Restart the watcher. Do not act without asking. |
| `review-wait stopped:` | Watcher gave up (GitHub unreachable or a fatal error). | `REVIEW-WATCH: BLOCKED` with the reason, stop. |
| anything else | | Restart the watcher silently. |

## Follow-up round

Re-checks the author's response to your earlier remarks. You do not redo the review and do not open new threads.

### Step 1: PR state

1. Read the PR number, author, state, head SHA, task ID from title or branch, and CI checks on the head SHA (name, status, conclusion, job link). `MERGED` or `CLOSED`: report and end. `APPROVED` by you: end with `APPROVED`.
2. Read your remarks, paginating every list to its end:
   - inline threads whose ids are in `remark_ids` (`reviewThreads`: path, line, `isResolved`, `isOutdated`, each comment with `databaseId`, author, `createdAt`, body);
   - review bodies whose ids are in `remark_ids`, split into separate remarks (one per numbered or bulleted item).
   The author's answers: thread comments by the author, and general PR comments by the author (they answer review-body remarks).
3. Take the read time before these reads. It becomes `checked_at` in Step 6.
4. Base SHA: the stored `head`. If it is no longer in the repo (force-push), use the `commit.oid` of your latest review and note that.
5. Worktree: the location from the workspace rules, default `<main-checkout>/../<repo-name>.worktrees/pr-<N>`. `git fetch origin pull/<N>/head`, then `git worktree add --detach <path> <head SHA>`. Reuse a worktree already at the head SHA. Local changes or a `HEAD` other than the head SHA: blocker. Fetch the base SHA too and write `git diff <base>..<head>` to `followup.diff` in the artifacts directory (default `$TMPDIR/review-pr/<repo>-pr-<N>/`). If the base is missing, diff against the full PR diff and say so.

If the watcher woke for `review requested again` or author activity, run the round. If you came from Start step 4 and nothing changed (same head, no author activity after `checked_at`), skip the round and go on to Watcher.

### Step 2: Judge each remark

Each remark gets one status with evidence: `file:line` at the head SHA, the author's quote, and the link.

- `fixed`: the code change removes the problem. Check the code itself; a claim alone does not count. A "done" without the change that does it is not a fix.
- `justified`: the author did not change the code but gave a concrete argument that you verify in the code, the project docs or the task (read-only). Examples: the problem does not occur because …; the requirement says otherwise (quote it); a deliberate decision with a sound reason. Deferring the issue outside this PR counts only with a link to an existing task that covers it.
- `not fixed`: no answer and no change; a vague answer ("ok", "not needed", "looks better") without a reason; an argument that is false or unrelated; a partial or wrong fix.

Resolving a thread does not change the verdict. For an outdated thread, judge the current code at that location.

### Step 3: Regressions and CI

Review `followup.diff` for problems the changes introduced: regressions, deleted or weakened tests, new failing checks. Report them. Never publish them as new threads. List failing checks.

### Step 4: Report and decide

Report: a table `# | remark (link) | status | evidence | author's answer (short)`, then CI checks, then `followup.diff` problems.

- At least one `not fixed`: for each, draft a reply for its thread in the workspace's comment language (default English, no prefix) that says concretely what is missing or why the argument does not hold, with `file:line`. Show the full texts. Ask the user which to publish (all, selected or none) and whether to change any text. After any change, show the changed texts in full again.
- All `fixed` or `justified`: ask whether to approve. Include the report, failing checks and `followup.diff` problems in the question.

### Step 5: Publish

Only the exact text the user approved, and only after an explicit yes (or the explicit caller instruction described in Notify and ask).

- Thread reply: `gh api repos/<owner>/<repo>/pulls/<N>/comments/<databaseId of the thread's first comment>/replies -f body=<text>`.
- Remark from a review body: one general PR comment (`gh pr comment <N> --repo <owner>/<repo> --body-file <file>`) quoting the remark it answers.
- Approve: `gh pr review <N> --repo <owner>/<repo> --approve`, no body.

After each publication, read the PR or thread again to confirm it landed. "None" publishes nothing.

### Step 6: Update state and clean up

- Remove the worktree with `git worktree remove` (not `rm`) and delete `followup.diff`. Leave other files and worktrees alone.
- Update the state: `head` = the head SHA checked, `checked_at` = the read time from Step 1, `rounds` + 1, `remark_ids` and `review_ids` refreshed from GitHub. Update it even if nothing was published, so the same activity is not checked again.
- The PR is still open and not approved: restart the watcher.

## Never

- Never send REQUEST_CHANGES.
- Never resolve or reopen threads.
- Never open new threads in a follow-up round. Problems go into the report only.
- Never change code, commit, push, or merge.
- Never publish a reply or approve without the user's explicit approval (or an explicit caller instruction covering it).
- Never start a second watcher for the same PR.
- Never recognize your remarks by text prefix. Use your login and the ids in the state.
