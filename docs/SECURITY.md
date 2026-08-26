# Founder + Company AI — Security and Permissions

## 1. Non-negotiable boundary

Founder-private memory and company-visible memory are different security domains.

A future employee account must not be able to retrieve founder-only rows through:

- UI navigation
- search
- model context assembly
- exports
- logs
- analytics
- direct database access
- tool calls

V1 is founder-only. The visibility field is stored now so later multi-user work begins with an explicit data model rather than retrofitting privacy.

## 2. Authority levels

| Level | Meaning | Examples |
|---|---|---|
| 0 — Read only | No state change | read memory, inspect repository |
| 1 — Draft | Creates an unsubmitted artifact | draft email, draft plan |
| 2 — Reversible | Safe mutation with audit | create task, create branch |
| 3 — Approval required | Material external action | send email, merge, production change, payment |
| 4 — Prohibited | Never execute | unauthorized payment, destructive production deletion |

V1 implements Levels 0 and 2 locally. It does not expose external tools.

## 3. Approval rules

Approval must be:

- explicit
- action-specific
- recent
- tied to exact arguments
- invalidated when material arguments change
- written to the audit log

A generic statement such as “handle everything” must not authorize payments, production deletion, permission escalation, legal acceptance, or public publishing.

## 4. Data handling

### Source control

Never commit:

- API keys
- database files
- audio recordings
- conversation exports
- founder notes
- customer information
- contracts
- financial records
- production credentials

### Local runtime

V1 stores runtime data under `.local/`.

Before deployment:

- encrypt storage at rest
- establish backups
- define retention
- add authenticated access
- add per-user authorization tests
- centralize secrets
- remove technical error details from end-user responses

### Cloud model context

Cloud memory context is off by default.

Before enabling it, define:

- which scopes can be sent
- which categories are prohibited
- redaction rules
- provider retention settings
- audit of context selection
- user consent and company policy

## 5. Voice privacy

V1 sends recorded audio for transcription only when the founder presses the submit button.

Always-on listening is prohibited until the product has:

- visible listening state
- hardware/OS permission handling
- local stop control
- interruption behavior
- retention policy
- accidental-capture protection
- battery and network limits
- clear workplace consent rules

## 6. Repository hardening checklist

- [ ] Rename repository to the final product name
- [ ] Make repository private
- [ ] Remove public deployment links
- [ ] Enable secret scanning
- [ ] Enable protected branches
- [ ] Require pull-request review
- [ ] Add dependency update automation
- [ ] Add CI tests
- [ ] Add static analysis
- [ ] Add an incident response contact
- [ ] Verify no historical secrets exist
