---
name: using-linear
description: Use when the user mentions Linear, issues, tasks, current work, sprint or cycle, backlog, creating or updating issues, project context, or anything related to task tracking and planning. Invoke BEFORE asking the user any question about Linear context.
---

# Using Linear

Work with Linear issues in the context of the user's current work. Derive everything you can yourself; ask only what the workspace and Linear cannot answer.

## 1. Load workspace rules first

Before any Linear operation, read or write, locate the workspace's Linear rules file:

1. The path named in the project instructions (`AGENTS.md`, `CLAUDE.md` or equivalent).
2. Otherwise the nearest `LINEAR.md`, walking up from the current directory to the workspace root.

If it exists, read it completely and apply it. Its rules (teams, projects, parent routing, title conventions, cycle, language, confirmation, status workflow, worklog) override the defaults in this skill. The most specific matching rule wins over a general one.

## 2. Derive context instead of asking

Fetch the user's active issues:

```bash
linear api <<'GRAPHQL'
query {
  viewer {
    assignedIssues(
      first: 20
      orderBy: updatedAt
      filter: { state: { type: { in: ["started", "unstarted"] } } }
    ) {
      nodes {
        identifier
        title
        team { key }
        project { name id }
        state { name }
        parent { identifier title }
      }
    }
  }
}
GRAPHQL
```

Combine these issues, the rules file and the conversation to decide:

- team, project and parent for a new issue,
- the title convention: mirror sibling issues under the chosen parent,
- the assignee: the user (`--assignee self`) unless told otherwise.

Ask only when the destination is still ambiguous after this. Then ask one short question with the candidate destinations.

Before working on an existing issue, fetch its full title and description and read them completely.

## 3. Writes require explicit approval

Every mutation (create, edit title or description, status, assignee, priority, cycle, comment, delete) follows this order:

1. **Propose** the exact change: title, description, team, project, parent, assignee, state, cycle, comment text.
2. **Wait** for explicit approval. A changed draft needs new approval.
3. **Execute** only then.

An explicitly invoked workflow that declares its invocation as approval for its own Linear changes counts as that approval, within that workflow's scope.

## 4. Defaults

Apply these unless the rules file says otherwise:

- Write every title, description and comment in English, including drafts shown for approval.
- New issues: `--assignee self`, state `backlog`.
- Execute with the `linear` CLI; use the `linear-cli` skill when available for command syntax.

```bash
linear issue create \
  --team <TEAM> \
  --title "<title following the sibling convention>" \
  --description-file <approved-description.md> \
  --assignee self \
  --parent <PARENT-ID> \
  --state backlog
```

## 5. Epic audits and bulk edits

When asked what is really done in an epic, or when one approved change touches several fields or issues, follow `references/epic-audit-and-bulk-edits.md`. It covers cross-checking Linear against git and PRs, multi-field `linear api` mutations with variables, safe edits to long plan descriptions, and what a parking or cancel comment must say.

## Red flags

| Thought | Instead |
|---|---|
| "I'll ask which project or team" | Read the rules file and query active issues |
| "I don't know the parent or epic" | Check parents of the active issues and the rules file routing |
| "Which naming convention?" | Rules file first, then sibling issues under the parent |
| "I can run this change right away" | Propose it and wait for approval |
| "Linear says Done/In Review, so it is" | Verify against the default branch and the PR state |
