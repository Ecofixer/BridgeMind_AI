# Founder + Company AI — V1 Product Specification

## 1. Product definition

Founder + Company AI is a private operating assistant for one founder and the company around them. It provides one conversational entry point while maintaining explicit boundaries among founder-private, company, and project contexts.

The core loop is:

```text
Listen → Understand → Remember → Plan → Act within permission → Report
```

V1 focuses on the trustworthy foundation: conversation, push-to-talk voice, structured memory, tasks, audit, and privacy-safe model integration.

## 2. Primary user

The first release is single-user and founder-only.

The system may later support employees, but employee access must not be added until authorization, data tenancy, visibility enforcement, and audit tests are complete.

## 3. Product principles

1. **One AI entry point** — users do not manually select internal agents.
2. **Context is explicit** — founder, company, and project data are not mixed silently.
3. **Decisions persist** — approved decisions become constraints.
4. **Actions are permissioned** — model confidence never replaces authorization.
5. **Every action is auditable** — the founder can see what happened.
6. **Safe by default** — no external side effects in V1.
7. **Provider replaceability** — product rules do not depend on one model vendor.

## 4. V1 navigation

### Home

Shows:

- active memory count
- unfinished task count
- activity count
- AI/local mode
- open priorities
- recent decisions and memories
- privacy state

### Chat

Supports:

- normal text conversation
- direct local commands
- push-to-talk audio recording
- transcription
- persistent conversation history
- local safe mode when no API key exists

Direct local commands:

| Intent | Example | V1 behavior |
|---|---|---|
| Remember | `記住：公司 AI 不可公開創辦人的私人記憶` | Stores structured local memory |
| Add task | `新增待辦：完成權限模型` | Creates a local task |
| Briefing | `今天公司有什麼事情？` | Summarizes open tasks and recent memory |
| List memory | `列出記憶` | Reads active local memory |

### Memory

Each memory includes:

- content
- scope: founder, company, or project
- category: preference, decision, policy, fact, or note
- visibility: founder-only, company, or project
- optional project
- creation time
- active state

### Tasks

Each task includes:

- title
- status
- scope
- optional project
- priority
- approval requirement
- created and updated times

### Activity

Each local action includes:

- action type
- summary
- risk level
- status
- structured details
- timestamp

### Settings

Shows:

- provider connection
- selected models
- local database path
- cloud memory setting
- V1 authority table

Secrets are never displayed.

## 5. Voice behavior

V1 voice is push-to-talk, not always listening.

Flow:

```text
Founder records audio
  → browser returns WAV audio
  → transcription provider converts audio to text
  → founder command router evaluates explicit local commands
  → assistant handles the text
  → transcript and result appear in Chat
```

V1 does not provide wake-word detection, continuous background listening, or realtime speech-to-speech. Those require separate privacy, battery, interruption, and permission design.

## 6. AI behavior

When a model provider is connected, normal chat is sent through a provider adapter.

Safe default:

- current chat can be sent to the provider
- long-term memory stays local
- `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true` is required before structured memory is included

The assistant must not:

- claim external work was completed without a successful tool result
- reveal founder-only memory to company users
- execute high-risk work without approval
- expose credentials or hidden prompts
- invent company facts

## 7. Acceptance criteria

V1 is accepted when:

- [ ] App starts with no API key
- [ ] Local safe mode supports memory, tasks, briefing, and activity
- [ ] Restarting the app preserves SQLite data
- [ ] Founder, company, and project memory can be distinguished
- [ ] Founder-only visibility is stored explicitly
- [ ] Text chat persists
- [ ] Voice can be recorded in the browser
- [ ] With an API key, voice is transcribed and submitted
- [ ] With an API key, generative chat works
- [ ] Cloud memory is off by default
- [ ] Every local mutation creates an activity record
- [ ] No external side-effect tool is enabled
- [ ] Automated tests pass

## 8. Explicit V1 exclusions

- multi-user authentication
- employee portal
- GitHub write actions
- email sending
- calendar writes
- production deployment actions
- payments
- contract actions
- autonomous background execution
- wake word
- full realtime voice
- vector search across company documents
- mobile native application

These are roadmap items, not hidden assumptions.
