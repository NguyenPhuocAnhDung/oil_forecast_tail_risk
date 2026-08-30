"""
config.py - SINGLE SOURCE OF TRUTH
===================================
File cấu hình thống nhất cho toàn bộ dự án GUMNet-WF v2.
Tất cả models (GUMNet + Baselines) PHẢI import config từ đây.
Đảm bảo Fair Comparison tuyệt đối.
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# DATA PATHS
# ============================================================
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'unified_data.csv')
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'clean_data_exo.csv')
TRADING_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'trading_data_business_days.csv')
DATASET_FREEZE_DATE = '2026-04-30'  # Dataset frozen prior to experimental design

# ============================================================
# TARGET DEFINITIONS
# ============================================================
TARGETS = {
    'XANG': ['MG95', 'MG92'],
    'DAU':  ['DO 0.001%', 'DO 0.05%'],
    'BOTH': ['MG95', 'MG92', 'DO 0.001%', 'DO 0.05%'],
}

# ============================================================
# ALL HORIZONS (Methodology-frozen)
# ============================================================
ALL_HORIZONS = [1, 3, 5, 7, 10, 20, 60]

# ============================================================
# DATA SPLIT RATIOS
# ============================================================
SPLIT_RATIOS = {'train': 0.70, 'validation': 0.15, 'test': 0.15}
DEFAULT_LOOKBACK = 120  # Input window length (business days)

# ============================================================
# CONFIDENCE INTERVAL & SIGNIFICANCE
# ============================================================
CONFIDENCE_LEVEL = 0.95
SIGNIFICANCE_LEVEL = 0.05

# ============================================================
# BASELINES TO RUN (11 models + GUMNet)
# ============================================================
BASELINES = [
    'LSTM', 'GRU', 'BiLSTM_Attention', 'XGBoost', 'PatchTST', 'DLinear',
    'TimesNet', 'iTransformer', 'TimeMixer', 'TFT', 'NHits'
]

# ============================================================
# EXTENDED SOTA & GUMNET VARIANTS (Milestone A)
# ============================================================
SOTA_TAXONOMY_REGISTRY = {
    "P1_Linear":      ["DLinear", "RLinear", "LTSF_Linear", "NBEATS", "NHits"],
    "P2_Transformer": ["PatchTST", "TFT", "Autoformer", "FedFormer", "Informer", "Reformer"],
    "P3_Inverted":    ["iTransformer", "UniTS", "TimeXer", "Crossformer", "CARD"],
    "P4_Frequency":   ["TimesNet", "TimeMixer", "TTM", "FITS", "CoST"],
    "P5_SSM":         ["TimeMachine", "S_Mamba", "MambaFormer", "BiMamba"],
    "P6_Foundation":  ["Chronos", "TimesFM", "Moirai", "Lag_Llama", "TEMPO", "GPT4TS"],
    "P7_SparseMoE":   ["Time_MoE", "Gated_TabNet"],
}
ALL_SOTA_BASELINES = [m for ms in SOTA_TAXONOMY_REGISTRY.values() for m in ms]

GUM_NET_VARIANTS = [
    "GUMNet", "GUMNet_Mamba", "GUMNet_iTrans", "GUMNet_Wavelet",
    "GUMNet_Patch", "GUMNet_Fourier", "GUMNet_Diffusion", "GUMNet_Graph",
    "GUMNet_RL", "GUMNet_MoE_Sparse", "GUMNet_Fusion", "GUMNet_Decomp",
    "GUMNet_Adaptive", "GUMNetHet",
]


HORIZON_TEMPORAL_CONFIG = {
    1:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    3:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    5:  {"test_days": 100, "patience": 30, "min_epochs": 20},
    7:  {"test_days": 150, "patience": 30, "min_epochs": 25},
    10: {"test_days": 200, "patience": 25, "min_epochs": 30},
    20: {"test_days": 300, "patience": 30, "min_epochs": 40},
    60: {"test_days": 600, "patience": 35, "min_epochs": 50},
}

# ============================================================
# UNIFIED FEATURE SETS (FAIR COMPARISON)
# Tất cả models dùng CÙNG feature set cho cùng (target_type, horizon)
# ============================================================
def get_unified_config(target_type: str, horizon: int) -> dict:
    """
    Trả về cấu hình thống nhất cho 1 experiment.
    Cùng features, cùng seq_len, cùng test_days cho TẤT CẢ models.
    """
    cfg = {}

    # --- Hyperparameters theo horizon (matched to experiment.yaml) ---
    hcfg = HORIZON_TEMPORAL_CONFIG.get(horizon, {"test_days": 100, "patience": 15, "min_epochs": 20}).copy()
    cfg.update(hcfg)
    
    # Keep d_feat adaptive
    if horizon in [1, 3, 5, 7]:
        cfg['d_feat'] = 128
    elif horizon in [10, 20, 60]:
        cfg['d_feat'] = 64
    else:
        cfg['d_feat'] = 128  # Fallback
        
    # Add max epochs explicitly
    cfg['max_epochs'] = 200

    # --- Target columns ---
    cfg['target_cols'] = TARGETS[target_type]

    # --- Feature columns: THỐNG NHẤT cho tất cả models ---
    # Các sản phẩm liên ngành (petroleum product prices)
    if target_type == 'XANG':
        product_prices = ['MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO']
        ratio_features = ['Ratio_95_WTI', 'Ratio_92_WTI']
    elif target_type == 'DAU':
        product_prices = ['DO 0.001%', 'DO 0.05%', 'FO 180', 'NAPHTHA', 'KERO']
        ratio_features = ['Ratio_DO001_WTI', 'Ratio_DO05_WTI', 'Ratio_DO_Spread']
    else:  # BOTH (Coupled)
        product_prices = ['MG97', 'MG95', 'MG92', 'DO 0.001%', 'DO 0.05%', 'FO 180', 'NAPHTHA', 'KERO']
        ratio_features = ['Ratio_95_WTI', 'Ratio_92_WTI', 'Ratio_DO001_WTI', 'Ratio_DO05_WTI', 'Ratio_DO_Spread']

    # Crude oil benchmarks
    crude_prices = ['WTI_Daily', 'Brent_EU_Daily', 'BRT_DTD', 'BRT_KH']

    # Macro features
    macro_daily = ['USD_Index', 'GPR']
    macro_derived_short = ['Day_sin', 'Day_cos']
    macro_derived_trend = ['Trend_WTI']
    macro_monthly = ['WTI_Monthly', 'Brent_Global_Monthly']
    macro_ma30 = ['GPR_MA30', 'USD_Index_MA30']
    macro_volatility = ['Vol_WTI_10d', 'Vol_WTI_30d']  # Chỉ dùng tại H60 (có đủ lookback 180 ngày)

    # --- Feature set theo horizon (cùng cho MỌI model) ---
    # Default lookback from experiment.yaml
    # Adaptive lookback: horizon-specific optimal window
    # H1: short window (less noise), H10: longer (regulatory cycle context), H60: 6mo+ history
    seq_len_map = {1: 10, 3: 20, 5: 30, 7: 40, 10: 60, 20: 120, 60: 180}
    cfg['seq_len'] = seq_len_map.get(horizon, DEFAULT_LOOKBACK)

    if horizon in [1, 3]:
        cfg['feature_cols'] = product_prices + crude_prices + ratio_features + macro_daily + macro_derived_short
    elif horizon in [5, 7]:
        cfg['feature_cols'] = product_prices + crude_prices + ratio_features + macro_daily + macro_derived_trend + macro_derived_short
    elif horizon in [10, 20]:
        # FIX (Expert Review Top 0.1%): Loại Vol_WTI_10d/30d khỏi H10/H20 để tránh Router collapse
        # Phân tích gating_weights cho thấy: khi có Vol features, GRU bị suppressed (3.2%)
        # và KAN chiếm 60.7% → prediction collapse (near-constant output)
        # Fix: dùng feature set giống H5 + trend, để Router cân bằng 3 expert
        cfg['feature_cols'] = product_prices + crude_prices + ratio_features + macro_daily + macro_derived_trend
    elif horizon == 60:
        # Add volatility + monthly macro for long-term forecasting (H60 có đủ lookback 180 ngày)
        cfg['feature_cols'] = product_prices + crude_prices + ratio_features + macro_daily + macro_ma30 + macro_monthly + macro_volatility
    else:
        # Fallback for any custom horizon
        cfg['feature_cols'] = product_prices + crude_prices + ratio_features + macro_daily + macro_derived_trend
        
    ablation = os.environ.get('GUMNET_ABLATION', 'none')
    if ablation == 'no_gpr':
        cfg['feature_cols'] = [c for c in cfg['feature_cols'] if 'GPR' not in c]

    if os.environ.get('GUMNET_TEST_MODE') == '1':
        cfg['max_epochs'] = 2
        cfg['min_epochs'] = 1
        cfg['patience'] = 1
        cfg['test_days'] = 10

    return cfg


# ============================================================
# EXPERIMENT SETTINGS
# ============================================================
SEEDS = [42, 123, 777, 2025, 9999]  # Multi-seed (5 seeds as agreed) cho confidence intervals
SEEDS_EXTENDED = [42, 123, 777, 2025, 9999, 101, 888, 2023, 555, 1234]
DEFAULT_SEED = 42
BATCH_SIZE = 64
MAX_EPOCHS = 200
D_FEAT = 128  # Default for short horizons (H1-H5)
D_FEAT_LONG = 64  # For H10, H60 — avoids convergence failure on low-SNR horizons
NUM_QUANTILES = 3
QUANTILES = [0.1, 0.5, 0.9]

# ============================================================
# EVALUATION PROTOCOLS (Methodology §4)
# ============================================================
PROTOCOLS = ['random', 'chronological', 'walkforward', 'future_holdout']
FUTURE_HOLDOUT_RATIO = 0.15  # Final 15% temporal segment — IMMUTABLE once created

# ============================================================
# EVALUATION DATABASE SCHEMA
# ============================================================
EVAL_DB_SCHEMA_VERSION = "2.0"

# ============================================================
# RESULTS PATHS
# ============================================================
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results_v4')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs_v4')
EVAL_DB_DIR = os.path.join(RESULTS_DIR, 'evaluation_database')
PIPELINE_DIR = os.path.join(PROJECT_ROOT, 'scripts', 'pipeline')

# Output directories
def get_output_dir(model_name: str, target_type: str, horizon: int):
    return os.path.join(RESULTS_DIR, model_name, f'{target_type}_H{horizon}')

def get_log_dir(model_name: str):
    return os.path.join(LOGS_DIR, model_name)


# ============================================================
# COLUMNS TO LOG-DIFFERENCE (for stationarity)
# ============================================================
PRICE_COLS_TO_LOG = [
    'MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO',
    'DO 0.001%', 'DO 0.05%', 'FO 180',
    'BRT_DTD', 'BRT_KH',
    'WTI_Daily', 'Brent_EU_Daily',
    'WTI_Monthly', 'Brent_Global_Monthly',
]
USD_COLS_TO_LOG = ['USD_Index', 'USD_Index_MA30']


if __name__ == '__main__':
    # Quick test
    for tt in ['XANG', 'DAU']:
        for h in ALL_HORIZONS:
            cfg = get_unified_config(tt, h)
            print(f"{tt} H{h:02d}: seq_len={cfg['seq_len']:2d}, "
                  f"features={len(cfg['feature_cols']):2d}, "
                  f"test_days={cfg['test_days']:3d}")
