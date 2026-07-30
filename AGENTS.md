# LingMoldyEnterprises Repository Workflow

The home `/home/codex/AGENTS.md` is authoritative. This file adds only LingMoldyEnterprises-specific workflow.

## Branches and pull requests

- `Development` is the integration branch and current default work branch.
- `main` is the stable release branch.
- Create short-lived branches from `Development` using `feature/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`, `chore/<name>`, or `test/<name>`.
- Create `hotfix/<name>` from `main` only for urgent production repairs.
- All changes reach `Development` and `main` through pull requests.
- Use the `codex-max-molden` bot identity for repository operations when configured.
- Add `max-molden` as pull-request reviewer and assignee.
- The user is the final approver. Do not merge or enable auto-merge without explicit user approval.

## Validation

Before opening or updating a pull request, run the repository's formatting, linting, type-checking, tests, production build, accessibility checks, and link/security checks when applicable. Validate changed behavior in a local or preview environment and add regression coverage for bug fixes.

Do not bypass failed checks, secret scanning, or dependency/security warnings without explicit user approval.

## Secrets and configuration

- Never commit secrets or production credentials.
- Keep runtime secrets in ignored local files or an approved secret manager.
- Maintain a tracked `.env.example` or equivalent template with safe names and descriptions.
- Add clear startup validation when a feature requires missing configuration.

## Dependencies and documentation

- Do not install packages automatically; report the exact command for the user to run when installation is required.
- Keep lockfiles and runtime versions consistent.
- Document setup, validation commands, architecture decisions, and deployment assumptions without duplicating the home policy.

## Deployment and cleanup

Before changing a live service, document the deployment path, preview validation, smoke checks, observability, and rollback path. Do not deploy from an unreviewed feature branch.

After a pull request is merged or closed, fetch current remote state and remove the related local feature branch when safe. Preserve `Development` and `main`.
