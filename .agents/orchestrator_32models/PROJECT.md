# Project: Upgrade GUM-Net Research OS with 32 Models

## Architecture
- config.py: Centralized configuration containing taxonomies, horizons, seeds, and temporal configs.
- src/models/: Contains extended SOTA models (`extended_sota.py`) and GUM-Net variants (`gumnet_family.py`).
- scripts/: contains train_unified.py, run_all_32models.py, compile_32model_results.py, dm_test_32models.py, effect_size_32models.py, generate_all_outputs.py, and check_environment.py.
- docs/research_os/: contains the 17 stages reports, specifically stages 2, 5, 7, 9, 10 to be updated.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Milestone_A_Code_Infra | Update config.py, implement src/models/extended_sota.py, src/models/gumnet_family.py, update scripts/train_unified.py, create requirements_32models.txt and scripts/check_environment.py | none | DONE |
| 2 | Milestone_B_Scripts_Pipeline | Create run_all_32models.py, compile_32model_results.py, dm_test_32models.py, effect_size_32models.py, and generate_all_outputs.py | Milestone_A_Code_Infra | DONE |
| 3 | Milestone_C_Reports_Docs | Update docs/research_os/ reports (Stage 2, 5, 7, 9, 10) | Milestone_A_Code_Infra | DONE |
| 4 | Victory_Audit_Bug_Fixes | Resolve Windows encoding crashes and test suite failures (KeyError in empty df, all-NaN exclusions) | Milestone_B_Scripts_Pipeline | DONE |

## Interface Contracts
- SOTA Models: `__init__(input_dim, output_dim, horizon, seq_len, **kwargs)` with forward pass `forward(x)` returning output of shape `[B, horizon, output_dim]`.
- GUM-Net variants: same signature, inherits/extends `gumnet_het.py`.
- Model Dispatch: `get_model_instance(name, cfg)` maps string to model instance in `scripts/train_unified.py`.
