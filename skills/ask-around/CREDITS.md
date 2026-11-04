# Credits

Inspired by [Matt Pocock's `to-questionnaire` skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/to-questionnaire) (MIT): interviewing the user only about the send and not the subject, aiming questions at the gap between what the recipient knows and what the user needs, one idea per question, most important first, a short "why this matters" only where a question could be misread, and treating "I don't know" as a useful answer.

This skill uses an independently written workflow: questions grouped per recipient, the current assumption stated for each question, chat-sized messages by default, a check against the written record first, and a step that folds the answers back in. The upstream skill is not a runtime dependency.
