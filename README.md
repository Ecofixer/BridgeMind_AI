# Founder + Company AI

A private AI operating assistant built for one founder and the company around them.

The product has one entry point and two protected context domains:

- **Founder context** — personal preferences, decisions, schedule, private notes, and priorities.
- **Company context** — products, projects, tasks, operating decisions, documents, and approved tools.

It is designed to **listen, understand, remember, plan, act within permission, and report**. It is not a collection of branded sub-agents and it is not a generic chatbot.

## V1 included in this branch

- Founder + Company chat workspace
- Push-to-talk voice recording and transcription
- Local SQLite memory with scope, category, visibility, and project fields
- Local task tracking
- Activity and audit log
- Direct commands for remembering decisions and creating tasks
- Daily founder briefing
- Optional OpenAI Responses API integration
- Cloud-memory sharing disabled by default
- No automatic merge, payment, production, permission, or destructive actions

## Product model

```text
Founder
  |
  v
Founder + Company AI
  |
  +-- Conversation
  +-- Voice
  +-- Context Router
  +-- Founder Memory
  +-- Company Memory
  +-- Project Memory
  +-- Task and Action Layer
  +-- Permission Policy
  +-- Audit Log
  |
  v
Approved tools and real actions
```

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
新增待辦：完成 Founder + Company AI 權限模型
今天公司有什麼事情？
列出記憶
```

## Safety defaults

1. Runtime data is written under `.local/` and excluded from Git.
2. No secret or personal/company memory belongs in source control.
3. Founder-only memory is represented separately from company-visible memory.
4. Cloud memory context is opt-in through `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true`.
5. V1 does not execute external side effects.
6. Every local action is written to the activity log.

## Important repository action

Before adding real founder or company data:

1. Rename the repository to the final product name.
2. Make the repository private.
3. Enable branch protection and secret scanning.
4. Store API keys only in environment variables or a secret manager.
5. Review the security model in `docs/SECURITY.md`.

## Documentation

- `docs/PRODUCT_V1.md` — detailed product behavior and acceptance criteria
- `docs/ARCHITECTURE.md` — system layers and code boundaries
- `docs/SECURITY.md` — privacy, permissions, risk levels, and audit rules
- `docs/ROADMAP.md` — staged path from local assistant to company operating system

## Status

This is a **V1 foundation**, not the finished autonomous company system. It intentionally starts with local memory, safe chat, push-to-talk voice, tasks, and auditability. External tools are added only after their permission and approval contracts are defined.

Copyright © 2026 EcoFixer. All rights reserved.
