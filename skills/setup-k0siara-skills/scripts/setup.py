#!/usr/bin/env python3
"""setup.py: write the k0siara-reviewer and k0siara-verifier agents for every harness found.

  setup.py [--role reviewer=MODEL[:EFFORT]] [--role verifier=MODEL[:EFFORT]] [--write] [--backup-dir DIR]

MODEL is an OMP model selector (`provider/id`, e.g. `openai-codex/gpt-6.1-sol`, or a bare id OMP
resolves to one provider); EFFORT is its thinking level (default high). Roles not given on the
command line come from ~/.config/k0siara-skills/config.yml.

Without --write nothing changes: it prints the diff of everything it would write. With --write it
copies each file it changes to the backup directory, then writes:

  ~/.config/k0siara-skills/config.yml     role -> model + effort (the source of truth)
  ~/.omp/agent/agents/k0siara-<role>.md   + task.agentModelOverrides in ~/.omp/agent/config.yml
  ~/.codex/agents/k0siara-<role>.toml     no model: the subagent uses the session's model
  ~/.claude/agents/k0siara-<role>.md      no model: the subagent uses the session's model

Only OMP gets a model: its `task` tool has no model field, so the override is the only way to pin one.
Files for a harness are written only when its CLI (omp, codex, claude) is on PATH.

Exit codes: 0 done, 1 OMP cannot run a configured model or a command failed, 2 bad arguments.
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
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

ROLES = ("reviewer", "verifier")
HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "k0siara-skills"
CONFIG = CONFIG_DIR / "config.yml"
OMP_CONFIG = HOME / ".omp" / "agent" / "config.yml"
ROLE_DIR = Path(__file__).resolve().parent.parent / "roles"
OVERRIDES = "task.agentModelOverrides"
DESCRIPTIONS = {
    "reviewer": "Independent read-only code reviewer (pre-pr-review). Never edits, commits or publishes.",
    "verifier": "Runs a change's checks and verification (verify-changes); may fix failures in scope, never commits.",
}
# OMP's bundled reviewer tools; `spawns` lets a reviewer that runs pre-pr-review start its own reviewers.
OMP_REVIEWER_TOOLS = ["read", "find", "grep", "glob", "bash", "lsp", "web_search", "ast_grep"]
CLAUDE_EDIT_TOOLS = "Edit, Write, NotebookEdit"


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"setup: {message}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"`{' '.join(cmd[:4])}` exited {proc.returncode}: {proc.stderr.strip()[-500:]}")
    return proc.stdout


@dataclass
class Role:
    name: str
    model: str
    effort: str

    @property
    def agent(self) -> str:
        return f"k0siara-{self.name}"

    @property
    def prompt(self) -> str:
        return (ROLE_DIR / f"{self.name}.md").read_text()


# ---------- config.yml: only this script writes it, so it reads only this format ----------

def read_config() -> dict[str, tuple[str, str]]:
    if not CONFIG.exists():
        return {}
    roles: dict[str, dict[str, str]] = {}
    current = None
    for line in CONFIG.read_text().splitlines():
        if m := re.fullmatch(r"  ([a-z]+):", line):
            current = roles.setdefault(m.group(1), {})
        elif current is not None and (m := re.fullmatch(r"    (model|effort): (\S+)", line)):
            current[m.group(1)] = m.group(2)
    return {n: (r["model"], r["effort"]) for n, r in roles.items() if n in ROLES and {"model", "effort"} <= r.keys()}


def render_config(roles: list[Role]) -> str:
    lines = ["# Written by setup-k0siara-skills. Change it by running the skill again.", "roles:"]
    for role in roles:
        lines += [f"  {role.name}:", f"    model: {role.model}", f"    effort: {role.effort}"]
    return "\n".join(lines) + "\n"


def omp_resolve(role: Role) -> str:
    """The OMP selector for role.model; fails unless OMP lists it with role.effort."""
    model_id = role.model.split("/", 1)[-1]
    provider = role.model.split("/", 1)[0] if "/" in role.model else None
    found = json.loads(run(["omp", "models", "find", model_id, "--json"]))["models"]
    hits = [m for m in found if m["id"] == model_id and provider in (None, m["provider"])]
    if not hits:
        fail(f"{role.name}: OMP has no model {role.model} (see `omp models find {model_id}`)")
    if len(hits) > 1:
        fail(f"{role.name}: {model_id} comes from several providers; pass one of "
             + ", ".join(m["selector"] for m in hits), 2)
    efforts = hits[0].get("thinking") or []
    if efforts and role.effort not in efforts:
        fail(f"{role.name}: {hits[0]['selector']} supports effort {', '.join(efforts)}, not {role.effort}", 2)
    return hits[0]["selector"]


# ---------- agent files ----------

def frontmatter(fields: list[tuple[str, str | list[str]]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, list):
            lines += [f"{key}:"] + [f"  - {item}" for item in value]
        else:
            lines.append(f"{key}: {json.dumps(value)}")
    return "\n".join(lines + ["---", ""])


def omp_agent(role: Role) -> str:
    fields: list[tuple[str, str | list[str]]] = [("name", role.agent), ("description", DESCRIPTIONS[role.name])]
    if role.name == "reviewer":
        fields += [("tools", OMP_REVIEWER_TOOLS), ("spawns", [role.agent])]
    return frontmatter(fields) + role.prompt


def codex_agent(role: Role) -> str:
    return "\n".join([
        f"name = {json.dumps(role.agent)}",
        f"description = {json.dumps(DESCRIPTIONS[role.name])}",
        f"developer_instructions = {json.dumps(role.prompt)}",  # a JSON string is a valid TOML basic string
    ]) + "\n"


def claude_agent(role: Role) -> str:
    fields: list[tuple[str, str | list[str]]] = [("name", role.agent), ("description", DESCRIPTIONS[role.name])]
    if role.name == "reviewer":
        fields.append(("disallowedTools", CLAUDE_EDIT_TOOLS))
    return frontmatter(fields) + role.prompt


# ---------- plan and apply ----------

def main() -> None:
    parser = argparse.ArgumentParser(prog="setup.py", description="Write the k0siara role agents.")
    parser.add_argument("--role", action="append", default=[], metavar="ROLE=MODEL[:EFFORT]")
    parser.add_argument("--write", action="store_true", help="apply the plan (default: show it only)")
    parser.add_argument("--backup-dir", type=Path, help="where to copy files before changing them")
    args = parser.parse_args()

    wanted = read_config()
    for item in args.role:
        m = re.fullmatch(r"([a-z]+)=([^\s:]+)(?::([a-z]+))?", item)
        if not m or m.group(1) not in ROLES:
            fail(f"--role {item!r}: expected reviewer|verifier=MODEL[:EFFORT]", 2)
        wanted[m.group(1)] = (m.group(2), m.group(3) or "high")
    missing = [name for name in ROLES if name not in wanted]
    if missing:
        fail(f"no model for {', '.join(missing)}: pass --role {missing[0]}=MODEL[:EFFORT]", 2)
    roles = [Role(name, *wanted[name]) for name in ROLES]
    found = [name for name in ("omp", "codex", "claude") if shutil.which(name)]
    print(f"harnesses found: {', '.join(found) or 'none'}")

    files: dict[Path, str] = {CONFIG: render_config(roles)}
    overrides = new_overrides = {}
    if "omp" in found:
        overrides = json.loads(run(["omp", "config", "get", OVERRIDES, "--json"]))["value"] or {}
        new_overrides = dict(overrides)
    for role in roles:
        if "omp" in found:
            new_overrides[role.agent] = f"{omp_resolve(role)}:{role.effort}"
            files[HOME / ".omp" / "agent" / "agents" / f"{role.agent}.md"] = omp_agent(role)
        if "codex" in found:
            files[HOME / ".codex" / "agents" / f"{role.agent}.toml"] = codex_agent(role)
        if "claude" in found:
            files[HOME / ".claude" / "agents" / f"{role.agent}.md"] = claude_agent(role)

    old = {path: path.read_text() if path.exists() else None for path in files}
    changed = [path for path in files if old[path] != files[path]]
    for path in changed:
        print(f"{'update' if old[path] is not None else 'create'} {path}")
        if old[path] is not None:
            sys.stdout.writelines(difflib.unified_diff(
                old[path].splitlines(True), files[path].splitlines(True), "current", "new"))
    for agent in sorted(new_overrides):
        if overrides.get(agent) != new_overrides[agent]:
            print(f"omp config {OVERRIDES}.{agent}: {overrides.get(agent)} -> {new_overrides[agent]}")
    if not changed and new_overrides == overrides:
        print("no changes")
        return
    if not args.write:
        print("dry run: nothing written (pass --write)")
        return

    backup = args.backup_dir or CONFIG_DIR / "backups" / time.strftime("%Y%m%d-%H%M%S")
    touched = [path for path in changed if old[path] is not None]
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
    if new_overrides != overrides:
        # omp merges the one key into its config.yml and keeps every other setting.
        run(["omp", "config", "set", OVERRIDES, json.dumps(new_overrides)])
    print("written")


if __name__ == "__main__":
    main()
