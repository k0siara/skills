---
name: setup-k0siara-skills
description: "Use once after installing k0siara/skills, and whenever the user wants to change which model reviews or verifies: asks for the model and effort of the `reviewer` and `verifier` roles, writes ~/.config/k0siara-skills/config.yml and creates the k0siara-reviewer and k0siara-verifier agents for OMP, Codex and Claude Code. Shows every change before writing and is safe to rerun. Triggers: setup-k0siara-skills, /setup-k0siara-skills, set up k0siara skills, change the reviewer model, configure review agents."
---

# Set up k0siara skills

`<skill-dir>` is the directory that contains this file.

`deliver-pr` and `pre-pr-review` never name a model. They start two agents by role:

| agent | role | used by |
|---|---|---|
| `k0siara-reviewer` | independent read-only review | `pre-pr-review` reviewers, the `deliver-pr` review stage |
| `k0siara-verifier` | runs checks, may fix in scope, never commits | the `deliver-pr` verification stage |

This skill creates both agents in every harness it finds and records the models in one place, `~/.config/k0siara-skills/config.yml`:

- **OMP:** `~/.omp/agent/agents/k0siara-<role>.md`, and the role's model in `task.agentModelOverrides` of `~/.omp/agent/config.yml`. OMP's `task` tool takes no model, so this override is what pins it. `omp config set` merges the key and keeps every other setting.
- **Codex:** `~/.codex/agents/k0siara-<role>.toml`, with no model: the subagent uses the session's model.
- **Claude Code:** `~/.claude/agents/k0siara-<role>.md`, with no model: the subagent uses the session's model.

The reviewer has no edit tools in OMP and Claude Code. Codex agent files cannot restrict tools, so there the read-only rule lives in its instructions.

## Steps

1. Read `~/.config/k0siara-skills/config.yml` if it exists and show the current models.
2. Ask the user for the model and effort of each role, offering the current values as defaults. A model is an OMP selector such as `openai-codex/gpt-6.1-sol`, and the effort one of the levels OMP lists for it (`omp models find <id>`). Without OMP the model is only recorded; Codex and Claude Code use their session model either way.
3. Show the plan without writing anything:

   ```bash
   python3 <skill-dir>/scripts/setup.py --role reviewer=<model>:<effort> --role verifier=<model>:<effort>
   ```

   It names the harnesses it found, validates each model in OMP (exit 1 or 2 with the reason when OMP does not offer the model or the effort) and prints every file it would create or update as a diff, plus the OMP override changes. `no changes` means everything is already in place.
4. Show the plan to the user and ask for approval. Do not write before they approve.
5. Apply it with the same command plus `--write`. It copies each file it changes, including `~/.omp/agent/config.yml`, to `~/.config/k0siara-skills/backups/<timestamp>/` (or `--backup-dir <dir>`) before writing, and prints that path.
6. Run the step 3 command again. It must print `no changes`. Report the agents created, the backup path and, for OMP, that new sessions and subagent launches pick the agents up without a restart.

Rerun the skill after installing another harness, to give it the agents too.
