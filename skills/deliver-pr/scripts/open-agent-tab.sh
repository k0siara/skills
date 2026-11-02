#!/usr/bin/env bash
# Starts one interactive omp agent with its first prompt in a new tab of the caller's Herdr space, via hc.
# Used by deliver-pr (stage agents) and rebase-all (one agent per PR).
# Usage: open-agent-tab.sh [--model <omp-model>] [--outlive-parent] <agent-name> <tab-name> <cwd> <prompt>
# Output: one JSON line {agent, address, tab}
set -euo pipefail

usage() { echo "usage: open-agent-tab.sh [--model <omp-model>] [--outlive-parent] <agent-name> <tab-name> <cwd> <prompt>" >&2; exit 2; }

model=""; outlive=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --model) [ "$#" -ge 2 ] || usage; model="$2"; shift 2 ;;
    --outlive-parent) outlive=(--outlive-parent); shift ;;
    --) shift; break ;;
    -*) usage ;;
    *) break ;;
  esac
done
[ "$#" -eq 4 ] || usage
[ -n "${HC_TERMINAL_ID:-}" ] || { echo "not running inside hc (HC_TERMINAL_ID unset)" >&2; exit 1; }
agent="$1"; tab_name="$2"; cwd="$3"; prompt="$4"

space=$(herdr-app ls | jq -r --arg t "$HC_TERMINAL_ID" '.spaces[] | select(any(.tabs[].terminals[]; .terminal == $t)) | .id')
[ -n "$space" ] || { echo "no Herdr space shows terminal $HC_TERMINAL_ID" >&2; exit 1; }

# Without --outlive-parent the agent ends with its caller, as an hc child does.
# hc starts programs with the core's environment, without the user's shell setup (PATH to omp/bun, variables from
# ~/.zshrc). Launch omp through an interactive login shell, like a terminal opened by hand.
# hc rejects a name that a live terminal already uses.
if [ -n "$model" ]; then
  launch='exec omp --model "$2" "$1"'
else
  launch='exec omp "$1"'
fi
addr=$(hc run --bg --json ${outlive[@]+"${outlive[@]}"} --name "$agent" --cwd "$cwd" --label herdr.space="$space" \
  "${SHELL:-/bin/zsh}" -lic "$launch" omp "$prompt" "$model" | jq -r .address)

# The window adopts the labelled terminal asynchronously; wait for its tab (up to ~10 s).
tab=""
for _ in $(seq 40); do
  tab=$(herdr-app ls | jq -r --arg t "$addr" '.spaces[].tabs[] | select(any(.terminals[]; .terminal == $t)) | .id')
  [ -n "$tab" ] && break
  sleep 0.25
done
if [ -n "$tab" ]; then
  herdr-app do tab.rename --id "$tab" --name "$tab_name" >/dev/null
else
  echo "tab for $addr did not appear; agent runs unnamed" >&2
fi

jq -nc --arg a "$agent" --arg ad "$addr" --arg tb "$tab" '{agent:$a,address:$ad,tab:$tb}'
