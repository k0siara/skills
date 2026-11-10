---
name: using-tracker
description: "Use when the user mentions issues, tickets, tasks, epics, current work, sprint or cycle, backlog, creating or updating issues, or anything about task tracking and planning in any tracker (Linear, Jira, GitHub Issues, local files). Invoke BEFORE asking the user any question about tracker context. Triggers: using-tracker, /using-tracker, create an issue, update the ticket, what am I working on."
---

# Using the task tracker

Work with the issue tracker in the context of the user's current work. Derive everything you can yourself; ask only what the workspace and the tracker cannot answer.

## 1. Find the tracker and its rules first

Before any tracker operation, read or write:

1. Find the tracker the project uses and its rules file: the path named in the project instructions (`AGENTS.md`, `CLAUDE.md` or equivalent), otherwise the nearest `<TRACKER>.md` (such as `LINEAR.md`, `JIRA.md`, `TRACKER.md`) walking up to the workspace root. Without either, infer the tracker from issue IDs and links in the conversation, branch names and commits; if still unknown, ask once.
2. Read the rules file completely and apply it. Its rules (projects, teams or boards, parent routing, title conventions, cycle or sprint, language, confirmation, status workflow, worklog, CLI or tool to use) override the defaults below. The most specific matching rule wins.
3. Command syntax comes from, in order: the rules file, the tracker's CLI skill when installed (such as `linear-cli`), the tracker's reference in `references/` (`references/linear.md` for Linear), the CLI's own `--help`. For GitHub Issues use `gh issue`.

## 2. Derive context instead of asking

Fetch the user's active issues (assigned to them, started or not started, most recently updated first). Combine them, the rules file and the conversation to decide:

- project, team or board, and parent for a new issue,
- the title convention: mirror sibling issues under the chosen parent,
- the assignee: the user unless told otherwise.

Skip the query when the destination is already clear. Ask only when it is still ambiguous, in one short question with the candidate destinations.

Before working on an existing issue, fetch its full title, description and comments and read them completely.

## 3. Writes require explicit approval

Every mutation (create, edit title or description, status, assignee, priority, cycle or sprint, labels, relations, comment, delete) follows this order:

1. **Propose** the exact change: every field and the full text.
2. **Wait** for explicit approval. A changed draft needs new approval.
3. **Execute** only then, read the issue back and report what was written.

An explicitly invoked workflow that declares its invocation as approval for its own tracker changes counts as that approval, within that workflow's scope.

Never invent labels, statuses, fields or issue types; use only those the tracker has.

## 4. Defaults

Unless the rules file says otherwise:

- Write titles, descriptions and comments in English, drafts included.
- New issues: assigned to the user, in the initial backlog state.
- Pass long descriptions through a file, not an inline shell argument.

## 5. Audits and bulk edits

When asked what is really done in an epic or plan, or when one approved change touches several fields or issues: read the parent and all its comments, fetch the whole tree once into a scratch file and print one line per issue, cross-check states against the default branch and PR states, report the drift (In Review with a merged PR, closed-unmerged PRs, claimed work with no code, code no issue covers), then propose the fixes. For Linear, including publishing many new issues with relations at once, follow `references/linear-epic-audit-and-bulk-edits.md`.

## Red flags

| Thought | Instead |
|---|---|
| "I'll ask which project, team or board" | Read the rules file and query active issues |
| "I don't know the parent or epic" | Check parents of the active issues and the rules file routing |
| "Which naming convention?" | Rules file first, then sibling issues under the parent |
| "I can run this change right away" | Propose it and wait for approval |
| "The tracker says Done or In Review, so it is" | Verify against the default branch and the PR state |
