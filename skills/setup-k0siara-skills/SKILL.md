---
name: setup-k0siara-skills
description: "Use once after installing k0siara/skills, and whenever the user wants to change which model reviews and verifies: asks for the model and effort of the `review` agent, writes ~/.config/k0siara-skills/config.yml and creates the `review` agent for OMP, Codex and Claude Code. Shows every change before writing and is safe to rerun. Triggers: setup-k0siara-skills, /setup-k0siara-skills, set up k0siara skills, change the review model, configure the review agent."
---

# Set up k0siara skills

`<skill-dir>` is the directory that contains this file.

Skills never name a model. Verification and review run in one agent, `review`, which has no instructions of its own: the delegating prompt says what to do. It exists so these subagents run on a model other than the session's.

| used by | for |
|---|---|
| `deliver-pr` | the `verify-changes` and `review-change` stages |
| `review-change` | the technical and architecture reviewers, each prompted with its checklist |
| `review-pr` | the same reviewers, through `review-change` |

This skill creates the agent in every harness it finds and records the model in one place, `~/.config/k0siara-skills/config.yml`:

- **OMP:** `~/.omp/agent/agents/review.md`, and the model in `task.agentModelOverrides` of `~/.omp/agent/config.yml`. OMP's `task` tool takes no model, so this override is what pins it.
- **Codex:** `~/.codex/agents/review.toml`, with no model: the subagent uses the session's model.
- **Claude Code:** `~/.claude/agents/review.md`, with no model: the subagent uses the session's model.

It also removes the agents earlier versions created (`k0siara-reviewer`, `k0siara-verifier`, `code-review-technical-agent`, `code-review-architecture-agent`) and their OMP overrides.

## Steps

1. Read `~/.config/k0siara-skills/config.yml` if it exists and show the current model.
2. Ask the user for the model and effort, offering the current values as defaults. A model is an OMP selector such as `openai-codex/gpt-6.1-sol`, and the effort one of the levels OMP lists for it (`omp models find <id>`). Without OMP the model is only recorded; Codex and Claude Code use their session model either way.
3. Show the plan without writing anything:

   ```bash
   python3 <skill-dir>/scripts/setup.py --model <model>:<effort>
   ```

   It names the harnesses it found, validates the model in OMP (exit 1 or 2 with the reason when OMP does not offer the model or the effort) and prints every file it would create, update or remove, plus the OMP override changes. `no changes` means everything is already in place.
4. Show the plan to the user and ask for approval. Do not write before they approve.
5. Apply it with the same command plus `--write`. It copies each file it changes or removes, including `~/.omp/agent/config.yml`, to `~/.config/k0siara-skills/backups/<timestamp>/` (or `--backup-dir <dir>`) before writing, and prints that path.
6. Run the step 3 command again. It must print `no changes`. Report the agent files written and removed, the backup path and, for OMP, that new sessions and subagent launches pick the agent up without a restart.

Rerun the skill after installing another harness, to give it the agent too.
