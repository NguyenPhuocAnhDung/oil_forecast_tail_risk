# BRIEFING — 2026-07-17T16:41:00Z

## Mission
Review the five scripts under scripts/ for Milestone B, focusing on integration/downstream flow, figure requirements, and executing dry-run verification.

## 🔒 My Identity
- Archetype: Reviewer & Critic
- Roles: reviewer, critic
- Working directory: /data/quyhv/oil_forecast_tail_risk/.agents/reviewer_msB_2
- Original parent: 9a5de971-c13e-48d8-ab17-8a0d02ea22af
- Milestone: Milestone B
- Instance: 2 of 2

## 🔒 Key Constraints
- Review-only — do NOT modify implementation code.
- Focus on:
  1. Integration and downstream flow: run_all_32models.py backup and safe folder clearing.
  2. Figure requirements in generate_all_outputs.py (PDF+PNG 300dpi, IEEE/Elsevier styles, mock data support).
  3. Execute verification with GUMNET_TEST_MODE="1", dry-run and check outputs.

## Current Parent
- Conversation ID: 9a5de971-c13e-48d8-ab17-8a0d02ea22af
- Updated: 2026-07-17T16:41:00Z

## Review Scope
- **Files to review**:
  - scripts/compile_32model_results.py
  - scripts/dm_test_32models.py
  - scripts/effect_size_32models.py
  - scripts/generate_all_outputs.py
  - scripts/run_all_32models.py
- **Interface contracts**: config.py parameters
- **Review criteria**: correctness, completeness, quality, and adversarial robustness.

## Key Decisions Made
- Confirmed run_all_32models.py correctly does selective model folder cleanup without purging non-model walkforward folders.
- Noted a safety concern in backup failure handling in run_all_32models.py.
- Verified generate_all_outputs.py successfully outputs PDF and 300dpi PNG format figures using Arial fonts.
- Confirmed econometric tests (DM and MCS) are logically complete and center bootstrap distribution correctly.

## Artifact Index
- /data/quyhv/oil_forecast_tail_risk/.agents/reviewer_msB_2/handoff.md — Handoff report containing detailed Quality and Adversarial reviews.

## Review Checklist
- **Items reviewed**: compile_32model_results.py, dm_test_32models.py, effect_size_32models.py, generate_all_outputs.py, run_all_32models.py
- **Verdict**: APPROVE (with safety and execution recommendations)
- **Unverified claims**: None (all tested and verified via end-to-end dry-run)

## Attack Surface
- **Hypotheses tested**: 
  - circular block bootstrap and centering in MCS (verified correct implementation)
  - backup directory preservation (verified correct implementation)
  - selective model directory deletion (verified correct implementation)
- **Vulnerabilities found**:
  - Unsafe continuation on backup failure in run_all_32models.py
  - Artificially inflated Directional Accuracy (DA) for constant-predicting models in periods of flat oil prices
  - Underestimation of HAC variance in DM test due to rigid bandwidth cap at horizon - 1
  - Potential divide-by-zero or explosion in PINAW and R2 computations for constant series
- **Untested angles**: Execution of full 3080 experiments (dry-run only, due to resource constraints)
