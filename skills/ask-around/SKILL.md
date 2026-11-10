---
name: ask-around
description: "Use when open questions need answers from other people: drafts short, ready-to-send questions per person from the `why` skill or the conversation, each with the current assumption to confirm, never sends them, and folds the answers back in. Triggers: ask-around, /ask-around, who should I ask, prepare questions for, ask the team, draft questions to."
---

# Ask around

Turn what the user cannot answer alone into questions for the people who can.

Ask the user only about the send (who gets which question, what they need back, by when), never the questions themselves.

## 1. Collect the open questions

1. Take the open questions from the conversation: the `why` skill's open-questions list, a spec's open decisions, or what the user names.
2. Drop every question the written record already answers. Questions from a `why` run in this conversation are already checked. If the questions have not been checked against the record yet (tracker, docs, pull requests, workspace notes) and the `why` skill is installed, run it first and keep only what it leaves open. Otherwise say the questions are unchecked.
3. For each question note what it unblocks (a decision, a ticket, a spec section) and the current assumption, if there is one.

## 2. Pick the recipients

Assign each question to one person: the one most likely to answer it with authority (decision owner, doc author, ticket assignee or reporter, owner of the code or service). Use the people `why` found; otherwise propose names from the sources with the reason.

Show the user one table, `# | question | proposed recipient | why them | needed by`, and get one confirmation for all of it. Questions nobody can be assigned stay on a separate list.

## 3. Write the questions

One block per recipient, in the language the user uses with that person; ask once if unclear.

- **Opening:** one or two sentences of context the recipient needs and what the answers unblock. Assume they were not in the conversation.
- **Questions:** most important first, as many as the need requires. Each question is one idea, never compound, and answerable in a line:
  - State the current assumption and ask to confirm or correct it: "We assume X. Correct, or how does it work?"
  - When there are known options, list them (`a`, `b`, `c`) so the answer can be a letter.
  - Add a short "why it matters" only where the question could be misread or get a throwaway answer.
- **Close:** "I don't know" and partial answers are fine; ask who else to ask if they are not the right person.

Plain language, no internal shorthand the recipient may not share, no file paths unless the recipient works in that code.

Default form is a short chat message. For many questions, heavy context or a meeting, write a document: title, purpose, context, questions under headings with an empty answer line each, closing "anything we did not ask?".

## 4. Hand over

Show every block in its final form in the chat. Save to a file only where the workspace instructions say such notes go, or where the user asks.

Never send, post or schedule anything yourself, even when a messaging tool is available. If the user asks you to send it, follow the workspace rules for that channel and show the exact text and recipient for approval first.

## 5. Fold in the answers

When the user brings answers back (pasted, forwarded or as a link):

1. Match each answer to its question. Mark it `answered`, `partial`, `redirected` (with the new person) or `open`.
2. List what changes: assumptions confirmed or overturned, decisions now possible, and the spec, ticket or note that needs an update. Propose those updates; do not apply them without the user's approval.
3. For `partial`, `redirected` and `open` questions, propose a follow-up round with step 2.
