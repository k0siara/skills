---
name: to-spec
description: "Use when the user asks for a spec, PRD or RFC, or to turn a discussion into one. Synthesizes what is already decided, grounds it in the code, settles the few remaining decisions in one round of questions, and writes a spec that an agent without the conversation can plan and implement from. Triggers: write a spec, spec this, PRD for <feature>, to-spec, /to-spec."
---

# To spec

Write one spec for one outcome. The reader is a fresh agent or engineer who has none of this conversation: after reading the spec, they can plan and build the change without asking you anything.

The spec says **what** must be true and **why**, plus the design decisions that were actually made. It does not say how to edit each file. That belongs to planning and implementation.

## Instructions that shape the run

Read the workspace and repository instructions (`AGENTS.md`, `CLAUDE.md` and the files they point to) before step 1. They decide where specs live (a docs folder, a topics folder, an issue tracker), their language, file naming, a template that replaces the one here, and which writes need approval. They win over the defaults below.

Defaults when nothing says otherwise:

- Location: `docs/specs/<slug>.md` in the repository the change lives in. For a change across several repositories, ask once where it goes.
- Language: the language the user writes in.
- Writes: show the draft first. Commit, push or publish to a tracker only after the user approves.

If the project has a glossary or decision records (`GLOSSARY.md`, `docs/adr/`), use their terms and respect their decisions. When the user's word conflicts with the glossary, ask which one they mean.

## Process

1. **Collect what is decided.** Read the conversation, the linked task, designs and docs. List the goal, the decisions and the constraints you already have. If there is no agreed problem or goal yet, stop and suggest a grilling session first. A spec cannot settle what nobody decided.
2. **Ground it in the code.** Read every part of the system the change touches: entry points, data flow, who owns each piece of state, external contracts (API, schema, events, stored data) and the tests around them. Find the closest existing feature that solves a similar problem; it is the prior art the design follows or explicitly departs from. Finding facts is your job, never the user's. For a large area, send a subagent and keep only its summary.
3. **Consider two shapes.** When the design is not obvious, sketch at least two structurally different approaches, not two variants of one. Reject a shape that gives one task two ways to be done, gives one piece of state two owners, or makes two lists that must be kept in sync by hand. Choose one and keep one line on why the other lost. Skip this step when only one sensible shape exists, and say so.
4. **Pick the test seams.** Choose where the behaviour is tested: the highest existing seam that can observe it, and as few seams as possible. Name the existing tests the new ones follow. Name the live check (driving the real app or calling the real endpoint) that proves it works end to end.
5. **Check compatibility and rollout.** Go through the list in [`references/template.md`](references/template.md) under *Compatibility and rollout*: clients already in users' hands, stored data, reversibility, release order, flags. Write down what applies. Write `None` when you checked and nothing applies; never drop the section.
6. **Ask one round.** Collect every decision that is still open and that only the user can make: product choices, trade-offs, scope cuts, your seams. Ask them in one numbered message. Give your recommended answer for each, worded so that "yes" accepts it. Never ask what the code, the docs or a quick experiment can answer. When an answer would only change a detail, decide it yourself, mark it as an assumption and move on. Whatever stays open goes to *Open questions*.
7. **Write the spec** with [`references/template.md`](references/template.md). Keep every required section.
8. **Check it** against the list below and fix what fails.
9. **Hand it over.** Show the spec or its path, then list its assumptions and blocking open questions. It stays `Draft` until the user approves; then set `Approved` and save or publish it as the instructions say. Do not create tickets or start implementation. Suggest the next step: planning the work into tasks.

## Rules for the content

- **Behaviour over code.** Describe modules, interfaces, contracts and state ownership by name. Do not write file paths, line numbers or code: they go stale before the work starts. Exception: a short snippet that states a decision more precisely than prose (a schema, a type shape, a state machine). Keep only the part that carries the decision.
- **Every scenario is observable.** Each one has an ID (`S1`, `S2`, …) that tasks can refer to, an actor, an action and a result someone can see or measure. "Works correctly" and "handles errors" are not results. Cover the main path, the important edge cases and the failures. Prefer a few sharp scenarios to a long list of user stories.
- **Facts and assumptions stay apart.** A statement about the current system is something you read in the code. Anything you could not verify is marked `Assumption:`.
- **Decisions keep their reason.** One line per decision: what was chosen and why. Record who decided and when in the *Decision log*.
- **Out of scope is explicit.** Name what someone could reasonably expect from this change but will not get.
- **Plain words.** Cut every word that does no work. Use the short, everyday word and the project's own names for things.
- **One outcome per spec.** When the spec grows into several independent outcomes that could ship on their own, propose splitting it.

## Check before handing over

- Could an agent without this conversation plan the work from the spec alone?
- Does every scenario have an observable result, and does the testing section say where each one is tested?
- Is every open question marked blocking or non-blocking, with someone who answers it?
- Are *Compatibility and rollout* and *Out of scope* filled in, even if only with `None`?
- Are there no file paths, line numbers or code beyond decision snippets?
- Does every claim about today's system come from code you read, and is the rest marked as an assumption?
