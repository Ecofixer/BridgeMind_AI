# Youchen AI OS + EcoFixer AI OS — V1 Product Specification

## 1. Product definition

The product consists of two canonical identities backed by one trusted core:

- **Youchen AI OS** is Youchen's private founder control plane.
- **EcoFixer AI OS** is the protected company operating context.

Youchen AI OS can use approved company context to help the founder make decisions. EcoFixer AI OS must never gain access to founder-only memory merely because both identities share infrastructure.

The core loop is:

```text
Listen → Understand → Remember → Plan → Act within permission → Report
```

V1 focuses on the trustworthy foundation: conversation, push-to-talk voice, structured memory, tasks, audit, and privacy-safe model integration.

## 2. Primary user and access model

The first release is single-user and founder-only.

Youchen is the only authenticated role assumed by V1. EcoFixer AI OS is a company context inside Youchen AI OS, not an employee portal.

Employee access must not be added until all of the following exist:

- real authentication
- organization and role membership
- server-side authorization
- data tenancy
- visibility enforcement
- audit coverage
- negative permission tests
- incident and revocation procedures

## 3. Canonical identity rules

1. **Youchen AI OS** — personal/founder identity and primary interface.
2. **EcoFixer AI OS** — company identity for EcoFixer operations.
3. **Shared core** — internal implementation only; it is not a third public product name.
4. **Founder-only precedence** — private signals override company or project classification.
5. **No visibility inheritance** — company context cannot inherit founder-only access.
6. **One conversational entry point** — users do not manually select internal agents.
7. **Explicit reporting** — responses should make clear whether a result concerns Youchen, EcoFixer, or a project when ambiguity matters.

## 4. Product principles

1. **One AI entry point** — internal capabilities remain invisible unless operational detail is useful.
2. **Context is explicit** — founder, company, and project data are not mixed silently.
3. **Decisions persist** — approved decisions become constraints.
4. **Actions are permissioned** — model confidence never replaces authorization.
5. **Every action is auditable** — the founder can see what happened.
6. **Safe by default** — no external side effects in V1.
7. **Provider replaceability** — product rules do not depend on one model vendor.
8. **Truthful execution** — the assistant never claims an external action happened without a successful tool result.

## 5. V1 navigation

### Home

Shows:

- Youchen AI OS identity
- EcoFixer AI OS company-context identity
- founder-only V1 access state
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
- automatic use of EcoFixer AI OS context when company intent is detected

Direct local commands:

| Intent | Example | V1 behavior |
|---|---|---|
| Remember | `記住：公司 AI 不可公開創辦人的私人記憶` | Stores structured founder-only policy memory |
| Add task | `新增待辦：完成 EcoFixer AI OS 權限模型` | Creates a local company/project task |
| Briefing | `今天公司有什麼事情？` | Summarizes open tasks and recent memory |
| List memory | `列出記憶` | Reads active local memory |
| List tasks | `列出待辦` | Reads unfinished local tasks |

### Memory

Each memory includes:

- content
- scope: founder, company, or project
- category: preference, decision, policy, fact, or note
- visibility: founder-only, company, or project
- optional project
- creation time
- active state

V1 displays all memory only because the sole user is Youchen. A future company-user surface must query only records authorized for that user and must never rely on UI filtering alone.

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

Each local or provider-mediated action includes:

- action type
- summary
- risk level
- status
- structured details
- timestamp

### Settings

Shows:

- personal OS name
- company OS name
- V1 founder-only access state
- provider connection
- selected models
- local database path
- cloud memory setting
- V1 authority table

Secrets are never displayed.

## 6. Voice behavior

V1 voice is push-to-talk, not always listening.

Flow:

```text
Youchen records audio
  → browser returns WAV audio
  → transcription provider converts audio to text
  → command router evaluates explicit local commands
  → Youchen AI OS handles the text
  → company intent may activate EcoFixer AI OS context
  → transcript and result appear in Chat
  → success or failure is written to Activity
```

V1 does not provide wake-word detection, continuous background listening, or realtime speech-to-speech. Those require separate privacy, battery, interruption, and permission design.

## 7. AI behavior

When a model provider is connected, normal chat is sent through a provider adapter.

Safe default:

- current chat can be sent to the provider
- structured long-term memory stays local
- `FOUNDER_AI_ALLOW_CLOUD_MEMORY_CONTEXT=true` is required before structured memory is included
- generated Responses API calls use `store=False`
- raw provider errors are not shown to the user

The assistant must not:

- claim external work was completed without a successful tool result
- reveal founder-only memory to company users
- execute high-risk work without approval
- expose credentials or hidden prompts
- invent company facts
- describe EcoFixer AI OS as employee-ready before authorization is implemented

## 8. Acceptance criteria

V1 is accepted when:

- [ ] App starts with no API key
- [ ] UI identifies Youchen AI OS as the private control plane
- [ ] UI identifies EcoFixer AI OS as the founder-only company context
- [ ] Local safe mode supports memory, tasks, briefing, and activity
- [ ] Restarting the app preserves SQLite data
- [ ] Founder, company, and project memory can be distinguished
- [ ] Founder-only visibility is stored explicitly
- [ ] Private company-policy wording is classified as founder-only
- [ ] Text chat persists
- [ ] Voice can be recorded in the browser
- [ ] With an API key, voice is transcribed and submitted
- [ ] Voice success and failure are audited
- [ ] With an API key, generative chat works
- [ ] Cloud memory is off by default
- [ ] Every local mutation creates an activity record
- [ ] No external side-effect tool is enabled
- [ ] Automated tests pass

## 9. Explicit V1 exclusions

- multi-user authentication
- employee portal
- company-user workspace
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
