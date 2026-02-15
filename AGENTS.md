# Workflow Rules (max-molden)

1. Use `Development` as the default base branch for new work.
2. Always push feature branches and open PRs against `Development` by default.
3. Before starting new work, check whether the prior PR is still open.
4. If the prior PR is closed/merged, confirm with the user before creating a new branch.
5. If a non-`Development` base seems better, explain why and confirm with the user before branching.
6. Create commits, pushes, and PRs using the bot identity (`codex-max-molden`) for this repo.
7. When creating PRs, always add `max-molden` as reviewer and assignee.
8. After PR merge/close, ensure feature branches are cleaned up (remote auto-delete plus local cleanup).
9. Do not install packages; tell the user exactly what to install instead.
10. When switching back to `Development` (or finishing/closing a feature branch), always fetch and fast-forward/pull `Development` so future branches start from the latest base.
11. After creating a PR, always enable auto-merge on that PR (use `gh pr merge --auto` with the standard merge method for this repo).
12. Never merge work directly into local `Development`; all merges to `Development` must go through a PR.
13. `max-molden` is the sole approver for this repo and the only person who can approve changes that land on `Development`.
14. Configure each PR so it completes automatically after required checks and approval, with remote branch auto-deletion enabled.
15. At the start of the next work session, if a local feature branch is already merged/closed ("dead"), delete the local branch during cleanup.
