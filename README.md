# Skills for Software Engineers

Agent skills by [@k0siara](https://github.com/k0siara).

## Install

```bash
npx skills@latest add k0siara/skills
```

## Reference

| Skill | What it does | When to use |
|---|---|---|
| [babysit-pr](./skills/babysit-pr/SKILL.md) | Watches a GitHub PR in the background until it is approved, notifies you about review comments, CI failures and approval, proposes minimal fixes and replies for your approval, and rebases on conflict. Needs `gh` (logged in) and `python3`. | After opening a PR you want watched. Trigger: "babysit PR #123", "watch this PR", `/babysit-pr`. |
| [deliver-pr](./skills/deliver-pr/SKILL.md) | Delivers one task (Linear, GitHub issue or a written spec) end to end in an isolated worktree: research, plan, implementation, verification and independent review, then a verified PR. Takes conventions from your workspace instructions. Inside Herdr with `hc`, runs verification and review as `omp` agents in new tabs; otherwise as subagents. | When a task is ready to implement. Trigger: "deliver-pr ABC-123", "go #45", `/deliver-pr`. |
| [pr](./skills/pr/SKILL.md) | Writes review-focused PR titles and descriptions grounded in the diff, observed verification, compatibility and rollout risks. Follows repository templates and confidentiality rules. | When preparing, opening or updating a PR. Trigger: "write a PR description", "open a PR", `/pr`. |
| [pre-pr-review](./skills/pre-pr-review/SKILL.md) | Independent, read-only review of a local branch against its task: business context from the task source, rule-to-implementation-and-test traceability, technical and architecture reviewers who did not write the code, verified findings and a PASS, ISSUES or INCONCLUSIVE verdict. | Before opening a PR for your own change. Trigger: "review my branch before the PR", `/pre-pr-review`. |
| [restate-problem](./skills/restate-problem/SKILL.md) | Restates your goals and the problem you're solving in the agent's own words. | Before starting non-trivial work, to catch misunderstandings early. Trigger: "restate the problem", `/restate-problem`. |
| [using-linear](./skills/using-linear/SKILL.md) | Works with Linear in the context of your current work: reads the workspace `LINEAR.md` rules, derives team, project, parent and naming from your active issues, and proposes every change for approval before running it. Needs the `linear` CLI (logged in). | Whenever you talk about Linear issues, tasks, cycles or backlog. Trigger: "create a Linear task", "what am I working on", `/using-linear`. |
| [verify-changes](./skills/verify-changes/SKILL.md) | Finds and runs the repository's formatters, static checks, build and tests, plus a project verification skill that drives the real app when one exists. Fixes failures at the root cause within a retry limit, reviews the diff and returns PASS, FAIL or INCONCLUSIVE with evidence. | Before a commit, PR or merge. Trigger: "verify my changes", "run the checks", `/verify-changes`. |
