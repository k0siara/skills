# Linear

Use the `linear` CLI; the `linear-cli` skill has the full command syntax.

## Active issues of the user

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

## Create an issue

```bash
linear issue create \
  --team <TEAM> \
  --title "<title following the sibling convention>" \
  --description-file <approved-description.md> \
  --assignee self \
  --parent <PARENT-ID> \
  --state backlog
```

## Audits and bulk edits

See `linear-epic-audit-and-bulk-edits.md`.
