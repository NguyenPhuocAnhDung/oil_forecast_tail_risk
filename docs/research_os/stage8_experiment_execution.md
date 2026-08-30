## EXPERIMENT_PIPELINE_LOG

# Stage 8: Experiment Execution & Seed Freezing Protocol

This document defines the formal experiment execution architecture, detailing the random-seed freezing protocol, the exact checkpoint and log directory structures, and the unified hyperparameter configuration across all evaluation scenarios.

---

## 1. Random-Seed Freezing Protocol

To ensure absolute numerical reproducibility of the non-linear optimization landscapes, weights initialization, dropout masks, and stochastic routing logits, GUM-Net enforces a strict multi-seed freezing protocol. 

The pipeline is evaluated over **10 independent runs** using a predefined set of random seeds:
$$\mathcal{S} = \{42, 101, 2023, 777, 999, 123, 456, 888, 1111, 2026\}$$

### 1.1 Implementation Specification
At the initialization phase of every training run, the environment and libraries are bound using the following Python block:

```python
import random
import os
import numpy as np
import torch

def set_seed(seed: int):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # for multi-GPU setups
    
    # Enforce deterministic algorithm execution
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

This protocol guarantees that:
1. **Initial Parameter States**: The weights of the Multi-Scale CNN filters, GRU layers, and Wavelet-KAN basis parameters ($\sigma, \mu$) are identically initialized across runs.
2. **Data Shuffling**: The data loader batches are shuffled identically for a given seed, preserving the exact stochastic gradient descent trajectory.
3. **Dropout Stochastics**: All dropout layers in the expert architectures and the gating head operate with consistent random masks.

---

## 2. Directory Structure Blueprint

All outputs, intermediate model checkpoints, and runtime logs are structured under a unified root directory `results_v4/`. This layout separates transient logs, model weights, and out-of-sample predictions.

```
results_v4/
├── checkpoints/                              # Serialized model state dicts
│   └── GUMNet/
│       ├── XANG_H1_seed42_best.pt
│       ├── XANG_H1_seed101_best.pt
│       │   ...
│       ├── DAU_H60_seed1111_best.pt
│       └── DAU_H60_seed2026_best.pt
├── walkforward/                              # Walk-forward evaluation output
│   └── GUMNet/
│       ├── XANG_H3_seed42/
│       │   ├── predictions.csv               # Timestamps, true values, and quantile forecasts
│       │   ├── errors.npy                    # Array of prediction residuals
│       │   ├── gating_weights.npy            # Log of routing gate weights [w1, w2, w3]
│       │   └── results.json                  # Final computed metrics (MAE, RMSE, MAPE, R2, DA)
│       └── ...
└── logs/                                     # Diagnostic runtime logs
    └── GUMNet/
        ├── GUMNet_XANG_H3_walkforward_20260717_162027.log
        ├── GUMNet_XANG_H3_walkforward_20260717_163450.log
        └── ...
```

### 2.1 File Definitions:
* **`predictions.csv`**: Contains four columns: `Ngày` (Date), `target_col` (actual price log-returns), `pred_q10` (10th percentile), `pred_q50` (median point forecast), and `pred_q90` (90th percentile).
* **`gating_weights.npy`**: A binary numpy array of shape $[N_{\text{test}}, H, 3]$ recording the dynamic expert activation routing weights $(w_1, w_2, w_3)$ for each step of the test window.
* **`results.json`**: Stores metadata including training time, parameters count, learning rate profiles, and final evaluation metrics.

---

## 3. Unified Training Hyperparameters

To ensure a fair comparison, all models (GUM-Net and the 11 baseline models) are trained using a unified hyperparameter configuration, managed by the single source of truth configuration file (`config.py`).

| Hyperparameter | Configuration Value | Description / Purpose |
|---|---|---|
| **Optimizer** | AdamW | Incorporates decoupled weight decay to regularize weights. |
| **Base Learning Rate ($\eta$)** | $1 \times 10^{-3}$ ($0.001$) | Initial step size for parameter updates. |
| **Weight Decay** | $1 \times 10^{-4}$ ($0.0001$) | $L_2$ regularization penalty. |
| **Learning Rate Scheduler** | `ReduceLROnPlateau` | Multiplies learning rate by factor $0.5$ if validation loss fails to decrease for 5 consecutive epochs. |
| **Batch Size** | $64$ | Number of samples processed before updating weights. |
| **Gradient Clipping** | Max $L_2$ Norm $= 1.0$ | Mitigates gradient explosion during backpropagation through recurrent and Wavelet-KAN layers. |
| **Loss Function (GUM-Net)** | Pinball Loss + Load-Balancing | Minimizes quantile deviations and ensures expert diversity. |
| **Expert Regularization ($\alpha_{\text{lb}}$)** | $0.01$ | Load-balancing penalty coefficient preventing gate routing collapse. |
| **Max Epochs** | $200$ | Hard limit on the maximum training epochs per window. |

### 3.1 Adaptive Horizon Configurations
To prevent overfitting on shorter horizons and allow sufficient representation capacity on longer strategic windows, GUM-Net adaptively scales look-back sequence lengths, testing parameters, and early stopping boundaries:

```
+-----------------------------------------------------------------------------+
|                        ADAPTIVE HORIZON PARAMETERS                          |
+-----------------------------------------------------------------------------+
| Horizon (H) | Sequence Len (L) | Min Epochs | Patience | Feature Dimension  |
+-------------+------------------+------------+----------+--------------------+
|     H1      |        10        |     20     |    30    |        128         |
|     H3      |        20        |     20     |    30    |        128         |
|     H5      |        30        |     20     |    30    |        128         |
|     H10     |        60        |     30     |    25    |         64         |
|     H20     |       120        |     40     |    30    |         64         |
|     H60     |       180        |     50     |    35    |         64         |
+-----------------------------------------------------------------------------+
```
* **Early Stopping Rule**: Training is terminated early if the validation loss does not improve for `patience` consecutive epochs, provided the model has completed the `min_epochs` requirement.
