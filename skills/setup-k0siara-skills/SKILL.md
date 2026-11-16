---
name: setup-k0siara-skills
description: "Use once after installing k0siara/skills or to change the models that verify and review: creates the `verify` and `review` agents for OMP, Codex and Claude Code and records the models. Shows every change before writing. Triggers: setup-k0siara-skills, /setup-k0siara-skills, set up k0siara skills, change the review model, change the verify model, configure the review agent."
---

# Set up k0siara skills

`<skill-dir>` is the directory that contains this file.

Skills never name a model. Verification (`verify-changes`) runs in the `verify` agent and review (`review-change`, `review-pr`) in the `review` agent, both with no instructions of their own (the delegating prompt says what to do), so they can run on models other than the session's, and on different ones: verification mostly runs commands and needs less effort and cost than review. The script creates both in every harness it finds, records the models in `~/.config/k0siara-skills/config.yml` and removes agents from earlier versions. Only OMP gets the models (`task.agentModelOverrides`, since its `task` tool takes no model); Codex and Claude Code use the session's model.

## Steps

1. Read `~/.config/k0siara-skills/config.yml` if it exists and show the current review model and verify model (`verify_model`; without it `verify` uses the review model).
2. Ask the user for the review model and effort and for the verify model and effort, offering the current values as defaults (the verify default is the current verify model, else the review model). A model is an OMP selector such as `openai-codex/gpt-6.1-sol`, and the effort one of the levels OMP lists for it (`omp models find <id>`).
3. Show the plan without writing anything:

   ```bash
   python3 <skill-dir>/scripts/setup.py --model <model>:<effort> --verify-model <model>:<effort>
   ```

   It validates the model in OMP (exit 1 or 2 with the reason) and prints every change it would make. `no changes` means everything is already in place.
4. Show the plan to the user and ask for approval. Do not write before they approve.
5. Apply it with the same command plus `--write`. It copies each file it changes or removes, including `~/.omp/agent/config.yml`, to `~/.config/k0siara-skills/backups/<timestamp>/` (or `--backup-dir <dir>`) before writing, and prints that path.
6. Run the step 3 command again. It must print `no changes`. Report the agent files written and removed, the backup path and, for OMP, that new sessions and subagent launches pick the agent up without a restart.

Rerun the skill after installing another harness, to give it the agent too.
