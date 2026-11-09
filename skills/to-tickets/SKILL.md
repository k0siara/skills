---
name: to-tickets
description: "Use when the user asks to break a spec, plan or discussion into tickets or issues, to write a single ticket for one change, or to plan the work of a spec. Works for one standalone ticket, tickets under an existing parent, or a large plan with a new parent and many children. Cuts the work into vertical slices that each fit one agent, one repository and one PR, writes every ticket so that the ticket plus its parent is the complete brief an agent needs (what, where, why, how to verify), proves that with a blind-read check, shows the exact drafts for approval and then publishes them in dependency order to the configured tracker. Triggers: to-tickets, /to-tickets, break this into tickets, create issues for <spec>, plan the work."
---

# To tickets

Turn one spec (or an agreed discussion) into tickets: a single ticket, a few tickets under an existing parent, or a large plan with a new parent and many children. Each ticket is a contract a fresh agent can pick up alone: from the tracker, without the spec, the conversation or the other tickets, it knows what to build, where, why this way, when it is done and what it waits for.

The set of tickets is the plan. Their blocking edges give the order; there is no separate phase document unless the workspace asks for one.

## The non-negotiable rule: tickets are self-contained

The reader of a ticket is an agent that has the tracker and the repository, and nothing else. It cannot open the spec, your notes, the conversation or any file on your machine.

- **A child ticket plus its parent chain is the complete brief.** Everything the agent needs to implement, decide and verify is written in that text.
- **Only reachable references.** A ticket may point to other tickets in the same tracker, code on the repository's default branch, pull requests and public URLs. It never points to local files or folders, a spec or document outside the tracker, the conversation, or anything only you can open.
- **No source-internal numbering.** Never cite spec section numbers, decision ids or scenario ids ("§6", "D24", "S3") unless that numbering is itself written in the parent. State the decision itself.
- **The spec's content moves into the tracker.** Everything binding from the spec (goal, target architecture, decisions with their reasons, rejected alternatives, terms, constraints, order) is written into the parent. A link to the spec may be added only when every reader can open it, and only as an extra: the parent must stand without it.

Workspace instructions may change the template, the language, the fields and the tracker. They never relax this rule.

## Instructions that shape the run

Read the workspace and repository instructions (`AGENTS.md`, `CLAUDE.md` and the files they point to) before step 1. They decide:

- the tracker (GitHub, Linear, local files) and how to write to it,
- the ticket template, title convention and language: a project template replaces [`references/ticket-template.md`](references/ticket-template.md) and its required fields win, but the content the self-containment rule needs is still written,
- where the parent sits: an existing epic or plan issue, or a new parent for this spec,
- the label and status vocabulary, and who may mark a ticket ready for an agent,
- which writes need approval.

For Linear, follow the `using-linear` skill for every write. Never invent labels, statuses or fields. Never mark tickets ready for an agent unless the instructions allow it.

Defaults when nothing says otherwise: local files next to the spec, `<spec-dir>/<spec-slug>/tickets/<NN>-<slug>.md`, the parent as `00-parent.md`, children numbered from `01` in dependency order, one ticket per file; the spec's language; every write after explicit approval.

## Pick the shape

Decide the shape after grounding the work in the code (step 2), and say which one you chose when you show the drafts.

| Shape | When | What gets written |
|---|---|---|
| **Standalone ticket** | The work fits one ticket and belongs to no existing epic | One ticket from the standalone template: the child's sections plus the parent's (problem and goal, decisions with reasons, rejected alternatives, terms) folded in. No parent is created for it. |
| **Under an existing parent** | One or more tickets join an epic or plan that already exists | Children from the child template, plus an approved edit that adds to the existing parent whatever shared context it lacks and lists the new children. |
| **New parent with children** | A plan with several slices and no parent yet | A new parent from the parent template, then its children. |

Never create a parent just to hold one ticket. The rules below apply to every shape; for a standalone ticket "the parent" means the parent sections inside the ticket itself.

## Two layers: parent and child

Shared context is written once, in the parent. Each child adds what its one change needs. Nothing binding stays outside the tracker.

**The parent** (a new one for this spec, or an existing epic the work joins) carries:

- the problem and the goal,
- the target architecture (a short diagram when more than two parts move),
- every binding decision with its reason, and the rejected alternatives with why they were rejected,
- the terms the children use, defined once,
- the facts about today's code that several children rely on,
- constraints and what the whole effort leaves out of scope,
- the children, their order and the dependency picture, and phases if the spec has them.

When the work joins an existing parent, add the missing shared context to that parent as an approved edit instead of leaving it in the spec.

**The child** carries:

- a first line that sends the reader to the parent ("Read the parent <reference> first"),
- **Context**: how the code behaves today where this change lands (named classes, modules, flows, existing tests), and why the change is needed now,
- **What to build**: contracts, names, steps and behaviour, precise enough that two agents would build the same thing,
- **Decisions**: the decisions that constrain this change, copied in with their reason. General principles stay in the parent; a decision that changes how this ticket is built is written here even if the parent has it too,
- **Rejected approaches** where an agent could plausibly take another route,
- **Out of scope**, **Acceptance criteria**, **How to verify**, and **Blocked by** with what each blocker provides.

## Process

1. **Read the source completely.** For a spec, read its body, decisions and comments. If it has blocking open questions, stop and list them: tickets built on an open decision get rebuilt. Without a spec, check that the problem, the outcome and the scope are agreed; if not, suggest writing a spec first (`to-spec`).
2. **Ground it in the code.** Find where each scenario lands: repositories, modules, contracts, existing tests, and the current behaviour the tickets will describe as context. Look for a prefactor that makes the change easy ("make the change easy, then make the easy change"). Send a subagent for a large area and keep only its summary.
3. **Pick the shape, then draft:** the parent (new, or the edit to the existing one) before its children, or the one standalone ticket, by the rules below. Write the full text of every ticket exactly as it will be published. Use stable placeholders only for identifiers the tracker has not assigned yet.
4. **Check the drafts** against the list at the end and fix them.
5. **Run the blind-read gate on every ticket** (below). Fix every gap it finds and rerun it for the changed tickets until it passes.
6. **Show the drafts and ask once.** Show the full text of every ticket and of every edit to an existing ticket, never only a summary. For one or a few tickets, put the full text in the reply. For more, write them to files (one per ticket, one for edits to existing tickets), give the path, and add a compact table to the reply: per ticket title, repository, parent, blocked by, one line of behaviour, scenarios covered, number of criteria. Add the coverage line (every scenario → tickets), the tickets that can start at once and the gate result. Ask in one round: is the granularity right, are the edges real gates, should any ticket be merged or split, plus every open decision, each with your recommendation. Iterate until the user approves this exact text.
7. **Publish in dependency order**, blockers first, so every edge points at a real identifier. Use the tracker's native parent and blocking relations where it has them, and keep the `Blocked by` sections consistent with them. Resolve every placeholder in a second pass once all identifiers exist. Add the queue label or status that lets automation start work only after the relations are written and read back; otherwise a running scheduler can pick up a ticket before its blockers exist. Before retrying a write that may have succeeded, look the ticket up by title so a retry does not create a duplicate. Read the tracker state again just before writing; if something changed since approval, show the new diff and ask again. Do not close or rewrite a parent beyond the approved edits.
8. **Read back and report.** Fetch every published ticket from the tracker and check: no unresolved placeholder, no reference the reader cannot open, parents and relations as approved. Report what was actually written: links, relations, the tickets that can start now and the ones waiting for a person.

## The blind-read gate

The proof that a ticket is self-contained. It runs for every ticket, every time, before the drafts are shown.

- **The reader is isolated:** a subagent that receives only the rendered text of one ticket and its parent chain (none for a standalone ticket), exactly as the tracker will show it, plus read-only access to the repository's default branch. It gets no spec, no conversation, no other ticket and no planning files. Independent tickets can go to parallel readers; the parent is also read alone once.
- **The reader returns:** what it would build and where; why it is built this way; how it would prove each acceptance criterion; every question it would have to ask; every reference it could not open; every term it could not resolve.
- **The gate passes** when the reader's account matches the intent and it has no blocking question. A question, an unreachable reference or a wrong account is a gap in the ticket: fix the text (usually by moving context from the spec into the parent or the child), not the reader's prompt.
- **If no isolated reader is available,** say so when showing the drafts and do not call the tickets self-contained.

## Slicing rules

- **Vertical.** A ticket cuts a narrow but complete path through every layer it needs (data, API, UI, tests), so its result can be shown or checked on its own. A ticket that only adds a layer nobody can observe is not a slice.
- **One repository, one PR, one outcome.** Work across repositories becomes dependent tickets. The side that provides a contract ships first and keeps working for the consumers already released; the consumer follows.
- **Fits one agent.** One area, at most three acceptance criteria, small enough for one fresh context window. When a ticket needs more criteria, split it. The limit is on scope; it never limits context, decisions or verification detail.
- **Prefactor first.** A refactor that makes the slices simple is its own ticket that the slices wait for.
- **Wide mechanical changes go expand–contract.** When one rename or retype breaks callers across the codebase, add the new form beside the old, move callers in batches (one ticket each, blocked by the expand), then delete the old form in a ticket blocked by every batch.
- **Tests and docs live in the ticket they belong to.** No separate "write tests" or "update docs" ticket.
- **Edges are real gates.** A ticket waits for another only when it cannot start or cannot pass without it. No cycles. Prefer independent tickets that can run in parallel.
- **People get their own tickets.** A step only a person can do (store submission, credentials, a product sign-off, a manual test, a rollout decision) is a separate ticket that names the person and what confirms it is done.
- **Small work stays small.** A change that fits one ticket gets one ticket, without artificial phases or a parent of its own (see "Pick the shape").

## Writing a ticket

Use the project template, else [`references/ticket-template.md`](references/ticket-template.md).

- Name things precisely: classes, interfaces, modules, functions, flags, endpoints, test suites. A path is fine when it is how the agent finds the place to change; leave out line numbers, which go stale. A short snippet is fine when it states a contract or decision more precisely than prose.
- Describe today's behaviour before the change, so the agent recognises the code it is about to touch and notices when it has moved.
- Give the reason with every decision. An agent that knows why can handle the case the ticket did not foresee.
- Every acceptance criterion is observable and can be checked on its own. "Works correctly" is not a criterion.
- "How to verify" names the tests to add or extend, the existing tests to follow as a pattern, the commands that must pass and how to see the result live.
- Name what is out of scope where an agent could plausibly overreach.

## Check before the blind-read gate

- Is every spec scenario covered by at least one ticket, and does no ticket add scope the spec does not have?
- Does every ticket have one repository, at most three observable criteria, a way to verify and an explicit `Blocked by`?
- Does any ticket reference something the reader cannot open (a local path, an outside document, the conversation) or cite source-internal numbering? Is everything binding from the spec written in the parent or a child?
- Are all edges real gates, with no cycle, and can the first tickets start at once?
- Do existing tickets you add edges to state the opposite dependency in their text ("Depends on X" while the new edge says they block X's children)? A new edge can create a cycle in prose that the tracker does not see: raise it as a decision and fix both texts in the approved set.
- Does every label the spec asks for (phase, area) exist in the tracker? If not, carry it in the description text and ask before creating labels.
- Does every step that needs a person have its own ticket?
