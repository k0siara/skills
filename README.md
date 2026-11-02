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
| [pr](./skills/pr/SKILL.md) | Writes review-focused PR titles and descriptions grounded in the diff, observed verification, compatibility and rollout risks. Follows repository templates and confidentiality rules. | When preparing, opening or updating a PR. Trigger: "write a PR description", "open a PR", `/pr`. |
| [restate-problem](./skills/restate-problem/SKILL.md) | Restates your goals and the problem you're solving in the agent's own words. | Before starting non-trivial work, to catch misunderstandings early. Trigger: "restate the problem", `/restate-problem`. |
| [using-linear](./skills/using-linear/SKILL.md) | Works with Linear in the context of your current work: reads the workspace `LINEAR.md` rules, derives team, project, parent and naming from your active issues, and proposes every change for approval before running it. Needs the `linear` CLI (logged in). | Whenever you talk about Linear issues, tasks, cycles or backlog. Trigger: "create a Linear task", "what am I working on", `/using-linear`. |
