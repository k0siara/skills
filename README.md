# Skills

Agent skills by [@k0siara](https://github.com/k0siara).

## Install

```bash
npx skills@latest add k0siara/skills
```

Install a single skill for a specific agent, globally:

```bash
npx skills add k0siara/skills --skill <name> -a claude-code -g
```

List available skills:

```bash
npx skills add k0siara/skills --list
```

## Reference

| Skill | What it does | When to use |
|---|---|---|
| [restate-problem](./skills/restate-problem/SKILL.md) | Restates your goals and the problem you're solving in the agent's own words. | Before starting non-trivial work, to catch misunderstandings early. Trigger: "restate the problem", `/restate-problem`. |
