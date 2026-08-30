# BRIEFING — 2026-07-17T20:39:00+07:00

## Mission
Coordinate and implement the 17 stages (Stage 0 to Stage 16) of the Research OS for GUM-Net under geopolitical tail risk. All report files must be generated in `docs/research_os/` as separate Markdown files.

## 🔒 My Identity
- Archetype: Project Orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator
- Original parent: parent
- Original parent conversation ID: 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b

## 🔒 My Workflow
- **Pattern**: Project Pattern
- **Scope document**: /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/PROJECT.md
1. **Decompose**: We decompose the 17 stages into 6 milestones:
   - Milestone 1: Exploration and scanning of the codebase, draft papers, and data folder.
   - Milestone 2: Phase A implementation (Stages 0, 1, 2, 2.5).
   - Milestone 3: Phase B implementation (Stages 3, 4, 5, 6, 7).
   - Milestone 4: Phase C implementation (Stages 8, 9, 10, 11).
   - Milestone 5: Phase D implementation (Stages 12, 13, 14, 15, 16).
   - Milestone 6: Validation, review, and forensic audit.
2. **Dispatch & Execute**:
   - Delegate (sub-orchestrator / workers): We will spawn workers for exploration, implementation of Phase A, B, C, D in separate runs to stay within the spawn count threshold of 16.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: Self-succeed when cumulative sub-agent spawn count >= 16 and all subagents are complete.
- **Work items**:
  1. Milestone 1: Exploration [done]
  2. Milestone 2: Phase A (Stages 0-2.5) [done]
  3. Milestone 3: Phase B (Stages 3-7) [done]
  4. Milestone 4: Phase C (Stages 8-11) [done]
  5. Milestone 5: Phase D (Stages 12-16) [done]
  6. Milestone 6: Validation and Audit [done]
- **Current phase**: 6
- **Current focus**: Project Complete

## 🔒 Key Constraints
- NEVER write, modify, or create source code files directly.
- NEVER run build/test commands yourself — require workers to do so.
- We MAY use file-editing tools ONLY for metadata/state files (.md) in our .agents/ folder.
- All report files must be generated in `docs/research_os/` as separate Markdown files.
- Never reuse a subagent after it has delivered its handoff — always spawn fresh.

## Current Parent
- Conversation ID: 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b
- Updated: not yet

## Key Decisions Made
- Decomposed the 17 stages into Phase A, B, C, D to be executed by separate subagent Worker runs to avoid exceeding the spawn threshold of 16.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| Explorer 1 | teamwork_preview_explorer | Scan workspace & data | failed | ba4d3f55-8888-4861-ab0f-5f307fe7b8b0 |
| Explorer 1 Gen 2 | teamwork_preview_explorer | Scan workspace & data | completed | e34bd18e-6597-44af-afc7-7267b2d4fae3 |
| Worker Phase A | teamwork_preview_worker | Implement Phase A (Stages 0-2.5) | completed | 24131180-ee2f-4147-925e-ddef75c1b193 |
| Worker Phase B | teamwork_preview_worker | Implement Phase B (Stages 3-7) | completed | 3f822750-49e9-4592-82b6-fa2937d4d4d0 |
| Worker Phase C | teamwork_preview_worker | Implement Phase C (Stages 8-11) | completed | 10d50f01-3893-4fe0-8ad5-200bef780a1e |
| Worker Phase D | teamwork_preview_worker | Implement Phase D (Stages 12-16) | completed | f8f91593-7858-431c-b8ac-eae45f8db3cc |
| Auditor 1 | teamwork_preview_auditor | Forensic Integrity Audit | completed | 85df168a-87a0-4113-921a-659eec17b537 |

## Succession Status
- Succession required: no
- Spawn count: 7 / 16
- Pending subagents: none
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: 502c963a-0625-43e8-8805-88b44ce179dc/task-30
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run `manage_task(Action="list")` — re-create if missing

## Artifact Index
- /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/PROJECT.md — Global index and milestone tracking
- /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/progress.md — Liveness and status heartbeat
- /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator/plan.md — Project execution plan
