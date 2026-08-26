# Youchen AI OS Voice and 24-Hour Runtime

## 1. Product identity

- Personal operating system: **Youchen AI OS**
- Company operating workspace: **EcoFixer AI OS**
- Primary wake phrase: **Hey Youchen**

The wake phrase activates one assistant. The request content, user identity, location, and permission policy determine whether the task remains in Youchen AI OS or enters EcoFixer AI OS.

## 2. Why some assistants appear to work 24 hours

There are two different capabilities that are often confused:

1. **Always-available voice** — a local device listens only for a short wake phrase and opens a voice session when it detects that phrase.
2. **Continuous work execution** — server processes, schedules, webhooks, monitoring events, and durable queues trigger work without anyone speaking.

A language model is not normally kept in one endless conversation for 24 hours. Small local services and durable backend workers keep the system available, while an AI model is called only when reasoning or language generation is needed.

## 3. Voice activation pipeline

```text
Microphone
  -> local wake-word detector
  -> wake event: "Hey Youchen"
  -> audible / visual acknowledgement
  -> voice activity detection (VAD)
  -> record only the command window
  -> speech-to-text
  -> identity and permission check
  -> context router
       -> Youchen AI OS
       -> EcoFixer AI OS
  -> planner and approved tool execution
  -> response verification
  -> text-to-speech
  -> audit log
```

### Wake-word detector

This is a small local model that continuously processes short audio frames. It should run on the room device and should not stream ambient room audio to a cloud model.

### Voice activity detection

VAD detects when the user starts and stops speaking so the system records a bounded command rather than keeping a permanent open recording.

### Speech-to-text

Only the activated command window is transcribed. V1 currently performs transcription after push-to-talk recording. The always-on version will pass the VAD-bounded audio segment into the same transcription boundary.

### Context and permission routing

Examples:

- `Hey Youchen, remind me to call the doctor` -> Youchen AI OS
- `Hey Youchen, check EcoFixer's failed CI` -> EcoFixer AI OS
- `Hey Youchen, merge the release branch` -> EcoFixer AI OS, approval required

## 4. Recommended physical architecture

### Room node

A dedicated always-powered device is the most reliable option:

- Mac mini
- Linux mini PC
- Raspberry Pi-class device for wake word and audio capture
- Dedicated smart-speaker-style enclosure

Recommended hardware:

- microphone array or quality USB microphone
- speaker
- physical microphone mute switch
- visible listening / recording indicator
- stable wired or Wi-Fi network
- automatic restart after power loss

The room node should perform wake-word detection locally. It can send the short activated command to a private backend over an encrypted connection.

### Personal mobile and desktop clients

- macOS menu-bar app or launch agent
- iPhone app with push-to-talk, shortcuts, and notifications
- Android foreground service when continuous listening is intentionally enabled

Mobile operating systems restrict arbitrary background microphone usage. A dedicated room node or always-powered Mac is therefore more reliable than depending only on an iPhone background process.

## 5. Continuous company work pipeline

Voice is only one trigger. EcoFixer AI OS should also receive events from:

- GitHub webhooks and CI results
- calendar schedules
- email arrival events
- application monitoring alerts
- database events
- recurring schedules
- explicit tasks created by Youchen AI OS

```text
Event / schedule
  -> task intake
  -> durable queue
  -> policy and risk classification
  -> worker lease
  -> tool execution
  -> verification
  -> retry or escalation
  -> result and audit log
  -> founder notification when needed
```

A durable queue is essential. If the computer restarts or a provider times out, the task must remain recoverable rather than disappearing with an in-memory process.

## 6. Authority model for voice

Wake-word detection is not authentication. Speaker recognition is also not sufficient authorization for irreversible operations.

Suggested rules:

- Read-only briefing: may execute after wake phrase.
- Create local note or task: reversible; execute and log.
- Create draft or branch: execute only in an approved scope and log.
- Send email, merge, deploy, permission change, payment: require explicit confirmation tied to the exact action.
- Destructive production action: prohibited or require a separate secure approval channel.

High-risk confirmation should include the exact target, impact, and expiration window. A generic spoken `yes` should not approve an unrelated or stale action.

## 7. Privacy controls

Required controls for a room deployment:

- local wake-word processing
- physical mute control
- visible recording indicator
- bounded command recording
- configurable retention or immediate audio deletion after transcription
- encrypted transport
- founder-only and company memory separation
- per-tool permissions
- complete audit trail
- no hidden background recording

## 8. Deployment stages

### Stage A — current V1

- push-to-talk
- transcription after recording
- text response
- local memory, tasks, and audit
- wake-phrase-aware text routing

### Stage B — local wake-word prototype

- one Mac or Linux room node
- local `Hey Youchen` detector
- VAD-bounded audio capture
- audible acknowledgement
- existing transcription and assistant pipeline
- no high-risk tool execution

### Stage C — full duplex voice

- streaming speech-to-text
- interruption / barge-in handling
- text-to-speech
- conversation timeout and privacy indicator
- speaker profile used only as an additional signal

### Stage D — 24-hour operations

- scheduler
- webhook intake
- durable queue and workers
- retries and dead-letter handling
- notification routing
- approval center
- GitHub, calendar, email, and EcoFixer operational connectors

### Stage E — multi-room and company access

- multiple room nodes
- device identity and room policy
- employee company-only identities
- no access to Youchen AI OS private memory
- central fleet health and remote mute / revoke controls

## 9. Recommended first production setup

For the first dependable version:

1. Run the private backend and database on an always-on machine or private server.
2. Use a Mac mini or Linux mini PC as the room node.
3. Keep `Hey Youchen` wake-word detection local.
4. Route personal requests to Youchen AI OS and company requests to EcoFixer AI OS.
5. Allow only read-only and reversible voice actions initially.
6. Require the approval center for merge, deployment, email send, payment, and permission changes.
7. Add scheduled briefings and GitHub CI monitoring before attempting broad autonomous execution.

This design creates the experience of a 24-hour assistant without continuously sending room audio to a cloud language model or allowing a wake phrase to bypass security.
