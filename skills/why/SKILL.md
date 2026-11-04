---
name: why
description: "Use when the user asks what was decided, why something is the way it is, or how a feature, flow or rule is supposed to work, and the answer should come from the team's written record instead of guesses. Searches the issue tracker, long-form docs (PRDs, ERDs, design docs), pull requests and local specs in parallel, read-only, and returns a cited answer with confidence levels, conflicts between sources and the open questions with who is likely to know. Triggers: why, /why, why did we, what did we decide about, how is X supposed to work, find what we know about, is this documented."
---

# Why

Answer a question about the product or a decision from what the team has already written down. Every claim carries its source. What the record does not answer is a result too: it becomes a list of open questions and the people likely to know.

Read-only. Never write to the tracker, docs, pull requests or chat, even to leave a note.

## 1. Pin the question

1. Write the question in one sentence, plus the topic keywords and the names, IDs or links the user gave. If the user embeds a guess ("I assume it's because..."), keep it as one hypothesis to test, not the answer.
2. Pin the scope before searching:
   - **Area:** the projects, initiatives, epics and doc spaces the topic belongs to. Derive them from the user's current work: their active and recent tracker issues and projects, specs and notes in the workspace, and the conversation. The workspace instructions (`AGENTS.md`, `CLAUDE.md` and the files they point to) may name doc spaces, tracker rules and where notes live; follow them.
   - **Time window:** default the last 12 months, wider when the topic is older.
3. If the question is too vague to search (no topic, no referent), make the best guess from the conversation, state it in one line and go on. Ask only when two readings would send the search to different places.

## 2. Find the sources

List the tools you can reach for each source kind:

| Source | Typical tools | Best at |
|---|---|---|
| Issue tracker | Linear, Jira, GitHub Issues (CLI, MCP or connector) | The business reason, scope decisions, comments where things got settled |
| Long-form docs | Confluence, Notion, Google Docs | PRDs, ERDs, design docs, rationale written before the code |
| Pull requests and history | `gh`, `git log`, `git log -S`, review threads | Decisions made during review, what actually shipped |
| Workspace notes | Specs, ADRs, meeting notes, prior research files in the workspace | Decisions already captured with the user |
| Team chat | Slack, Teams (read access only) | Decisions that never reached a doc |

A source kind with no reachable tool is a gap, not a skip: report it as "not searchable here". Skip a reachable source only when it provably cannot hold the answer, and say why.

## 3. Investigate in parallel

Start one read-only investigator subagent per reachable source, all in one call when your harness allows, each owning exactly one source. Use your harness's subagent tool; pick a fast model if the harness lets you choose. Each investigator's prompt is the full text of [`references/investigator.md`](references/investigator.md) with its placeholders filled: the question, the scope, the source and the leads you already have.

If subagents cannot reach a source (for example a connector only the main agent has), search that source yourself with the same rules.

When an investigator's report names a lead in another source (a ticket ID in a doc, a PR in a ticket), and that source's investigator did not cover it, send it a follow-up or open it yourself.

## 4. Synthesize

Combine the reports yourself. For every claim:

- **Confidence:**
  - `confirmed`: someone wrote it down in a source you can quote.
  - `supported`: several sources point the same way, none says it outright.
  - `inferred`: your reading of the context, with the chain of reasoning shown.
  - `unknown`: searched and not found; say where and with which queries.
- **Recency and authority:** a later decision overrides an earlier one only when it says so or clearly replaces it. A doc marked draft or a comment that was never acted on is weaker than a merged PR or an accepted decision. Say which is which.
- **Conflicts:** when sources disagree, show both with citations and dates. Do not pick the tidier story.
- **The user's hypothesis:** confirm, refute or mark it unresolved, with evidence. Do not agree because it was offered.

Words like "because", "decided" and "requires" need a citation next to them. Hedge inferences ("likely", "suggests") and show what they rest on.

## 5. Answer

Reply in the user's language:

1. **Answer:** two to five sentences, the direct answer at the highest confidence the evidence allows.
2. **What the record says:** claims grouped by subtopic, each with its confidence, a short verbatim quote and a link or ID with date and author.
3. **Conflicts and stale points**, if any.
4. **Open questions:** each with why it matters, where you looked, and who is likely to know (doc owner, ticket assignee or reporter, PR author, the person who made a related decision). If the user wants to ask them, hand the list to the `ask-around` skill when it is installed.
5. **Sources searched:** per source, the queries and what came back, including empty results and sources that were not searchable.

Save the answer to a file only when the user asks or the workspace instructions say where such notes go.
