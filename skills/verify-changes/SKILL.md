---
name: verify-changes
description: "Use when changes in a worktree must be proven before a commit, PR or merge. Discovers and runs the repository's formatters, static checks, build and tests, plus a project verification skill that drives the real app when one exists, fixes failures at the root cause within a retry limit, reviews the diff, and returns PASS, FAIL or INCONCLUSIVE with evidence. Triggers: verify-changes, /verify-changes, verify my changes, run the checks, is this ready to commit."
---

# Verify changes

Prove that the current changes work, with evidence a reviewer can rerun. "It compiles" is not evidence, and a check that did not run is not a pass.

## Inputs

- Worktree: the given path, else the current directory.
- Base: the given ref, else the merge base with the repository's default branch on `origin`.
- Task brief: an optional `task.md` (goal, acceptance criteria, artifacts directory). Without it, take the goal from the user's request.
- Previous report: an optional earlier `verify.md` for the same change. When given, rerun only the checks the changes since its `HEAD` can affect and carry the other results over, marked with the SHA they ran on.

Run nothing against production systems or live customer data.

## 1. Find the checks

Local verification gives fast feedback on the changed code. CI runs the full matrix after the PR is opened; do not repeat it locally.

Collect the local checks in this order of authority:

1. Repository instructions: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the pre-submit checklists they point to, and the directories on the path of each changed file. Checks they list for before a PR are required; conditional ones (for example "screenshot tests if UI changed") only when the condition holds.
2. Build files: package scripts, Gradle tasks, Makefile targets, Xcode schemes and similar, to find the commands and scope them to the changed modules.

When the instructions name no local checks, the default is: format, static checks of the changed modules, one build that compiles the changed code into the app, and the tests of the changed modules.

Read the CI configuration (such as `.github/workflows/`) only to learn what runs after the PR. Do not run a CI job locally because it exists in CI: release and variant builds, full test or screenshot suites, full end-to-end suites and similar matrix jobs go to "Deferred to CI" in the report. Run one locally only when the instructions require it or it is the only way to prove the changed behavior.

Group the checks as: format, static checks (lint, types), build, tests. Scope tests and screenshot checks to the changed modules when the build allows it. Note any check you cannot find a command for.

## 2. Add runtime proof for user-visible changes

Tests show branch behavior, not that the product works. When the change alters what a user sees or does, look for a project verification skill (a skill named `verify-<app>`, or one the instructions name) for that surface. Run it for the affected flows only, never the whole end-to-end suite, and keep its evidence: screenshots, recordings, logs or responses. A change with no user-visible effect (refactoring, internal wiring) needs no runtime proof; its tests and CI's end-to-end jobs cover it.

No such skill, or no environment to run it (device, simulator, credentials): record runtime behavior as unverified, with the reason. Do not substitute a guess.

## 3. Run

- Run format first. Formatters rewrite files, so review what they changed and re-stage it when the repository requires formatted commits.
- Run slow commands so they do not block you, through the background facility the environment instructions name. Wait for the result instead of polling.
- For each check, record the command, exit code and, on failure, the relevant output lines.

## 4. Fix failures

1. Find the root cause. Fix it in the task's code, then rerun the failed check and every check the fix can affect.
2. A failure in code the change does not touch may be pre-existing. Run the same check on the base. If it also fails there, report it as pre-existing with that evidence and do not fix it as part of this change.
3. Never make a check pass by skipping or deleting tests, weakening assertions, lowering thresholds, adding suppressions or disabling a check. That needs the user's explicit approval.
4. After 10 attempts on the same kind of failure, stop and return `FAIL` with the evidence.

## 5. Review the diff

1. Read `git status` and the full diff from the base, including untracked files.
2. Remove debug output, temporary files, stray artifacts and changes unrelated to the task.
3. Confirm that the change matches the goal and each acceptance criterion, that it contains no secrets or credentials, and that it overwrote no one else's work.

## 6. Report

Results apply to the final state of the tree. If you edit anything after a check, rerun the checks that edit can affect (a rename: the build and the tests of the touched modules), not the whole set.

- `PASS`: every required check ran on the final tree and passed, and the diff review found nothing left.
- `FAIL`: a required check fails after the retry limit, or the diff review found a problem you could not resolve.
- `INCONCLUSIVE`: everything that ran passed, but a required check or the runtime proof could not run. Name each one and why. Checks deferred to CI are not required locally and do not make the result `INCONCLUSIVE`.

Start the report with the `HEAD` SHA and the list of uncommitted files it covers. Then a table, `check | command | result | evidence`, followed by unverified items, pre-existing failures and "Deferred to CI" (each CI check left to the PR, one line each). When a task brief names an artifacts directory, also write the report to `verify.md` there.
