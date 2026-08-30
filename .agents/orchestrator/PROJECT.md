# Project: Research OS for GUM-Net under Geopolitical Tail Risk
# Scope: Global Index and Milestones

## Architecture
- All report files are generated in `docs/research_os/` as separate Markdown files.
- Input data: `data/processed/unified_data.csv`.
- GUM-Net model evaluation under sequential geopolitical tail risk.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Exploration | Verify unified_data.csv structure, existing docs/ draft files, references in Refs/, and script utilities. | None | DONE |
| M2 | Phase A (Stg 0-2.5) | Dataset Governance (Stg 0), Problem Reframing (Stg 1), Conceptual Gaps (Stg 2), Regime Characterization (Stg 2.5). | M1 | DONE |
| M3 | Phase B (Stg 3-7) | Evidence Hierarchy (Stg 3), Look-Ahead Bias Audit (Stg 4), Hypothesis Design (Stg 5), Data Pipeline (Stg 6), Taxonomic Baseline (Stg 7). | M2 | DONE |
| M4 | Phase C (Stg 8-11) | Experiment Execution (Stg 8), Failure Case (Stg 9), Econometric Validation (Stg 10), XAI Attributions (Stg 11). | M3 | DONE |
| M5 | Phase D (Stg 12-16) | Peer Review Sim (Stg 12), Technical Manuscript (Stg 13), Decision Layer (Stg 14), Scientific Pedagogy (Stg 15), Workflow Audit (Stg 16). | M4 | DONE |
| M6 | Validation | Review, Challenger verification, and Forensic Auditor check. | M5 | DONE |

## Interface Contracts
- All outputs are separate Markdown files in `docs/research_os/` following specific title conventions (e.g. `## DATASET_GOVERNANCE_REPORT`, `## PROBLEM_FORMULATION_DIRECTIVE`, etc.).

## Code Layout
- `docs/research_os/` - output reports.
- `data/processed/unified_data.csv` - input dataset.
- `scripts/` - execution and analysis scripts.
