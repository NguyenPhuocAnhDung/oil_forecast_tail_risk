# BRIEFING — 2026-07-17T23:09:20+07:00

## Mission
Coordinate the upgrade of the GUM-Net Research OS with 32 models, including config.py, reports, model files, and validation scripts.

## 🔒 My Identity
- Archetype: teamwork_preview_orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models
- Original parent: parent
- Original parent conversation ID: d5f5707c-d383-4212-a14c-d6c762312691

## 🔒 My Workflow
- **Pattern**: Project
- **Scope document**: /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/PROJECT.md
1. **Decompose**: We break down the task into milestones:
   - Milestone 1: Update config.py at project root.
   - Milestone 2: Implement src/models/extended_sota.py.
   - Milestone 3: Implement src/models/gumnet_family.py.
   - Milestone 4: Update get_model_instance in scripts/train_unified.py.
   - Milestone 5: Update docs/research_os/ reports (Stage 2, 5, 7, 9, 10).
   - Milestone 6: Create experimental scripts in scripts/ (run_all_32models.py, compile_32model_results.py, dm_test_32models.py, effect_size_32models.py).
   - Milestone 7: Create table/plot generation pipeline (generate_all_outputs.py) and output validation.
   - Milestone 8: Create environment files (requirements_32models.txt, scripts/check_environment.py).
2. **Dispatch & Execute**:
   - **Direct (iteration loop)**: For each milestone, spawn Explorer(s) to analyze and draft changes, Worker to implement, Reviewer(s) to review, Challenger(s) to verify, and Auditor to audit.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: Self-succeed at 16 spawns, write handoff.md, spawn successor.
- **Work items**:
  1. Milestone 1: config.py [pending]
  2. Milestone 2: src/models/extended_sota.py [pending]
  3. Milestone 3: src/models/gumnet_family.py [pending]
  4. Milestone 4: scripts/train_unified.py [pending]
  5. Milestone 5: docs/research_os/ reports [pending]
  6. Milestone 6: scripts/ experimental scripts [pending]
  7. Milestone 7: scripts/generate_all_outputs.py & output validation [pending]
  8. Milestone 8: requirements & check_environment.py [pending]
- **Current phase**: 1
- **Current focus**: Milestone 1: config.py

## 🔒 Key Constraints
- Pure Orchestrator: Do NOT write code/docs directly. Dispatch to subagents.
- Write coordination files ONLY under /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/.
- Academic integrity: No hardcoded statistical values in Stage 9 report, Stage 7 has R8 verbatim.
- Self-succeed at 16 spawns.

## Current Parent
- Conversation ID: d5f5707c-d383-4212-a14c-d6c762312691
- Updated: not yet

## Key Decisions Made
- Organized the tasks into 8 milestones.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| explorer_1 | teamwork_preview_explorer | Analyze config.py, reqs, check_env | completed | e7ddf23b-a7bb-47b4-acaf-c2ea678ccee3 |
| explorer_2 | teamwork_preview_explorer | Analyze models, 20 SOTAs, 10 variants | completed | c4830d4a-3cf3-4f4c-a7d8-382d913ed062 |
| explorer_3 | teamwork_preview_explorer | Analyze train_unified.py get_model_instance | completed | fc40bbe1-5fd8-46b2-8794-ca2a28568d15 |
| worker_1 | teamwork_preview_worker | Implement Milestone A Code & Config | completed | 4d0901d1-bebb-48d7-b89a-4a0adf324f13 |
| sub_orch_msB | self | Coordinate Milestone B Scripts & Pipeline | completed | 9a5de971-c13e-48d8-ab17-8a0d02ea22af |
| sub_orch_msC | self | Coordinate Milestone C Reports & Docs | completed | d4d84ace-29f5-4b18-bce2-c92ab2ee837e |
| worker_fixes | teamwork_preview_worker | Implement Victory Audit Bug Fixes | completed | ba8e3393-bac5-42bd-b1bc-fab9c7b9e67b |

## Succession Status
- Succession required: no
- Spawn count: 7 / 16
- Pending subagents: none
- Predecessor: none
- Successor: not yet spawned

## Active Timers
- Heartbeat cron: none
- Safety timer: none

## Artifact Index
- /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/PROJECT.md — Global project plan and milestones
- /data/quyhv/oil_forecast_tail_risk/.agents/orchestrator_32models/progress.md — Liveness and status heartbeat
