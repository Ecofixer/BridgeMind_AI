# V1 Completion — Youchen AI OS and EcoFixer AI OS

## Goal

Complete the trustworthy foundation of the founder and company assistant without overwriting the identity decisions already made for Youchen AI OS, EcoFixer AI OS, and the “Hey Youchen” voice phrase.

## Added in this branch

### Structured operating context

The system can store stable context separately from conversational memory:

- Founder profile and working style
- Company identity and operating rules
- Project-specific baselines

Founder-domain context is forced to `founder_only` in the data layer.

### Approval inbox

The system can create exact action proposals and classify them as:

- draft
- reversible
- approval required
- prohibited

Approval changes the proposal status only. External execution requires a future connector, verification result, idempotency key, and audit record.

### Conversation privacy

Local commands such as `記住：...`, `新增待辦：...`, and `建立提案：...` are not cloud-eligible. When cloud memory context is disabled, they are excluded from later model conversation history.

### Database migration

Existing SQLite message tables are upgraded in place with a `cloud_allowed` field. Context and action-request tables are created without deleting current local tasks, memories, messages, or audit records.

### UI completion

Navigation now includes:

- Home
- Chat and push-to-talk voice
- Founder & Company context
- Memory
- Tasks
- Approvals
- Activity
- Settings

### Automated validation

The test suite covers:

- wake phrase handling
- branded operating spaces
- private-memory routing
- Founder visibility invariants
- project routing
- action risk classification
- proposal approval and prohibited actions
- legacy database migration
- cloud-history filtering
- opt-in cloud context
- task and briefing behavior

## Explicit exclusions

V1 still excludes automatic email sending, Git merge, production changes, payments, permission changes, contract acceptance, always-on wake listening, employee accounts, and autonomous background work.
