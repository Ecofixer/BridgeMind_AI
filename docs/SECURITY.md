# Security and Permission Model

## Non-negotiable boundary

Youchen AI OS private data and EcoFixer AI OS company-visible data are separate security domains. A future employee account must not retrieve Founder-only records through UI navigation, search, model context, exports, logs, analytics, database access, or tool calls.

V1 enforces two data-layer invariants:

- Founder profile context must be `founder_only`.
- Founder-scoped memory must be `founder_only`.

## Authority levels

| Level | Meaning | Examples |
|---|---|---|
| Read only | No state change | inspect memory, repository, or schedule |
| Draft | Creates an unsubmitted artifact | draft email or plan |
| Reversible | Audited recoverable mutation | create task or branch |
| Approval required | Material external action | send email, merge, production change, payment |
| Prohibited | Never execute | unauthorized payment or destructive production deletion |

## Approval requirements

Approval must be explicit, action-specific, recent, tied to exact arguments, invalidated when material arguments change, and recorded in the audit log.

A broad instruction such as “handle everything” never authorizes payments, legal acceptance, permission escalation, production deletion, or public publishing.

In V1, approval changes only proposal state. It does not execute an external operation.

## Cloud context

Structured profile, memory, and tasks remain local by default. Local commands and their responses are marked as not cloud-eligible. Enabling `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true` is an explicit opt-in.

The OpenAI provider uses `store=False`, but the company must still review provider settings, retention, redaction, and data-processing obligations before confidential deployment.

## Voice privacy

Audio is submitted for transcription only after the founder presses the execution button. The “Hey Youchen” phrase is an intended future local wake phrase, not proof of identity and not approval.

Always-on listening remains prohibited until the product has visible listening state, consent rules, stop control, accidental-capture protection, retention policy, and battery/network limits.

## Public history warning

The repository is currently public. New proprietary licensing does not revoke rights already granted under historical public licenses. Do not add confidential data until the repository is private and its history has been reviewed.
