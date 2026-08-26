# Repository Hardening Plan

Target repository:

```text
Ecofixer/youchen-ecofixer-ai-os
```

Target visibility: **Private**

## Required order

1. Rename the repository.
2. Change visibility to private.
3. Confirm all local clones use the redirected or updated remote URL.
4. Enable secret scanning and push protection.
5. Configure Actions and environment secrets.
6. Add a branch ruleset for `main`.
7. Merge the clean V1 PR only after the new security settings are verified.

## Repository ruleset for `main`

Recommended rules:

- target branch pattern: `main`
- block branch deletion
- block force pushes
- require a pull request before merging
- required approvals: `0` during solo-founder development; change to `1` when a second trusted reviewer exists
- dismiss stale approvals when new commits are pushed
- require all review conversations to be resolved
- require status check: `test`
- require status check: `security`
- require branches to be up to date before merging
- allow bypass only for the repository owner, for emergency recovery
- do not allow direct pushes during normal development

## Secrets management

Repository or organization secrets:

- `OPENAI_API_KEY`

Use variables, not secrets, for non-sensitive configuration:

- `OPENAI_MODEL`
- `OPENAI_TRANSCRIBE_MODEL`

Future credentials must be separated by environment and provider. Never reuse production secrets in development.

Recommended GitHub environments:

- `development`
- `staging`
- `production`

`production` must require explicit approval before deployment. Do not place founder-private credentials in company-visible environments.

## Secret scanning

Enable:

- Secret scanning
- Push protection
- Validity checks, when available
- Non-provider pattern detection, when available

The repository also includes a local tracked-file scanner as defense in depth. It does not replace GitHub secret scanning.

## Additional controls

- Dependabot alerts
- Dependabot security updates
- Private vulnerability reporting, if the repository will accept outside reports
- CODEOWNERS
- Weekly dependency update checks
- Monthly GitHub Actions update checks
- Least-privilege workflow permissions
- No long-lived credentials in repository files or Actions logs

## Public-history warning

Changing a public repository to private does not make previously public commits, downloaded files, clones, caches, or forks cease to have existed. Before storing real founder or company data, choose one of these paths:

1. Keep the old repository as a sanitized legacy archive and create a new private repository from the clean V1 tree; or
2. Rename and privatize this repository, then perform a separately reviewed history migration.

The safer recommendation is a new clean private repository if the old public history contained material that should not remain associated with the new system.
