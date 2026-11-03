---
name: to-tickets
description: "Use when the user asks to break a spec, plan or discussion into tickets or issues, or to plan the work of a spec. Cuts the work into vertical slices that each fit one agent, one repository and one PR, gives each its blocking edges, acceptance criteria tied to the spec's scenarios and a way to verify it, shows the breakdown for approval and then publishes it in dependency order to the configured tracker. Triggers: to-tickets, /to-tickets, break this into tickets, create issues for <spec>, plan the work."
---

# To tickets

Turn one spec (or an agreed discussion) into a set of tickets. Each ticket is a contract a fresh agent can pick up alone: it knows what to build, when it is done and what it waits for, without the conversation and without the other tickets.

The set of tickets is the plan. Their blocking edges give the order; there is no separate phase document unless the workspace asks for one.

## Instructions that shape the run

Read the workspace and repository instructions (`AGENTS.md`, `CLAUDE.md` and the files they point to) before step 1. They decide:

- the tracker (GitHub, Linear, local files) and how to write to it,
- the ticket template, title convention and language: a project template replaces [`references/ticket-template.md`](references/ticket-template.md), and its required fields win,
- the parent: an epic or plan issue with its own template, or only a link to the spec,
- the label and status vocabulary, and who may mark a ticket ready for an agent,
- which writes need approval.

For Linear, follow the `using-linear` skill for every write. Never invent labels, statuses or fields. Never mark tickets ready for an agent unless the instructions allow it.

Defaults when nothing says otherwise: local files next to the spec, `<spec-dir>/<spec-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order, one ticket per file; the spec's language; every write after explicit approval.

## Process

1. **Read the source completely.** For a spec, read its body, decisions and comments. If it has blocking open questions, stop and list them: tickets built on an open decision get rebuilt. Without a spec, check that the problem, the outcome and the scope are agreed; if not, suggest writing a spec first (`to-spec`).
2. **Ground it in the code.** Find where each scenario lands: repositories, modules, contracts, existing tests. Look for a prefactor that makes the change easy ("make the change easy, then make the easy change"). Send a subagent for a large area and keep only its summary.
3. **Draft the slices** by the rules below.
4. **Check the draft** against the list at the end. Fix it before you show it.
5. **Show the breakdown and ask once.** A numbered list; per ticket: title, repository, blocked by, what it delivers (one line of behaviour), scenarios covered, number of criteria. Then the coverage line (every scenario → tickets) and the tickets that can start at once. Ask: is the granularity right, are the edges real gates, should any ticket be merged or split. Give your recommendation for each. Iterate until the user approves this exact set.
6. **Publish in dependency order**, blockers first, so every edge points at a real identifier. Use the tracker's native parent and blocking relations where it has them, and keep the `Blocked by` section consistent with them. Link each ticket to the spec and the parent. Read the tracker state again just before writing; if something changed since approval, show the new diff and ask again. Do not close or rewrite a parent; adding children is part of the approved set.
7. **Report** what was actually written, read back from the tracker: links, relations, the tickets that can start now, and the ones waiting for a person.

## Slicing rules

- **Vertical.** A ticket cuts a narrow but complete path through every layer it needs (data, API, UI, tests), so its result can be shown or checked on its own. A ticket that only adds a layer nobody can observe is not a slice.
- **One repository, one PR, one outcome.** Work across repositories becomes dependent tickets. The side that provides a contract ships first and keeps working for the consumers already released; the consumer follows.
- **Fits one agent.** One area, at most three acceptance criteria, small enough for one fresh context window. When a ticket needs more, split it instead of adding criteria.
- **Prefactor first.** A refactor that makes the slices simple is its own ticket that the slices wait for.
- **Wide mechanical changes go expand–contract.** When one rename or retype breaks callers across the codebase, add the new form beside the old, move callers in batches (one ticket each, blocked by the expand), then delete the old form in a ticket blocked by every batch.
- **Tests and docs live in the ticket they belong to.** No separate "write tests" or "update docs" ticket.
- **Edges are real gates.** A ticket waits for another only when it cannot start or cannot pass without it. No cycles. Prefer independent tickets that can run in parallel.
- **People get their own tickets.** A step only a person can do (store submission, credentials, a product sign-off, a manual test) is a separate ticket that names the person and what confirms it is done.
- **Small work stays small.** A change that fits one ticket gets one ticket, without artificial phases.

## Writing a ticket

Use the project template, else [`references/ticket-template.md`](references/ticket-template.md).

- Describe behaviour and contracts by name, from the user's point of view. No file paths, line numbers or code: they go stale while the ticket waits. Exceptions: fields the project template requires, such as allowed paths, and a short snippet that states a decision more precisely than prose.
- Every acceptance criterion is observable and can be checked on its own. "Works correctly" is not a criterion.
- Carry the spec's binding decisions into the ticket that they constrain. A fresh agent reads the ticket, not the spec.
- Name what is out of scope where an agent could plausibly overreach.

## Check before showing the breakdown

- Is every spec scenario covered by at least one ticket, and does no ticket add scope the spec does not have?
- Does every ticket have one repository, at most three observable criteria, a way to verify and an explicit `Blocked by`?
- Are all edges real gates, with no cycle, and can the first tickets start at once?
- Does every step that needs a person have its own ticket?
- Could an agent finish any single ticket from its text alone?
