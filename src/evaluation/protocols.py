"""
src/evaluation/protocols.py — Evaluation Protocol Design (Methodology §4)
=============================================================================
4 protocols, mỗi protocol có Scientific Purpose riêng:
 - Random Split   → Control protocol
 - Chronological  → Conventional protocol
 - Walk-Forward   → Deployment protocol
 - Future Holdout  → External validation protocol

Tất cả protocols implement chung interface để đảm bảo Fair Comparison.
"""

import numpy as np
import pandas as pd
from typing import Generator, Tuple, Optional
from abc import ABC, abstractmethod


class BaseProtocol(ABC):
  """Abstract base class cho Evaluation Protocols."""

  def __init__(self, seq_len: int, horizon: int, seed: int = 42):
    self.seq_len = seq_len
    self.horizon = horizon
    self.seed = seed

  @abstractmethod
  def get_splits(self, df: pd.DataFrame, df_raw: pd.DataFrame,
          test_days: int) -> Generator[Tuple, None, None]:
    """
    Yield tuples of (df_train, df_val, df_raw_train, df_raw_val,
             df_test_slice, df_raw_test_slice, split_info).
    """
    pass

  @property
  @abstractmethod
  def name(self) -> str:
    pass

  @property
  @abstractmethod
  def scientific_purpose(self) -> str:
    pass


class RandomSplitProtocol(BaseProtocol):
  """
  Random Split — Control Protocol.
  Chia ngẫu nhiên để phơi bày sự nguy hiểm của temporal information leakage.
  Chỉ dùng làm baseline đối chứng, KHÔNG dùng để chọn mô hình.
  """

  @property
  def name(self) -> str:
    return "random"

  @property
  def scientific_purpose(self) -> str:
    return "Control"

  def get_splits(self, df: pd.DataFrame, df_raw: pd.DataFrame,
          test_days: int) -> Generator[Tuple, None, None]:
    rng = np.random.RandomState(self.seed)
    n = len(df)

    # Tạo indices và shuffle
    all_indices = np.arange(n - self.seq_len - self.horizon + 1)
    rng.shuffle(all_indices)

    # Split 70/15/15
    n_samples = len(all_indices)
    train_end = int(n_samples * 0.70)
    val_end = int(n_samples * 0.85)

    train_indices = sorted(all_indices[:train_end])
    val_indices = sorted(all_indices[train_end:val_end])
    test_indices = sorted(all_indices[val_end:])

    # Chia thành các iterations giống Walk-Forward để so sánh công bằng
    iterations = max(1, test_days // self.horizon)
    test_per_iter = max(1, len(test_indices) // iterations)

    for i in range(min(iterations, len(test_indices))):
      start_idx = i * test_per_iter
      if start_idx >= len(test_indices):
        break

      test_idx = test_indices[start_idx]
      test_row = test_idx + self.seq_len

      # Train: lấy tất cả train data
      train_size = int(len(train_indices) * 0.85)
      df_train = df.iloc[train_indices[:train_size]]
      df_val = df.iloc[val_indices]
      df_raw_train = df_raw.iloc[train_indices[:train_size]]
      df_raw_val = df_raw.iloc[val_indices]

      # Test slice
      test_start = max(0, test_row - self.seq_len)
      test_end = min(n, test_row + self.horizon)
      df_test = df.iloc[test_start:test_end]
      df_raw_test = df_raw.iloc[test_start:test_end]

      split_info = {
        'protocol': self.name,
        'iteration': i + 1,
        'test_row': int(test_row),
      }

      yield df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info


class ChronologicalSplitProtocol(BaseProtocol):
  """
  Chronological Split — Conventional Protocol.
  Cắt ngang chuỗi thời gian tại 1 mốc duy nhất (70/15/15).
  """

  @property
  def name(self) -> str:
    return "chronological"

  @property
  def scientific_purpose(self) -> str:
    return "Conventional"

  def get_splits(self, df: pd.DataFrame, df_raw: pd.DataFrame,
          test_days: int) -> Generator[Tuple, None, None]:
    n = len(df)

    # Fixed chronological split: 70/15/15
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    df_train = df.iloc[:train_end]
    df_val = df.iloc[train_end - self.seq_len:val_end]
    df_raw_train = df_raw.iloc[:train_end]
    df_raw_val = df_raw.iloc[train_end - self.seq_len:val_end]

    # Walk through test set in horizon-sized steps
    iterations = (n - val_end) // self.horizon
    for i in range(iterations):
      current_test_start = val_end + (i * self.horizon)
      test_start = current_test_start - self.seq_len
      test_end = min(n, current_test_start + self.horizon)

      df_test = df.iloc[test_start:test_end]
      df_raw_test = df_raw.iloc[test_start:test_end]

      split_info = {
        'protocol': self.name,
        'iteration': i + 1,
        'test_start': int(current_test_start),
      }

      yield df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info


class WalkForwardProtocol(BaseProtocol):
  """
  Expanding-Window Walk-Forward — Deployment Protocol.
  Mô phỏng chính xác kịch bản vận hành thực tế.

  Args:
    step_size: Số ngày tiến mỗi bước walk-forward. Mặc định = horizon (non-overlapping).
               Với H10, dùng step_size=5 để có 40 điểm đánh giá thay vì 20,
               giúp ước tính R² ổn định hơn.
  """

  def __init__(self, seq_len: int, horizon: int, seed: int = 42,
               step_size: int = None):
    super().__init__(seq_len, horizon, seed)
    # step_size=None → dùng horizon (non-overlapping, legacy behavior)
    # step_size=5 tại H10 → stride 5 ngày, nhiều điểm đánh giá hơn
    self.step_size = step_size if step_size is not None else horizon

  @property
  def name(self) -> str:
    return "walkforward"

  @property
  def scientific_purpose(self) -> str:
    return "Deployment"

  def get_splits(self, df: pd.DataFrame, df_raw: pd.DataFrame,
          test_days: int) -> Generator[Tuple, None, None]:
    n = len(df)
    # Dùng step_size thay vì horizon để điều chỉnh mật độ đánh giá
    # H10 step_size=5: 200 test_days / 5 = 40 iterations (nhiều điểm hơn)
    # H10 step_size=10 (legacy): 200 / 10 = 20 iterations
    effective_step = self.step_size
    iterations = test_days // effective_step

    for i in range(iterations):
      current_train_end = n - test_days + (i * effective_step)
      train_size = int(current_train_end * 0.85)

      df_train = df.iloc[:train_size]
      df_val = df.iloc[train_size - self.seq_len:current_train_end]
      df_raw_train = df_raw.iloc[:train_size]
      df_raw_val = df_raw.iloc[train_size - self.seq_len:current_train_end]

      # Test slice: luôn dự báo đúng horizon ngày
      test_start = current_train_end - self.seq_len
      test_end = min(n, current_train_end + self.horizon)
      df_test = df.iloc[test_start:test_end]
      df_raw_test = df_raw.iloc[test_start:test_end]

      split_info = {
        'protocol': self.name,
        'iteration': i + 1,
        'train_end': int(current_train_end),
        'step_size': effective_step,
      }

      yield df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info


class FutureHoldoutProtocol(BaseProtocol):
  """
  Future Holdout — External Validation Protocol.
  Trích xuất đoạn thời gian cuối cùng (final 15%) làm unseen future test.
  IMMUTABLE: Một khi đã tách, không script nào được phép thay đổi.
  
  Future Holdout is never used for model selection, hyperparameter tuning,
  early stopping, or threshold tuning.
  """

  def __init__(self, seq_len: int, horizon: int, seed: int = 42,
         holdout_ratio: float = 0.15):
    super().__init__(seq_len, horizon, seed)
    self.holdout_ratio = holdout_ratio

  @property
  def name(self) -> str:
    return "future_holdout"

  @property
  def scientific_purpose(self) -> str:
    return "External validation"

  def get_holdout_split_index(self, n: int) -> int:
    """Return the index where the Future Holdout begins."""
    return int(n * (1.0 - self.holdout_ratio))

  def get_splits(self, df: pd.DataFrame, df_raw: pd.DataFrame,
          test_days: int) -> Generator[Tuple, None, None]:
    n = len(df)
    holdout_start = self.get_holdout_split_index(n)

    # Train on everything BEFORE holdout using Walk-Forward within that range
    df_pre = df.iloc[:holdout_start]
    df_raw_pre = df_raw.iloc[:holdout_start]
    n_pre = len(df_pre)

    # Use Walk-Forward within the pre-holdout data for training
    wf_test_days = min(test_days, n_pre // 4)
    wf_iterations = max(1, wf_test_days // self.horizon)

    # Final model is trained on all pre-holdout data (Walk-Forward best)
    train_size = int(n_pre * 0.85)
    df_train = df_pre.iloc[:train_size]
    df_val = df_pre.iloc[train_size - self.seq_len:]
    df_raw_train = df_raw_pre.iloc[:train_size]
    df_raw_val = df_raw_pre.iloc[train_size - self.seq_len:]

    # Test on the IMMUTABLE Future Holdout segment
    holdout_iterations = (n - holdout_start) // self.horizon
    for i in range(holdout_iterations):
      current_test_start = holdout_start + (i * self.horizon)
      test_start = max(0, current_test_start - self.seq_len)
      test_end = min(n, current_test_start + self.horizon)

      df_test = df.iloc[test_start:test_end]
      df_raw_test = df_raw.iloc[test_start:test_end]

      split_info = {
        'protocol': self.name,
        'iteration': i + 1,
        'holdout_start': int(holdout_start),
        'test_start': int(current_test_start),
        'immutable': True,
      }

      yield df_train, df_val, df_raw_train, df_raw_val, df_test, df_raw_test, split_info


# Cấu hình step_size theo horizon (cho Walk-Forward)
# Dựa trên phân tích chuyên gia top 0.1%: H10 cần step_size=5 để có đủ điểm đánh giá
# và tránh ước lượng R² không ổn định do quá ít iterations.
WALKFORWARD_STEP_SIZE = {
  1:  1,   # H1: stride=1 (mỗi ngày 1 bước)
  3:  3,   # H3: stride=3
  5:  5,   # H5: stride=5
  7:  7,   # H7: stride=7
  10: 5,   # H10: stride=5 → 40 iterations thay vì 20 (more robust R²)
  60: 20,  # H60: stride=20 → nhiều điểm đánh giá hơn
}


def get_protocol(name: str, seq_len: int, horizon: int,
         seed: int = 42, **kwargs) -> BaseProtocol:
  """Factory function cho protocols.
  
  Với walkforward protocol, tự động áp dụng step_size tối ưu theo horizon.
  H10 dùng step_size=5 (thay vì step_size=10 legacy) để có 40 điểm đánh giá,
  giúp ước tính R² ổn định hơn và tránh artifact do ít iteration.
  """
  protocols = {
    'random': RandomSplitProtocol,
    'chronological': ChronologicalSplitProtocol,
    'walkforward': WalkForwardProtocol,
    'future_holdout': FutureHoldoutProtocol,
  }
  if name not in protocols:
    raise ValueError(f"Unknown protocol: {name}. Available: {list(protocols.keys())}")
  
  # Tự động inject step_size cho walkforward nếu chưa được override
  if name == 'walkforward' and 'step_size' not in kwargs:
    kwargs['step_size'] = WALKFORWARD_STEP_SIZE.get(horizon, horizon)
  
  return protocols[name](seq_len=seq_len, horizon=horizon, seed=seed, **kwargs)
