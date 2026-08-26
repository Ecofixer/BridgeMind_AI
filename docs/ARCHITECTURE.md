# Founder + Company AI — Architecture

## 1. Layered system

```text
Experience Layer
  Chat · Voice · Home · Memory · Tasks · Activity · Settings
                  |
                  v
Conversation and Context Layer
  conversation history · founder/company/project routing
                  |
                  v
Reasoning Layer
  local deterministic command router · optional model provider
                  |
                  v
Memory and Work Layer
  SQLite memories · tasks · decisions · policies · audit activity
                  |
                  v
Action and Permission Layer
  local actions now · external tool contracts later
                  |
                  v
External Systems
  GitHub · email · calendar · files · databases · internal APIs
```

## 2. Current code boundaries

| Module | Responsibility |
|---|---|
| `app.py` | Streamlit presentation and interaction |
| `config.py` | environment configuration and safe defaults |
| `models.py` | typed domain models and enums |
| `storage.py` | SQLite schema and persistence |
| `router.py` | explicit deterministic command routing |
| `assistant.py` | orchestration and context policy |
| `services/actions.py` | allowed local mutations and reporting |
| `providers/` | replaceable model and transcription adapters |

The UI does not write SQL directly. Provider-specific code does not own product permissions.

## 3. Context domains

### Founder

Examples:

- private preferences
- personal work style
- founder-only decisions
- private notes
- personal priorities

Default visibility: `founder_only`.

### Company

Examples:

- company policies
- product strategy
- operational priorities
- approved shared decisions

Default visibility: `company`.

### Project

Examples:

- EcoFixer architecture decisions
- project constraints
- release blockers
- project-specific tasks

Default visibility: `project`.

## 4. Memory design

SQLite is the V1 system of record.

This is intentionally not a vector database. Structured memory must first establish:

- ownership
- scope
- category
- visibility
- project
- active status
- time

Semantic retrieval can be added later, but it must filter by authorization before similarity ranking.

## 5. Model-provider boundary

The provider receives:

- identity and behavior instructions
- recent conversation
- optionally approved long-term context

The provider does not receive:

- database access
- authority to mutate external systems
- credentials
- hidden approval overrides

Later tool calling must return structured action proposals to the permission layer. The model must never directly decide whether an action is authorized.

## 6. External action contract

Every future external action should have:

```text
ActionRequest
  id
  actor
  tool
  operation
  arguments
  risk_level
  reversible
  approval_required
  approval_state
  idempotency_key
  created_at
```

Execution flow:

```text
Model proposes
  → policy validates
  → founder approves when required
  → connector executes
  → result is verified
  → audit record is written
  → assistant reports
```

## 7. Deployment evolution

### V1

- local single-user Streamlit
- local SQLite
- optional cloud model
- push-to-talk transcription

### V2

- authenticated private web deployment
- encrypted managed database
- company knowledge ingestion
- read-only tools
- approval inbox

### V3

- reversible write tools
- role-based company access
- scheduled workflows
- notification channels

### V4

- native mobile/desktop clients
- realtime voice
- policy-governed multi-agent execution
- organization-wide operating layer
