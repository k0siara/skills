# PR description examples

These are fictional examples of structure and detail, not evidence for an actual PR. Use the repository's required language and template. Never copy a result unless it was observed for the change being described.

## Small maintenance change

### Avoid

> Updated the CI YAML, removed the old job and cleaned up its configuration. Followed the plan and checked everything. Low risk.

### Prefer

> Remove the duplicate dependency scan: the organization-level workflow already runs it on each PR. The release workflow is unchanged.
>
> Verification: workflow validation passed. Application tests were not run because no application code changed.

The rationale and preserved boundary matter; the sequence of YAML edits does not.

## UI bug fix with limited platform coverage

### Avoid

> Fixed the dialog, updated widgets, added tests and took screenshots in `/tmp/dialog-check/`. All good on mobile.

### Prefer

> The confirmation button was unreachable when the keyboard was open on a small screen. Make the dialog content scroll without moving the primary action out of reach.
>
> ## Verification
> - Widget regression: the button was outside the visible area before the fix and is visible and tappable after it.
> - Android emulator, 360 × 640 logical pixels: opened the keyboard, entered a long label and confirmed successfully; no overflow was reported.
> - iOS was not exercised.

The failure mode and observed coverage are clear, without turning one platform's smoke into a claim about all platforms.

## Service contract and data migration

### Avoid

> Added V42, a nullable field, an index and mapper changes. Tests pass. Two-way door: revert if needed.

### Prefer

> **Rollout prerequisite:** deploy the service before enabling the new client filter. Companion PR: `<client PR link>`.
>
> Add optional `archivedAt` to the response so clients can distinguish archived records. Existing clients can ignore the field; records and their references are not deleted.
>
> ## Verification
> - Contract tests passed for responses with and without an archive timestamp.
> - Migration smoke passed on a disposable database using the supported production database engine: existing records retained their values and the new column was null.
> - Production-volume migration duration was not measured.
>
> ## Risks and rollout
> Migration V42 adds a nullable column and an index. Index creation may hold locks; the unmeasured production-volume impact remains a deployment risk.
>
> Rolling back the service does not remove the column or undo archive timestamps written after deployment. Recovery of those values requires a separate data operation.

A code revert is not a data rollback. State the actual deployment boundary instead of giving a reassuring label.

## Fix with a deliberate gap and a rejected alternative

### Avoid

> Fixed duplicate reminders. Considered several approaches and picked the best one. Some edge cases remain and will be handled later.

### Prefer

> A retried delivery job sent the same reminder twice when the first attempt timed out after the provider had accepted it. Send each reminder with an idempotency key derived from the reminder ID, so the provider drops the retry.
>
> ## Change
> - `ReminderSender` passes the same key on every attempt, including retries.
> - Rename the setting `retry.maxAttempts` to `reminders.retry.maxAttempts`. The old key is no longer read.
> - A per-reminder database lock was rejected: it would be held for the whole provider call and still would not cover a timeout after acceptance.
>
> ## Scope
> - Reminders that were already duplicated are not corrected.
> - Other notification types keep the current retry behavior; tracked in `<issue link>`.
>
> ## Verification
> - Integration test against the provider sandbox: a forced timeout after acceptance resulted in one delivered reminder.
> - Staging load test: p95 send latency 180 ms → 185 ms.
>
> ## Risks and rollout
> Environments that set `retry.maxAttempts` must rename it before deployment; otherwise they fall back to the default of three attempts.

The rejected alternative, the scope and both rename keys answer the obvious review questions.
