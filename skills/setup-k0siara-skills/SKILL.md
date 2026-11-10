---
name: setup-k0siara-skills
description: "Use once after installing k0siara/skills or to change the model that reviews and verifies: creates the `review` agent for OMP, Codex and Claude Code and records the model. Shows every change before writing. Triggers: setup-k0siara-skills, /setup-k0siara-skills, set up k0siara skills, change the review model, configure the review agent."
---

# Set up k0siara skills

`<skill-dir>` is the directory that contains this file.

Skills never name a model. Verification and review (`deliver-pr`, `review-change`, `review-pr`) run in one agent, `review`, with no instructions of its own (the delegating prompt says what to do), so they can run on a model other than the session's. The script creates it in every harness it finds, records the model in `~/.config/k0siara-skills/config.yml` and removes agents from earlier versions. Only OMP gets the model (`task.agentModelOverrides`, since its `task` tool takes no model); Codex and Claude Code use the session's model.

## Steps

1. Read `~/.config/k0siara-skills/config.yml` if it exists and show the current model.
2. Ask the user for the model and effort, offering the current values as defaults. A model is an OMP selector such as `openai-codex/gpt-6.1-sol`, and the effort one of the levels OMP lists for it (`omp models find <id>`).
3. Show the plan without writing anything:

   ```bash
   python3 <skill-dir>/scripts/setup.py --model <model>:<effort>
   ```

   It validates the model in OMP (exit 1 or 2 with the reason) and prints every change it would make. `no changes` means everything is already in place.
4. Show the plan to the user and ask for approval. Do not write before they approve.
5. Apply it with the same command plus `--write`. It copies each file it changes or removes, including `~/.omp/agent/config.yml`, to `~/.config/k0siara-skills/backups/<timestamp>/` (or `--backup-dir <dir>`) before writing, and prints that path.
6. Run the step 3 command again. It must print `no changes`. Report the agent files written and removed, the backup path and, for OMP, that new sessions and subagent launches pick the agent up without a restart.

Rerun the skill after installing another harness, to give it the agent too.
