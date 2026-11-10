# Epic audit and bulk edits

## Audit an epic against the code

Use when asked what is really done in a Linear epic or plan, where the gaps are, or what comes next.

1. Read the epic description and all comments completely. Plans and corrections often live in comments.
2. Fetch the whole tree in one query (children and grandchildren, with state and GitHub attachments), save it to a scratch file, and print a compact one-line-per-issue list. Do not dump raw JSON into context.

```bash
linear api <<'GRAPHQL' > "$TMPDIR/tree.json"
query { issue(id: "<EPIC>") { children(first: 100) { nodes {
  identifier title state { name } attachments { nodes { url } }
  children(first: 50) { nodes { identifier title state { name } attachments { nodes { url } } } } } } } }
GRAPHQL
```

3. Cross-check against the repo, not against Linear alone:
   - `git fetch` and then `git log origin/<default-branch> --oneline | grep <TEAM>-` for merged work. A stale local branch hides recent merges.
   - `gh pr view <n> --json state,mergeable,reviewDecision` for every attached PR.
   - `git grep <pattern> origin/<default-branch>` for leftovers the plan should have removed (markers, `shortcut:` comments, old helpers). The local knowledge graph indexes the working tree, so it can be stale.
4. Report the drift explicitly:
   - issue still In Review or In Progress although its PR is merged,
   - planned issue whose attached PR was closed without merging,
   - comment claims work started but the code shows none,
   - code that no issue covers (unplanned gaps).
5. Close with a short ordered "next" diagram and propose the Linear fixes. Never apply them without approval.

Delegate step 3 to a subagent when it means reading many files. Give it the plan's principles and the list of allowed exceptions, so it can classify each finding as allowed, known pending, or an unplanned gap.

## Publishing a set of new issues (with relations and plan edits)

Use when an approved breakdown creates many issues at once (a stage parent, children, blocking edges, notes in existing issues).

1. Resolve UUIDs once: team, project (`slugId` → `id`), active cycle (`team{activeCycle{id}}`), state, viewer. Create each issue with one `issueCreate(input:{teamId, projectId, cycleId, stateId, assigneeId, parentId, title, description})` through `linear api --variables-json`; the CLI flags cannot set every field in one call.
2. Keep the approved drafts as one file per issue plus a manifest (key, title, parent key, blocked-by keys) next to the spec. Reference not-yet-created issues with placeholders such as `<<20.1>>`.
3. Run a script that writes created issues to a `published.json` state file after every create and skips keys already in it, so a rerun after a failure never duplicates issues. Create parents first, then blockers before the issues they block.
4. Second pass: replace every placeholder with real identifiers (including sub-task lists in the parents' descriptions) and assert no `<<` is left; create the `blocks` relations (`issueRelationCreate(input:{issueId: blocker, relatedIssueId: blocked, type: blocks})`), logging each edge so reruns skip it; then apply the anchored edits to existing issues (next section).
5. Read back in one script: per new issue state, cycle, project, assignee, parent, blocked-by, blocks, children and a placeholder check; per edited issue, which new identifiers its description now references. Report from that output only.

## Multi-field mutation in one call

Use `linear api` with variables when one approved change touches several fields or issues (state, cycle, description, comment). Variables avoid escaping problems with markdown bodies.

```bash
# q.graphql
mutation($a:String!,$st:String!,$r:String!,$d:String!,$c:String!){
  u1:issueUpdate(id:$a,input:{stateId:$st,cycleId:null}){success}
  u2:issueUpdate(id:$r,input:{description:$d}){success}
  c:commentCreate(input:{issueId:$a,body:$c}){success} }

linear api --variables-json "$(cat v.json)" < q.graphql
```

- Resolve state ids first with `team(id:"<KEY>"){states{nodes{id name}}}`.
- `cycleId: null` removes an issue from its cycle.
- Build `v.json` in Python with `json.dumps`, never by hand-concatenating strings.

## Editing a long plan description

- Fetch the current description right before editing. Never rewrite it from memory.
- Insert or replace at a unique anchor, and `assert desc.count(anchor) == 1` first. Also assert that the new text is not already present, so a retry stays idempotent.
- Re-query after the mutation and print only the changed lines to verify.

## Parking or canceling a planned issue

The approved comment should state:

- why (one or two sentences),
- what happens to its PR and branch,
- which issue now owns the open decision,
- the impact on dependent issues.

Also add one line to the epic's plan, so the parked item stays visible from the root.
