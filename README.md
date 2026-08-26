# Youchen AI OS + EcoFixer AI OS

A private AI operating system with one shared core and two protected workspaces:

- **Youchen AI OS** — the founder-private assistant and primary interface.
- **EcoFixer AI OS** — the company operating workspace for products, projects, operations, documents, and approved tools.

The intended wake phrase is **`Hey Youchen`**. The same assistant wakes once, then routes the request into the private or company workspace based on meaning and permission.

> **Security status:** this GitHub repository is still public and still uses its legacy repository name. Do not add real founder, company, customer, financial, voice, or credential data until the repository is renamed, made private, and protected.

## Identity model

```text
Youchen
  |
  |  "Hey Youchen"
  v
Youchen AI OS
  |
  +-- Founder-private memory
  +-- Personal tasks, decisions, schedule, and preferences
  |
  +-- protected workspace switch --> EcoFixer AI OS
                                      +-- Company memory
                                      +-- Products and projects
                                      +-- Operations and approved tools
                                      +-- Company activity and audit
```

There is one reasoning and action core, but the two data spaces are never treated as interchangeable. Founder-only memory must not be exposed to company users.

## V1 included in this branch

- Youchen AI OS chat workspace
- EcoFixer AI OS company context routing
- Push-to-talk voice recording and transcription
- Wake-phrase-aware command routing for `Hey Youchen` and supported aliases
- Local SQLite memory with scope, category, visibility, and project fields
- Local task tracking
- Activity and audit log
- Direct commands for remembering decisions and creating or listing tasks
- Daily founder briefing
- Optional OpenAI Responses API integration
- Cloud-memory sharing disabled by default
- API response storage disabled for generated chat requests
- No automatic merge, payment, production, permission, or destructive actions

## How 24-hour voice operation works

A true always-available assistant is not one model continuously listening in the cloud. It is a layered runtime:

```text
Room microphone / device
  -> local low-power wake-word detector
  -> "Hey Youchen" detected
  -> voice activity detection records only the request
  -> speech-to-text
  -> Youchen AI OS context and permission router
  -> EcoFixer AI OS when company context is selected
  -> approved tools / task queue
  -> text-to-speech response
```

Separately, 24-hour work is handled by schedulers, event listeners, and durable job workers. GitHub events, calendar reminders, email arrivals, monitoring alerts, and scheduled briefings can trigger tasks even when nobody speaks.

V1 currently provides **push-to-talk**, not background microphone monitoring. The always-on room node, local wake-word engine, voice activity detection, text-to-speech, scheduler, and durable worker are staged in `docs/VOICE_RUNTIME.md`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
streamlit run app.py
```

Without `OPENAI_API_KEY`, the app runs in local safe mode. Memory, tasks, activity, wake-phrase routing, and direct commands still work. Generative chat and speech transcription require the API key.

Useful commands:

```text
Hey Youchen
Hey Youchen，今天公司有什麼事情？
記住：EcoFixer AI OS 不可以讓其他員工看到創辦人的私人記憶
新增待辦：完成 EcoFixer AI OS 權限模型
列出記憶
列出待辦
```

## Safety defaults

1. Runtime data is written under `.local/` and excluded from Git.
2. No secret or personal/company memory belongs in source control.
3. Founder-only memory is represented separately from company-visible memory.
4. Cloud memory context is opt-in through `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true`.
5. Generated Responses API requests explicitly set `store=False`.
6. A wake phrase, voice match, or speaker-recognition result is never sufficient approval for a high-risk action.
7. V1 does not execute external side effects.
8. Every local action and cloud-chat outcome is written to the activity log.

## Important repository actions

Before adding real founder or company data:

1. Rename the repository to `EcoFixer_AI_OS` or another final GitHub-safe form.
2. Make the repository private.
3. Enable branch protection and secret scanning.
4. Store API keys only in environment variables or a secret manager.
5. Review the security model in `docs/SECURITY.md`.

## Documentation

- `docs/PRODUCT_V1.md` — detailed product behavior and acceptance criteria
- `docs/ARCHITECTURE.md` — system layers and code boundaries
- `docs/SECURITY.md` — privacy, permissions, risk levels, and audit rules
- `docs/VOICE_RUNTIME.md` — wake word, room device, 24-hour workers, and deployment stages
- `docs/ROADMAP.md` — staged path from local assistant to company operating system

## Status

This is a **V1 foundation**, not the finished autonomous company system. It intentionally starts with local memory, safe chat, push-to-talk voice, tasks, and auditability. External tools and continuous voice are added only after their permission, privacy, and approval contracts are defined.

Copyright © 2026 EcoFixer. All rights reserved.
