"""
scripts/train_unified.py — Unified Training Script (All Protocols)
=====================================================================
Supports all 4 evaluation protocols from Methodology §4:
 - random: Random Split (Control)
 - chronological: Chronological Split (Conventional)
 - walkforward: Walk-Forward (Deployment)
 - future_holdout: Future Holdout (External Validation)

Usage:
  python scripts/train_unified.py --type XANG --model GUMNet --horizon 5 --protocol walkforward
  python scripts/train_unified.py --type DAU --model LSTM --horizon 10 --protocol random
  python scripts/train_unified.py --type XANG --model all --horizon 0 --protocol all
"""

import argparse
import os
import sys
import copy
import time
import json
import numpy as np
import pandas as pd
import torch
torch.set_num_threads(2)
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config import (
  get_unified_config, DATA_PATH, RESULTS_DIR, BASELINES,
  ALL_HORIZONS, DEFAULT_SEED, BATCH_SIZE, D_FEAT, NUM_QUANTILES,
  PRICE_COLS_TO_LOG, PROTOCOLS, FUTURE_HOLDOUT_RATIO, DATASET_FREEZE_DATE,
  get_output_dir, get_log_dir, ALL_SOTA_BASELINES, GUM_NET_VARIANTS,
)
from src.utils import set_seed, get_device, setup_logger, calculate_metrics
from src.data.dataset import DataProcessor, PetroleumDataset
from src.models.gumnet import GUMNet
from src.models.baselines import get_baseline_model
from src.models.losses import quantile_pinball_loss, HuberQuantileLoss
from src.evaluation.protocols import get_protocol


def get_model_instance(name: str, cfg: dict):
    """
    Unified model dispatcher. Maps a model name to its instantiated PyTorch/ML model.
    Supports baseline models, SOTA models, and GUM-Net family variants.
    """
    import inspect
    import torch.nn as nn
    from src.models.baselines import get_baseline_model
    from src.models.gumnet import GUMNet
    
    # 1. Extract dimensions
    input_dim = cfg.get('input_dim')
    output_dim = cfg.get('output_dim')
    horizon = cfg.get('horizon')
    seq_len = cfg.get('seq_len', 30)
    
    if input_dim is None and 'feature_cols' in cfg:
        input_dim = len(cfg['feature_cols'])
    if output_dim is None and 'target_cols' in cfg:
        output_dim = len(cfg['target_cols'])
    if horizon is None:
        raise ValueError("Horizon must be specified in config for model dispatch.")
        
    # 2. XGBoost Baseline (Special Non-PyTorch case)
    if name == 'XGBoost':
        return get_baseline_model('XGBoost', input_dim, output_dim, horizon)

    # 3. GUM-Net Variants (Quantile models returning predictions, gating_weights)
    is_gumnet = (name == 'GUMNet' or name.startswith('GUMNet_'))
    if is_gumnet:
        d_feat = cfg.get('d_feat', 128 if horizon <= 5 else 64)
        num_quantiles = cfg.get('num_quantiles', 3)
        available_features = cfg.get('available_features', cfg.get('feature_cols', None))
        
        # Base GUMNet (v2)
        if name == 'GUMNet':
            return GUMNet(
                seq_len=seq_len,
                input_dim=input_dim,
                output_dim=output_dim,
                horizon=horizon,
                d_feat=d_feat,
                num_quantiles=num_quantiles
            )
            
        # GUMNet Family Variants in gumnet_family.py (v3)
        gumnet_class_mapping = {
            'GUMNet_Mamba': 'GUMNetMamba',
            'GUMNet_iTrans': 'GUMNetiTrans',
            'GUMNet_Wavelet': 'GUMNetWavelet',
            'GUMNet_Patch': 'GUMNetPatch',
            'GUMNet_Fourier': 'GUMNetFourier',
            'GUMNet_Diffusion': 'GUMNetDiffusion',
            'GUMNet_Graph': 'GUMNetGraph',
            'GUMNet_RL': 'GUMNetRL',
            'GUMNet_MoE_Sparse': 'GUMNetMoESparse',
            'GUMNet_Fusion': 'GUMNetFusion',
            'GUMNet_Decomp': 'GUMNetDecomp',
            'GUMNet_Adaptive': 'GUMNetAdaptive',
            'GUMNetHet': 'GUMNetHet',
        }

        
        class_name = gumnet_class_mapping.get(name)
        if class_name:
            try:
                module = __import__('src.models.gumnet_family', fromlist=[class_name])
                model_class = getattr(module, class_name)
                
                # Check for feature_cols parameter (V3 dynamic features routing in GUMNetHet)
                sig = inspect.signature(model_class.__init__)
                kwargs = {}
                if 'feature_cols' in sig.parameters:
                    kwargs['feature_cols'] = available_features
                    
                return model_class(
                    seq_len=seq_len,
                    input_dim=input_dim,
                    output_dim=output_dim,
                    horizon=horizon,
                    d_feat=d_feat,
                    num_quantiles=num_quantiles,
                    **kwargs
                )
            except (ImportError, AttributeError, ModuleNotFoundError) as e:
                # Safe fallback to GUMNetHet (V3 base) or GUMNet (V2 base) if import fails
                print(f"[Warning] Failed to import {class_name} ({e}). Falling back to GUMNetHet.")
                try:
                    from src.models.gumnet_het import GUMNetHet
                    return GUMNetHet(
                        seq_len=seq_len,
                        input_dim=input_dim,
                        output_dim=output_dim,
                        horizon=horizon,
                        d_feat=d_feat,
                        num_quantiles=num_quantiles,
                        feature_cols=available_features
                    )
                except (ImportError, ModuleNotFoundError):
                    return GUMNet(
                        seq_len=seq_len,
                        input_dim=input_dim,
                        output_dim=output_dim,
                        horizon=horizon,
                        d_feat=d_feat,
                        num_quantiles=num_quantiles
                    )
        else:
            # Fallback for any custom/unregistered GUMNet_ variant name
            from src.models.gumnet_het import GUMNetHet
            return GUMNetHet(
                seq_len=seq_len,
                input_dim=input_dim,
                output_dim=output_dim,
                horizon=horizon,
                d_feat=d_feat,
                num_quantiles=num_quantiles,
                feature_cols=available_features
            )
            
    # 4. Baseline & SOTA PyTorch Models (Deterministic models returning predictions)
    sota_class_mapping = {
        'LSTM': ('src.models.baselines', 'BaselineLSTM'),
        'GRU': ('src.models.baselines', 'BaselineGRU'),
        'BiLSTM_Attention': ('src.models.baselines', 'BaselineBiLSTMAttention'),
        'PatchTST': ('src.models.baselines', 'BaselinePatchTST'),
        'DLinear': ('src.models.baselines', 'BaselineDLinear'),
        'TFT': ('src.models.sota_baselines', 'SimplifiedTFT'),
        'NHits': ('src.models.sota_baselines', 'SimplifiedNHits'),
        'TimesNet': ('src.models.sota_baselines', 'TimesNet'),
        'iTransformer': ('src.models.sota_baselines', 'iTransformer'),
        'TimeMixer': ('src.models.sota_baselines', 'TimeMixer'),
    }
    
    # Defaults to extended_sota.py for new/unmapped SOTAs (e.g. RLinear, Chronos, S_Mamba)
    module_path, class_name = sota_class_mapping.get(name, ('src.models.extended_sota', name))
    
    try:
        module = __import__(module_path, fromlist=[class_name])
        model_class = getattr(module, class_name)
        
        # Check signature to see if the model constructor takes seq_len
        sig = inspect.signature(model_class.__init__)
        kwargs = {}
        if 'seq_len' in sig.parameters:
            kwargs['seq_len'] = seq_len
            
        return model_class(input_dim=input_dim, output_dim=output_dim, horizon=horizon, **kwargs)
        
    except (ImportError, AttributeError, ModuleNotFoundError) as e:
        print(f"[Warning] Failed to import SOTA model {class_name} from {module_path} ({e}). Falling back to dummy linear wrapper.")
        
        # Robust fallback class to avoid KeyError or training crash
        class DummySOTAFallback(nn.Module):
            def __init__(self, input_dim: int, output_dim: int, horizon: int, seq_len: int):
                super().__init__()
                self.horizon = horizon
                self.output_dim = output_dim
                self.linear = nn.Linear(seq_len * input_dim, horizon * output_dim)
                
            def forward(self, x):
                # x: [B, seq_len, input_dim]
                B, L, D = x.shape
                out = self.linear(x.reshape(B, -1))
                return out.view(B, self.horizon, self.output_dim)
                
        return DummySOTAFallback(input_dim=input_dim, output_dim=output_dim, horizon=horizon, seq_len=seq_len)


def load_and_preprocess_data(target_type: str, cfg: dict):
  """Load unified data, compute log-returns, create ratio features."""
  df = pd.read_csv(DATA_PATH)
  df.columns = df.columns.str.strip()
  df['Ngày'] = pd.to_datetime(df['Ngày'])
  if DATASET_FREEZE_DATE:
    freeze_date = pd.Timestamp(DATASET_FREEZE_DATE)
    df = df.loc[df['Ngày'] <= freeze_date].reset_index(drop=True)
  df_raw = df.copy()

  epsilon = 1e-8
  if target_type == 'XANG':
    if all(c in df.columns for c in ['MG95', 'MG92', 'WTI_Daily']):
      wti_safe = df['WTI_Daily'].clip(lower=0.01)
      df['Ratio_95_WTI'] = np.log(df['MG95'] / wti_safe)
      df['Ratio_92_WTI'] = np.log(df['MG92'] / wti_safe)
  else:
    if all(c in df.columns for c in ['DO 0.001%', 'DO 0.05%', 'WTI_Daily']):
      wti_safe = df['WTI_Daily'].clip(lower=0.01)
      df['Ratio_DO001_WTI'] = np.log(df['DO 0.001%'] / wti_safe)
      df['Ratio_DO05_WTI'] = np.log(df['DO 0.05%'] / wti_safe)
      df['Ratio_DO_Spread'] = np.log(df['DO 0.001%'] / (df['DO 0.05%'] + epsilon))

  if 'WTI_Daily' in df.columns:
    df['Trend_WTI'] = np.log(df['WTI_Daily'].clip(lower=0.01) /
                 df['WTI_Daily'].clip(lower=0.01).rolling(10, min_periods=1).mean())
  if 'GPR' in df.columns:
    df['GPR_MA30'] = df['GPR'].rolling(30, min_periods=1).mean()
  if 'USD_Index' in df.columns:
    df['USD_Index_MA30'] = df['USD_Index'].rolling(30, min_periods=1).mean()


  price_cols = [c for c in PRICE_COLS_TO_LOG if c in df.columns]
  for col in price_cols:
    df[col] = np.log(df[col].clip(lower=0.01) / df[col].clip(lower=0.01).shift(1))

  # Volatility regime feature - tính trên log-return WTI để đảm bảo tính dừng I(0)
  if 'WTI_Daily' in df.columns:
    df['Vol_WTI_10d'] = df['WTI_Daily'].rolling(10, min_periods=3).std().fillna(0)
    df['Vol_WTI_30d'] = df['WTI_Daily'].rolling(30, min_periods=5).std().fillna(0)

  if 'USD_Index' in df.columns:
    df['USD_Index'] = np.log(df['USD_Index'] / df['USD_Index'].shift(1))

  ratio_cols = [c for c in df.columns if c.startswith('Ratio_')]
  for col in ratio_cols:
    df[col] = df[col] - df[col].shift(1)

  if 'GPR_MA30' in df.columns:
    df['GPR_MA30'] = np.log(df['GPR_MA30'] / df['GPR_MA30'].shift(1))
  if 'USD_Index_MA30' in df.columns:
    df['USD_Index_MA30'] = np.log(df['USD_Index_MA30'] / df['USD_Index_MA30'].shift(1))

  df = df.iloc[1:].reset_index(drop=True)
  df_raw = df_raw.iloc[1:].reset_index(drop=True)
  df.ffill(inplace=True)
  df.dropna(inplace=True)
  df_raw = df_raw.iloc[:len(df)].reset_index(drop=True)

  return df, df_raw


def train_one_window(model, train_loader, val_loader, device, cfg, is_gumnet=False):
  """Train model for one window (shared across all protocols)."""
  optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
  scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=10)
  
  from torch.cuda.amp import autocast, GradScaler
  # FFT models (FITS, Autoformer, FedFormer, Reformer, etc.) fail on FP16 cuFFT when signal size is not power of 2.
  no_amp_models = {'FITS', 'Autoformer', 'FedFormer', 'Reformer', 'CoST', 'TimesNet', 'GUMNet_Fourier'}
  model_cls_name = model.__class__.__name__
  is_fft_model = any(m in model_cls_name for m in no_amp_models)
  use_amp = (device.type == 'cuda') and not is_fft_model
  scaler = GradScaler(enabled=use_amp)

  if is_gumnet:
    criterion = HuberQuantileLoss(quantiles=[0.1, 0.5, 0.9], delta=0.02)
  else:
    criterion = nn.MSELoss()

  best_loss = float('inf')
  best_wts = None
  patience_counter = 0

  for epoch in range(cfg.get('max_epochs', 200)):
    model.train()
    train_loss = 0.0
    for batch_X, batch_y in train_loader:
      batch_X = batch_X.to(device)
      batch_y = batch_y.to(device).permute(0, 2, 1)

      optimizer.zero_grad()
      with autocast(enabled=use_amp):
        if is_gumnet:
          preds, gating_weights = model(batch_X)
          loss = 0.0
          for c in range(preds.shape[2]):
            loss += criterion(preds[:, :, c, :], batch_y[:, :, c])
          loss = loss / preds.shape[2]

          # Load-Balancing Regularization (Switch Transformer style)
          alpha_lb = 0.01
          n_experts = gating_weights.shape[-1]
          mean_w = gating_weights.mean(dim=(0, 1))
          uniform = torch.ones_like(mean_w) / n_experts
          load_balance_loss = alpha_lb * torch.sum((mean_w - uniform) ** 2)
          loss = loss + load_balance_loss
        else:
          preds = model(batch_X)
          loss = criterion(preds, batch_y)

      if device.type == 'cuda':
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
      else:
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
      train_loss += loss.item()

    train_loss /= max(len(train_loader), 1)

    model.eval()
    val_loss = 0.0
    with torch.no_grad():
      for batch_X, batch_y in val_loader:
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device).permute(0, 2, 1)
        with autocast(enabled=use_amp):
          if is_gumnet:
            preds, _ = model(batch_X)
            v_loss = 0.0
            for c in range(preds.shape[2]):
              v_loss += criterion(preds[:, :, c, :], batch_y[:, :, c])
            val_loss += (v_loss / preds.shape[2]).item()
          else:
            preds = model(batch_X)
            val_loss += criterion(preds, batch_y).item()

    val_loss /= max(len(val_loader), 1)
    scheduler.step(val_loss)

    if val_loss < best_loss:
      best_loss = val_loss
      best_wts = copy.deepcopy(model.state_dict())
      patience_counter = 0
    else:
      patience_counter += 1

    if patience_counter >= cfg['patience'] and epoch >= cfg['min_epochs']:
      break

  if best_wts:
    model.load_state_dict(best_wts)
  return model, best_loss


def predict_window(model, X_test, processor, df_raw, test_row_idx,
          target_cols, device, is_gumnet=False, conformal_adjust=None):
  """Make predictions for one test window. Returns (pred_prices, q10, q90, gating_w)."""
  model.eval()
  with torch.no_grad():
    X_tensor = torch.tensor(X_test[-1:], dtype=torch.float32).to(device)

    if is_gumnet:
      pred_out, gating_w = model(X_tensor)  # [1, H, C, Q]
      pred_q10 = pred_out[0, :, :, 0].cpu().numpy()  # Q10
      pred_scaled = pred_out[0, :, :, 1].cpu().numpy()  # Q50 (median) for point forecast
      pred_q90 = pred_out[0, :, :, 2].cpu().numpy()  # Q90
      gating_w_np = gating_w.cpu().numpy()
    else:
      pred_out = model(X_tensor)
      pred_scaled = pred_out[0].cpu().numpy()
      pred_q10, pred_q90 = None, None
      gating_w_np = None

    log_returns = processor.inverse_transform_targets(pred_scaled.T).T
    base_prices = df_raw.iloc[test_row_idx][target_cols].values
    pred_prices = base_prices * np.exp(log_returns)

    # Convert q10/q90 log-returns to prices for calibration
    if pred_q10 is not None:
      lr_q10 = processor.inverse_transform_targets(pred_q10.T).T
      lr_q50 = log_returns
      lr_q90 = processor.inverse_transform_targets(pred_q90.T).T
      
      if conformal_adjust is not None:
        lr_q10 = lr_q50 - conformal_adjust
        lr_q90 = lr_q50 + conformal_adjust
        
      prices_q10 = base_prices * np.exp(lr_q10)
      prices_q90 = base_prices * np.exp(lr_q90)
    else:
      prices_q10, prices_q90 = None, None

    return pred_prices, prices_q10, prices_q90, gating_w_np


def run_experiment(model_name: str, target_type: str, horizon: int,
          protocol_name: str, seed: int = DEFAULT_SEED):
  """Run full experiment for one (model, target, horizon, protocol) combination."""
  output_dir = os.path.join(RESULTS_DIR, protocol_name, model_name, f'{target_type}_H{horizon}_seed{seed}')
  json_path = os.path.join(output_dir, 'results.json')
  pred_path = os.path.join(output_dir, 'predictions.csv')
  if os.path.exists(json_path) and os.path.exists(pred_path):
    try:
      with open(pred_path, 'r', encoding='utf-8') as pf:
        lines = pf.readlines()
        if len(lines) > 1:
          last_date = lines[-1].split(',')[0].strip()
          freeze_cutoff = DATASET_FREEZE_DATE or '2026-04-30'
          if last_date <= freeze_cutoff:
            print(f"Skipping {model_name} | {target_type} | H{horizon} | {protocol_name} | seed={seed} (already completed valid <= {freeze_cutoff})")
            return None
    except Exception:
      pass

  start_time = time.time()
  set_seed(seed)
  device = get_device()
  cfg = get_unified_config(target_type, horizon)
  is_gumnet = (model_name == 'GUMNet' or model_name.startswith('GUMNet_'))

  # Output dir: results_v4/{protocol}/{model}/{target}_H{horizon}_seed{seed}/
  os.makedirs(output_dir, exist_ok=True)
  log_dir = os.path.join(RESULTS_DIR, 'logs', model_name)
  os.makedirs(log_dir, exist_ok=True)
  logger = setup_logger(f'{model_name}_{target_type}_H{horizon}_{protocol_name}', log_dir)

  logger.info("=" * 80)
  logger.info(f" {model_name} | {target_type} | H{horizon} | {protocol_name} | seed={seed}")
  logger.info("=" * 80)

  # Load data
  df, df_raw = load_and_preprocess_data(target_type, cfg)
  target_cols = cfg['target_cols']
  feature_cols = cfg['feature_cols']
  available_features = [c for c in feature_cols if c in df.columns]

  # Add structural dimensions to config dictionary for dispatcher compatibility
  cfg['input_dim'] = len(available_features)
  cfg['output_dim'] = len(target_cols)
  cfg['horizon'] = horizon
  cfg['available_features'] = available_features
  cfg['num_quantiles'] = NUM_QUANTILES

  logger.info(f"Data: {len(df)} rows | Features: {len(available_features)}")

  # Get protocol
  proto_kwargs = {}
  if protocol_name == 'future_holdout':
    proto_kwargs['holdout_ratio'] = FUTURE_HOLDOUT_RATIO
  protocol = get_protocol(
    protocol_name, seq_len=cfg['seq_len'], horizon=horizon,
    seed=seed, **proto_kwargs
  )

  all_true, all_pred, all_errors, all_gating = [], [], [], []
  all_q10, all_q90 = [], []  # quantile intervals for PICP/PINAW
  all_dates, all_products = [], []
  iteration = 0
  trained_model = None

  for df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info in \
      protocol.get_splits(df, df_raw, cfg['test_days']):

    iteration += 1

    # Prepare data
    processor = DataProcessor(seq_len=cfg['seq_len'], horizon=horizon)

    X_train, y_train = processor.prepare_data(
      df_train, target_cols, available_features,
      df_raw=df_raw_train, is_train=True, fit_scaler=True
    )
    X_val, y_val = processor.prepare_data(
      df_val, target_cols, available_features,
      df_raw=df_raw_val, is_train=False, fit_scaler=False
    )
    X_test, _ = processor.prepare_data(
      df_test, target_cols, available_features,
      df_raw=df_raw_test, is_train=False, fit_scaler=False
    )

    if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
      continue

    train_loader = DataLoader(PetroleumDataset(X_train, y_train),
                 batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)
    val_loader = DataLoader(PetroleumDataset(X_val, y_val),
                batch_size=BATCH_SIZE, shuffle=False, pin_memory=True)

    # Create fresh model (Fair Comparison — train from scratch each window)
    if is_gumnet:
      pass # Handled below
    else:
      is_xgboost = (model_name == 'XGBoost')
      if is_xgboost:
        if protocol_name == 'walkforward' or trained_model is None:
          xgb_model = get_model_instance('XGBoost', cfg)
          xgb_model.fit(X_train, y_train)
          trained_model = xgb_model
        else:
          xgb_model = trained_model

        pred_scaled = xgb_model.predict(X_test[-1:])
        pred_log_ret = processor.inverse_transform_targets(pred_scaled[0].T).T

        # Find test row in df_raw
        test_start_row = split_info.get('train_end', split_info.get('test_start',
                split_info.get('test_row', len(df) - cfg['test_days'])))
        base_prices = df_raw.iloc[test_start_row - 1][target_cols].values
        pred_prices = base_prices * np.exp(pred_log_ret)
        true_prices = df_raw.iloc[test_start_row:test_start_row + horizon][target_cols].values
        gating_w_np = None

        if len(true_prices) > 0:
          m = calculate_metrics(true_prices, pred_prices)
          all_true.extend(true_prices.tolist())
          all_pred.extend(pred_prices.tolist())
          all_errors.extend((true_prices - pred_prices).flatten().tolist())
          logger.info(f" Iter-{iteration:02d} | MAE={m['MAE']:.3f} | MAPE={m['MAPE']:.2f}%")
        continue

    # Train PyTorch models
    if protocol_name == 'walkforward' or trained_model is None:
      model = get_model_instance(model_name, cfg).to(device)

      model, best_val = train_one_window(model, train_loader, val_loader,
                        device, cfg, is_gumnet=is_gumnet)
      trained_model = model
    else:
      model = trained_model

    # Predict
    test_start_row = split_info.get('train_end', split_info.get('test_start',
             split_info.get('test_row', len(df) - cfg['test_days'])))

    conformal_adjust = None
    if model_name == 'GUMNet_Adaptive' and is_gumnet:
      model.eval()
      val_errors = []
      with torch.no_grad():
        for val_X, val_y in val_loader:
          val_X = val_X.to(device)
          val_y = val_y.to(device).permute(0, 2, 1) # [B, H, C]
          v_preds, _ = model(val_X) # [B, H, C, Q]
          v_pred_q50 = v_preds[:, :, :, 1] # [B, H, C]
          
          for b in range(val_X.shape[0]):
            pred_unscaled = processor.inverse_transform_targets(v_pred_q50[b].cpu().numpy().T).T
            y_unscaled = processor.inverse_transform_targets(val_y[b].cpu().numpy().T).T
            val_errors.append(np.abs(y_unscaled - pred_unscaled))
      if val_errors:
        val_errors_np = np.array(val_errors)
        conformal_adjust = np.quantile(val_errors_np, 0.80, axis=0)

    pred_prices, prices_q10, prices_q90, gating_w_np = predict_window(
      model, X_test, processor, df_raw, test_start_row - 1,
      target_cols, device, is_gumnet=is_gumnet, conformal_adjust=conformal_adjust)
    true_prices = df_raw.iloc[test_start_row:test_start_row + horizon][target_cols].values

    if len(true_prices) > 0 and len(pred_prices) > 0:
      # Ensure shapes match
      min_len = min(len(true_prices), len(pred_prices))
      true_prices = true_prices[:min_len]
      pred_prices = pred_prices[:min_len]

      m = calculate_metrics(true_prices, pred_prices)
      all_true.extend(true_prices.tolist())
      all_pred.extend(pred_prices.tolist())
      all_errors.extend((true_prices - pred_prices).flatten().tolist())
      
      dates = df_raw.iloc[test_start_row:test_start_row + horizon]['Ngày'].dt.strftime('%Y-%m-%d').tolist()
      for i in range(min_len):
        d = dates[i]
        for p in target_cols:
          all_dates.append(d)
          all_products.append(p)
      if prices_q10 is not None:
        all_q10.extend(prices_q10[:min_len].tolist())
        all_q90.extend(prices_q90[:min_len].tolist())
      if gating_w_np is not None:
        all_gating.append(gating_w_np)
      logger.info(f" Iter-{iteration:02d} | MAE={m['MAE']:.3f} | MAPE={m['MAPE']:.2f}%")

  # Aggregate
  elapsed = time.time() - start_time

  if not all_true:
    logger.warning("No predictions generated!")
    return None

  all_true_np = np.array(all_true)
  all_pred_np = np.array(all_pred)
  overall = calculate_metrics(all_true_np, all_pred_np)

  logger.info(f"\n OVERALL: MAE={overall['MAE']:.3f}, MAPE={overall['MAPE']:.2f}%, "
        f"R2={overall['R2']:.4f} ({elapsed:.1f}s)")

  # Save
  results = {
    'model': model_name,
    'target_type': target_type,
    'horizon': horizon,
    'protocol': protocol_name,
    'seed': seed,
    'metrics': overall,
    'n_iterations': iteration,
    'n_features': len(available_features),
    'runtime_seconds': round(elapsed, 1),
    'status': 'completed',
    'datetime': datetime.utcnow().isoformat() + 'Z',
  }

  np.save(os.path.join(output_dir, 'errors.npy'), np.array(all_errors))
  if is_gumnet and all_gating:
    # gating_w_np is usually [1, horizon, num_experts]
    try:
        gating_arr = np.concatenate(all_gating, axis=0) # [num_windows, horizon, num_experts]
        np.save(os.path.join(output_dir, 'gating_weights.npy'), gating_arr)
    except Exception as e:
        logger.warning(f"Failed to save gating weights: {e}")
  # Save predictions (with quantile columns for PICP computation)
  pred_df = pd.DataFrame({
    'date': all_dates,
    'product': all_products,
    'true': all_true_np.flatten(),
    'pred': all_pred_np.flatten()
  })
  if all_q10:
    q10_np = np.array(all_q10)
    q90_np = np.array(all_q90)
    pred_df['q10'] = q10_np.flatten()
    pred_df['q90'] = q90_np.flatten()
    # PICP metric
    covered = ((pred_df['true'] >= pred_df['q10']) & (pred_df['true'] <= pred_df['q90'])).mean()
    results['metrics']['PICP'] = round(float(covered * 100), 2)
    results['metrics']['PINAW'] = round(float((q90_np - q10_np).mean()), 4)
    
    # Calculate CRPS for quantile models
    from src.evaluation.metrics import calculate_crps
    crps_val = calculate_crps(all_true_np, q10_np, all_pred_np, q90_np)
    results['metrics']['crps'] = round(crps_val, 6)
  else:
    # Deterministic models: CRPS is mathematically identical to MAE
    results['metrics']['crps'] = overall['MAE']
    
  pred_df.to_csv(os.path.join(output_dir, 'predictions.csv'), index=False)

  # Save model checkpoint + scaler/processor (final walk-forward window)
  if trained_model is not None and model_name != 'XGBoost':
    try:
      import pickle
      ckpt_path = os.path.join(output_dir, 'model_checkpoint.pth')
      torch.save({
        'model_name': model_name,
        'target_type': target_type,
        'horizon': horizon,
        'seed': seed,
        'state_dict': trained_model.state_dict(),
        'n_features': len(available_features),
        'feature_names': available_features,
        'metrics': overall,
        'datetime': results.get('datetime'),
      }, ckpt_path)
      logger.info(f"Saved model checkpoint: {ckpt_path}")
      # Save DataProcessor (contains fitted scaler)
      proc_path = os.path.join(output_dir, 'processor.pkl')
      with open(proc_path, 'wb') as pf:
        pickle.dump(processor, pf)
      logger.info(f"Saved processor/scaler: {proc_path}")
    except Exception as e:
      logger.warning(f"Failed to save checkpoint/scaler: {e}")

  with open(os.path.join(output_dir, 'results.json'), 'w') as f:
    json.dump(results, f, indent=2)

  return results


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Unified Training (All Protocols)')
  parser.add_argument('--type', type=str, required=True, choices=['DAU', 'XANG'])
  parser.add_argument('--model', type=str, default='all', help='Model name or "all"')
  parser.add_argument('--horizon', type=int, default=0, help='Horizon (0 = all)')
  parser.add_argument('--protocol', type=str, default='all', help='Protocol or "all"')
  parser.add_argument('--seed', type=int, default=DEFAULT_SEED)
  args = parser.parse_args()

  models = (['GUMNet'] + BASELINES) if args.model == 'all' else [args.model]
  horizons = ALL_HORIZONS if args.horizon == 0 else [args.horizon]
  protocols = PROTOCOLS if args.protocol == 'all' else [args.protocol]

  total = len(models) * len(horizons) * len(protocols)
  done = 0

  for protocol in protocols:
    for model_name in models:
      for h in horizons:
        done += 1
        print(f"\n{'='*80}")
        print(f" [{done}/{total}] {model_name} | {args.type} | H{h} | {protocol}")
        print(f"{'='*80}\n")
        run_experiment(model_name, args.type, h, protocol, args.seed)

  print(f"\n All {total} experiments completed!")
