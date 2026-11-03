#!/usr/bin/env python3
"""setup.py: write the `review` agent for every harness found.

  setup.py [--model MODEL[:EFFORT]] [--write] [--backup-dir DIR]

`review` is a plain agent with no instructions of its own: the delegating prompt says what to do
(run `verify-changes`, run `pre-pr-review`, review against a checklist). It exists so these
subagents run on a chosen model.

MODEL is an OMP model selector (`provider/id`, e.g. `openai-codex/gpt-6.1-sol`, or a bare id OMP
resolves to one provider); EFFORT is its thinking level (default high). Without --model the model
comes from ~/.config/k0siara-skills/config.yml.

Without --write nothing changes: it prints the diff of everything it would write or remove. With
--write it copies each file it changes or removes to the backup directory, then writes:

  ~/.config/k0siara-skills/config.yml   model + effort (the source of truth)
  ~/.omp/agent/agents/review.md         + task.agentModelOverrides in ~/.omp/agent/config.yml
  ~/.codex/agents/review.toml           no model: the subagent uses the session's model
  ~/.claude/agents/review.md            no model: the subagent uses the session's model

It also removes the agents earlier versions created (OBSOLETE_AGENTS) and their OMP overrides.
Only OMP gets a model: its `task` tool has no model field, so the override is the only way to pin one.
Files for a harness are written only when its CLI (omp, codex, claude) is on PATH.

Exit codes: 0 done, 1 OMP cannot run the model or a command failed, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

AGENT = "review"
DESCRIPTION = "Plain subagent on a dedicated model: does exactly what the delegating prompt asks (verification, pre-PR review, PR review)."
OBSOLETE_AGENTS = ("k0siara-reviewer", "k0siara-verifier", "code-review-technical-agent", "code-review-architecture-agent")
HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "k0siara-skills"
CONFIG = CONFIG_DIR / "config.yml"
OMP_CONFIG = HOME / ".omp" / "agent" / "config.yml"
PROMPT = (Path(__file__).resolve().parent.parent / "roles" / "review.md").read_text()
OVERRIDES = "task.agentModelOverrides"
HARNESS_AGENT_FILES = {
    "omp": lambda name: HOME / ".omp" / "agent" / "agents" / f"{name}.md",
    "codex": lambda name: HOME / ".codex" / "agents" / f"{name}.toml",
    "claude": lambda name: HOME / ".claude" / "agents" / f"{name}.md",
}


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"setup: {message}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"`{' '.join(cmd[:4])}` exited {proc.returncode}: {proc.stderr.strip()[-500:]}")
    return proc.stdout


# ---------- config.yml: only this script writes it, so it reads only this format ----------

def read_config() -> tuple[str, str] | None:
    if not CONFIG.exists():
        return None
    values = dict(re.findall(r"^(model|effort): (\S+)$", CONFIG.read_text(), re.M))
    return (values["model"], values["effort"]) if {"model", "effort"} <= values.keys() else None


def render_config(model: str, effort: str) -> str:
    return f"# Written by setup-k0siara-skills. Change it by running the skill again.\nmodel: {model}\neffort: {effort}\n"


def omp_resolve(model: str, effort: str) -> str:
    """The OMP selector for model; fails unless OMP lists it with effort."""
    model_id = model.split("/", 1)[-1]
    provider = model.split("/", 1)[0] if "/" in model else None
    found = json.loads(run(["omp", "models", "find", model_id, "--json"]))["models"]
    hits = [m for m in found if m["id"] == model_id and provider in (None, m["provider"])]
    if not hits:
        fail(f"OMP has no model {model} (see `omp models find {model_id}`)")
    if len(hits) > 1:
        fail(f"{model_id} comes from several providers; pass one of " + ", ".join(m["selector"] for m in hits), 2)
    efforts = hits[0].get("thinking") or []
    if efforts and effort not in efforts:
        fail(f"{hits[0]['selector']} supports effort {', '.join(efforts)}, not {effort}", 2)
    return hits[0]["selector"]


# ---------- agent files ----------

def markdown_agent(harness: str) -> str:
    lines = ["---", f"name: {json.dumps(AGENT)}", f"description: {json.dumps(DESCRIPTION)}"]
    if harness == "omp":
        lines.append('spawns: "*"')  # pre-pr-review run in this agent starts its own reviewers
    return "\n".join(lines + ["---", ""]) + PROMPT


def codex_agent() -> str:
    return "\n".join([
        f"name = {json.dumps(AGENT)}",
        f"description = {json.dumps(DESCRIPTION)}",
        f"developer_instructions = {json.dumps(PROMPT)}",  # a JSON string is a valid TOML basic string
    ]) + "\n"


# ---------- plan and apply ----------

def main() -> None:
    parser = argparse.ArgumentParser(prog="setup.py", description="Write the review agent.")
    parser.add_argument("--model", metavar="MODEL[:EFFORT]")
    parser.add_argument("--write", action="store_true", help="apply the plan (default: show it only)")
    parser.add_argument("--backup-dir", type=Path, help="where to copy files before changing them")
    args = parser.parse_args()

    if args.model:
        m = re.fullmatch(r"([^\s:]+)(?::([a-z]+))?", args.model)
        if not m:
            fail(f"--model {args.model!r}: expected MODEL[:EFFORT]", 2)
        model, effort = m.group(1), m.group(2) or "high"
    elif current := read_config():
        model, effort = current
    else:
        fail("no model configured: pass --model MODEL[:EFFORT]", 2)
    found = [name for name in HARNESS_AGENT_FILES if shutil.which(name)]
    print(f"harnesses found: {', '.join(found) or 'none'}")

    files: dict[Path, str] = {CONFIG: render_config(model, effort)}
    for harness in found:
        files[HARNESS_AGENT_FILES[harness](AGENT)] = codex_agent() if harness == "codex" else markdown_agent(harness)
    removed = [path for harness in found for name in OBSOLETE_AGENTS
               if (path := HARNESS_AGENT_FILES[harness](name)).exists()]

    overrides = new_overrides = {}
    if "omp" in found:
        overrides = json.loads(run(["omp", "config", "get", OVERRIDES, "--json"]))["value"] or {}
        new_overrides = {k: v for k, v in overrides.items() if k not in OBSOLETE_AGENTS}
        new_overrides[AGENT] = f"{omp_resolve(model, effort)}:{effort}"

    old = {path: path.read_text() if path.exists() else None for path in files}
    changed = [path for path in files if old[path] != files[path]]
    for path in changed:
        print(f"{'update' if old[path] is not None else 'create'} {path}")
        if old[path] is not None:
            sys.stdout.writelines(difflib.unified_diff(
                old[path].splitlines(True), files[path].splitlines(True), "current", "new"))
    for path in removed:
        print(f"remove {path}")
    for agent in sorted(overrides.keys() | new_overrides.keys()):
        if overrides.get(agent) != new_overrides.get(agent):
            print(f"omp config {OVERRIDES}.{agent}: {overrides.get(agent)} -> {new_overrides.get(agent)}")
    if not changed and not removed and new_overrides == overrides:
        print("no changes")
        return
    if not args.write:
        print("dry run: nothing written (pass --write)")
        return

    backup = args.backup_dir or CONFIG_DIR / "backups" / time.strftime("%Y%m%d-%H%M%S")
    touched = [path for path in changed if old[path] is not None] + removed
    if new_overrides != overrides and OMP_CONFIG.exists():
        touched.append(OMP_CONFIG)
    for path in touched:
        target = backup / path.relative_to(HOME)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    if touched:
        print(f"backup: {backup}")
    for path in changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[path])
    for path in removed:
        path.unlink()
    if new_overrides != overrides:
        # omp merges the one key into its config.yml and keeps every other setting.
        run(["omp", "config", "set", OVERRIDES, json.dumps(new_overrides)])
    print("written")


if __name__ == "__main__":
    main()
