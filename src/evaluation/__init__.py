"""
src/evaluation — Evaluation Science Framework
================================================
Implements the complete evaluation methodology from Methodology_Upgraded.md:
 - Protocols: Random, Chronological, Walk-Forward, Future Holdout
 - Ranking: Average Rank (primary) + Borda (sensitivity)
 - Statistics: DM, Friedman, Nemenyi, Spearman, Kendall, Cliff's Delta, RII, PSS
 - Database: Centralized Evaluation Database (schema v2.0)
 - Metrics: MAE, RMSE, MAPE, R², DA
"""

from .metrics import *
from .statistical_tests import *
from .protocols import get_protocol
from .ranking import compute_metric_ranks, compute_average_rank, compute_borda_rank
from .evaluation_database import EvaluationDatabase
