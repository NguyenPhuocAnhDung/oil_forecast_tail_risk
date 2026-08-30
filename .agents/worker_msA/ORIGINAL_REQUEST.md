## 2026-07-17T16:14:56Z
You are teamwork_preview_worker. Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/worker_msA.
Your task is to implement the Code and Config Infrastructure for Milestone A.
Specifically, you must:
1. Update `config.py` at the project root to include the new taxonomy registry SOTA_TAXONOMY_REGISTRY (32 models total), ALL_SOTA_BASELINES, GUM_NET_VARIANTS, SEEDS_EXTENDED, and HORIZON_TEMPORAL_CONFIG. Keep existing horizons and seeds. Modify `get_unified_config` to read training parameters (test_days, patience, min_epochs) from `HORIZON_TEMPORAL_CONFIG` for the current horizon, while keeping `d_feat` adaptive: `d_feat=64` for horizons 10, 20, 60 and `d_feat=128` for horizons 1, 3, 5, 7.
2. Read the verified code from `/data/quyhv/oil_forecast_tail_risk/.agents/explorer_msA_2/proposed_extended_sota.py` and write it to `src/models/extended_sota.py`.
3. Read the verified code from `/data/quyhv/oil_forecast_tail_risk/.agents/explorer_msA_2/proposed_gumnet_family.py` and write it to `src/models/gumnet_family.py`.
4. Update `get_model_instance(name, cfg)` in `scripts/train_unified.py` to dispatch to the correct classes from `src/models/baselines.py`, `src/models/sota_baselines.py`, `src/models/extended_sota.py`, and `src/models/gumnet_family.py` without raising KeyError for any name in ALL_SOTA_BASELINES + GUM_NET_VARIANTS.
5. Create `requirements_32models.txt` at project root listing the required packages.
6. Create `scripts/check_environment.py` that verifies environment imports and reports readiness of the 32 models.
7. Run the verification script `scripts/check_environment.py` to verify the environment.
8. Document all commands and results in your handoff report at `/data/quyhv/oil_forecast_tail_risk/.agents/worker_msA/handoff.md` and notify the parent (d5f5707c-d383-4212-a14c-d6c762312691) via send_message.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
