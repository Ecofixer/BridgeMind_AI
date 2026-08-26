# Youchen AI OS + EcoFixer AI OS

A private AI operating system for one founder and the company around them.

The product has **one AI core** and two protected operating spaces:

- **Youchen AI OS** — founder-private preferences, schedule, decisions, notes, priorities, and personal work.
- **EcoFixer AI OS** — company products, projects, operations, approved documents, tasks, and tools.

The intended voice wake phrase is **“Hey Youchen.”** A wake phrase starts a voice interaction; it never authorizes a high-risk action.

## What V1 can do

- text chat with local safe mode
- push-to-talk voice recording and transcription
- structured Founder, Company, and Project context
- scoped memory with category, visibility, and project fields
- task tracking and daily Founder Briefing
- action proposals with approval, rejection, and prohibited states
- complete local activity and audit records
- optional OpenAI Responses API integration
- cloud structured-memory context disabled by default
- migration of existing local message databases

V1 does **not** automatically merge code, send email, change production, alter permissions, publish content, accept contracts, or make payments.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
streamlit run app.py
```

Without `OPENAI_API_KEY`, the system runs in local safe mode. Context, memory, tasks, proposals, activity, wake acknowledgement, and briefings still work.

Try:

```text
Hey Youchen
記住：公司 AI 不可以讓員工看到我的私人長期記憶
記住：EcoFixer 的金額與抽成比例必須可以調整，UI 先保留位置
新增待辦：完成 EcoFixer iOS 權限測試
建立提案：Merge 修正完成的 PR
今天公司有什麼事情？
```

## Privacy and authority defaults

1. Founder context and Founder memory are forced to `founder_only` in the data layer.
2. Local commands are marked as not cloud-eligible.
3. Structured profile, memory, and tasks enter model context only when `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true`.
4. OpenAI requests use `store=False`.
5. Approving a proposal changes authorization state only; it does not claim external execution.
6. Prohibited actions cannot be approved.
7. Every local mutation and approval decision creates an audit record.
8. Runtime databases and audio files are excluded from Git.

## Repository hardening required

This repository is still publicly visible under its legacy repository name. Do not store real founder secrets, customer information, contracts, financial data, or production credentials until the repository is renamed, made private, and its public history is reviewed.

Changing the license for new code does not revoke rights already granted by licenses attached to historical public commits.

## Documentation

- `docs/PRODUCT_V1.md` — original V1 product definition
- `docs/ARCHITECTURE.md` — architecture and provider boundaries
- `docs/SECURITY.md` — security and permission model
- `docs/ROADMAP.md` — staged path to a company operating system
- `docs/COMPLETION_V1.md` — features added in the completion branch
- `docs/REPLACEMENT_PLAN.md` — safe separation from the previous prototype

## Validation

```bash
python -m compileall -q founder_company_ai app.py
python -m pytest
```

The completion branch currently contains 24 automated tests covering routing, voice identity, privacy invariants, migration, persistence, action approvals, prohibited operations, cloud-context selection, and Founder Briefing.

Copyright © 2026 EcoFixer. All rights reserved.
