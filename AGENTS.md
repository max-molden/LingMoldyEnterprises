# Workflow Rules (max-molden)

1. Use `Development` as the default base branch for new work.
2. Before starting new work, check whether the prior PR is still open.
3. If the prior PR is closed/merged, confirm with the user before creating a new branch.
4. If a non-`Development` base seems better, explain why and confirm with the user before branching.
5. Create commits, pushes, and PRs using the bot identity (`codex-max-molden`) for this repo.
6. When creating PRs, always add `max-molden` as reviewer and assignee.
7. After PR merge/close, ensure feature branches are cleaned up (remote auto-delete plus local cleanup).
8. Do not install packages; tell the user exactly what to install instead.
9. When switching back to `Development` (or finishing/closing a feature branch), always fetch and fast-forward/pull `Development` so future branches start from the latest base.
10. After creating a PR, always enable auto-merge on that PR (use `gh pr merge --auto` with the standard merge method for this repo).
