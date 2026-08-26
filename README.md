# Youchen AI OS + EcoFixer AI OS

A private AI operating system built for Youchen and the company he operates.

> **Security status:** the GitHub repository is still public and still uses its legacy repository name. Do not add real founder, company, customer, financial, contract, or credential data until the repository is renamed, made private, and protected.

## Canonical product names

- **Youchen AI OS** — Youchen's private founder control plane. It can hold founder-only preferences, decisions, schedule, private notes, priorities, and approvals.
- **EcoFixer AI OS** — the protected company operating context for EcoFixer products, projects, tasks, documents, operations, and approved tools.

They share one trusted core, but they do **not** share visibility automatically. Founder-only data must never become company-visible data.

V1 is single-user and founder-only. `EcoFixer AI OS` is currently a company context inside Youchen's private control plane, not an employee portal.

## V1 included in this branch

- Youchen AI OS chat workspace
- EcoFixer AI OS company context
- Push-to-talk voice recording and transcription
- Local SQLite memory with scope, category, visibility, and project fields
- Local task tracking
- Activity and audit log
- Direct commands for remembering decisions and creating or listing tasks
- Daily founder briefing
- Optional OpenAI Responses API integration
- Cloud-memory sharing disabled by default
- API response storage disabled for generated chat requests
- No automatic merge, payment, production, permission, or destructive actions

## Product model

```text
Youchen
  |
  v
Youchen AI OS
  |  private founder control plane
  |
  +-- Conversation
  +-- Voice
  +-- Founder Memory
  +-- Personal Tasks and Decisions
  +-- Approval Center (roadmap)
  |
  +--> EcoFixer AI OS
       |  company operating context
       |
       +-- Company Memory
       +-- Projects
       +-- Tasks
       +-- Documents
       +-- Approved Tools
       +-- Audit Log
```

## Core loop

```text
Listen → Understand → Remember → Plan → Act within permission → Report
```

The product is not a collection of branded sub-agents and it is not a generic chatbot. Internal capabilities remain behind one assistant experience.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
streamlit run app.py
```

Without `OPENAI_API_KEY`, the app runs in local safe mode. Memory, tasks, activity, and direct commands still work. Generative chat and speech transcription require the API key.

Useful direct commands:

```text
記住：公司 AI 不可以讓其他員工看到創辦人的私人記憶
新增待辦：完成 EcoFixer AI OS 權限模型
今天公司有什麼事情？
列出記憶
列出待辦
```

## Safety defaults

1. Runtime data is written under `.local/` and excluded from Git.
2. No secret or personal/company memory belongs in source control.
3. Founder-only memory is represented separately from company-visible memory.
4. EcoFixer AI OS cannot inherit founder-only visibility.
5. Cloud memory context is opt-in through `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true`.
6. Generated Responses API requests explicitly set `store=False`.
7. V1 does not execute external side effects.
8. Every local action, voice outcome, and cloud-chat outcome is written to the activity log.

## Important repository action

Before adding real founder or company data:

1. Choose the final combined repository name.
2. Make the repository private.
3. Enable branch protection and secret scanning.
4. Store API keys only in environment variables or a secret manager.
5. Review the security model in `docs/SECURITY.md`.
6. Decide whether the legacy public Git history should be retained, rewritten, or replaced by a clean private repository.

Recommended repository name for the shared core:

```text
youchen-ecofixer-ai-os
```

This is an internal repository name, not a third product brand.

## Documentation

- `docs/IDENTITY_AND_BOUNDARIES.md` — canonical product names and data boundaries
- `docs/PRODUCT_V1.md` — detailed product behavior and acceptance criteria
- `docs/ARCHITECTURE.md` — system layers and code boundaries
- `docs/SECURITY.md` — privacy, permissions, risk levels, and audit rules
- `docs/ROADMAP.md` — staged path from local assistant to company operating system

## Status

This is a **V1 foundation**, not the finished autonomous company system. It intentionally starts with local memory, safe chat, push-to-talk voice, tasks, and auditability. External tools are added only after their permission and approval contracts are defined.

Copyright © 2026 EcoFixer. All rights reserved.
