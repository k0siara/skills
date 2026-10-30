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

This gives the reviewer a failure mode and observed coverage without turning one platform's smoke into a claim about all platforms.

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

## Updating an existing description

Replace stale claims rather than appending another dated update. If a final relevant edit followed the last test run, say that the current version has not been rechecked. Retain human-written requirements and approval references; do not silently replace a conflicting statement with an agent's assumption.

Mandatory security, compliance or change-management fields remain mandatory. Reference the permitted internal record rather than copying customer data, secrets or an entire approval history into the PR.
