# Identity and Data Boundaries

## Canonical names

### Youchen AI OS

Youchen AI OS is the private founder control plane.

It may contain:

- personal preferences
- private notes
- founder decisions
- schedule and reminders
- cross-company priorities
- approval decisions
- founder-only memory
- company context needed for founder decision-making

Only Youchen may access this identity in V1.

### EcoFixer AI OS

EcoFixer AI OS is the company operating context for EcoFixer.

It may contain:

- EcoFixer products
- projects and milestones
- company tasks
- operating decisions
- approved company documents
- code and repository context
- customer and financial data only after the repository and runtime are private and authorized
- company tools with explicit permission contracts

EcoFixer AI OS must not receive founder-only memory.

## Shared core

Both identities use the same internal core:

```text
Conversation
Voice
Context routing
Memory
Tasks
Permissions
Providers
Actions
Audit
```

The shared core is an implementation detail, not a third product brand.

The current Python package name `founder_company_ai` may remain as an internal technical name until a later low-risk refactor. It must not appear as the main user-facing identity.

## Direction of allowed context flow

```text
Approved EcoFixer company context
              |
              v
       Youchen AI OS
```

Youchen AI OS may read approved company information because the founder operates the company.

The reverse is not automatically allowed:

```text
Founder-only memory
        X
        |
        v
  EcoFixer AI OS
```

Founder-only data requires an explicit, narrow, auditable decision before any part of it can become company-visible.

## V1 interpretation

V1 has one user: Youchen.

Therefore:

- the primary UI is Youchen AI OS
- EcoFixer AI OS appears as a protected company context
- there is no employee login
- there is no company-user role
- showing company context to Youchen does not prove company-user authorization
- all future employee surfaces require server-side access control

## Naming rules in UI and documentation

Use:

- `Youchen AI OS`
- `EcoFixer AI OS`
- `AI Core` or `shared core` for internal architecture

Do not use as product brands:

- BridgeMind
- BridgeVision
- Founder + Company AI
- Founder AI
- Company AI as a standalone final name

Generic descriptive phrases such as “founder-private context” and “company context” remain valid when describing security boundaries.

## Repository naming

Recommended shared-core repository name:

```text
youchen-ecofixer-ai-os
```

Alternative if the repository is treated primarily as Youchen's private control plane:

```text
youchen-ai-os
```

Repository naming must not change the product identities above.

Before real data is introduced, the repository must be private and protected. Because the current repository has public legacy history, a clean private repository may be safer than retaining the public history.
