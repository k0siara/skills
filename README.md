# Skills for Software Engineers

Agent skills by [@k0siara](https://github.com/k0siara).

## Install

```bash
npx skills@latest add k0siara/skills
```

## Reference

| Skill | What it does | When to use |
|---|---|---|
| [babysit-pr](./skills/babysit-pr/SKILL.md) | Watches a GitHub PR in the background, notifies you about review comments, approval, CI failures and merge, proposes minimal fixes and replies for your approval, and rebases on conflict. Needs `gh` (logged in) and `python3`. | After opening a PR you want watched. Trigger: "babysit PR #123", "watch this PR", `/babysit-pr`. |
| [restate-problem](./skills/restate-problem/SKILL.md) | Restates your goals and the problem you're solving in the agent's own words. | Before starting non-trivial work, to catch misunderstandings early. Trigger: "restate the problem", `/restate-problem`. |
