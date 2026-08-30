"""
scripts/pipeline/00_environment.py — Environment Capture
==========================================================
Ghi nhận toàn bộ thông tin môi trường chạy thực nghiệm.
Output: environment.json
"""

import os
import sys
import json
import platform
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def capture_environment() -> dict:
  """Capture full environment info for reproducibility."""
  import torch
  import numpy as np

  env = {
    'captured_at': datetime.utcnow().isoformat() + 'Z',
    'system': {
      'hostname': platform.node(),
      'os': platform.platform(),
      'cpu': platform.processor() or platform.machine(),
      'python': platform.python_version(),
      'architecture': platform.architecture()[0],
    },
    'gpu': {},
    'packages': {
      'torch': torch.__version__,
      'numpy': np.__version__,
    },
  }

  # GPU info
  if torch.cuda.is_available():
    env['gpu'] = {
      'name': torch.cuda.get_device_name(0),
      'count': torch.cuda.device_count(),
      'cuda_version': torch.version.cuda or 'unknown',
      'cudnn_version': str(torch.backends.cudnn.version()) if torch.backends.cudnn.is_available() else 'N/A',
    }
    # Try nvcc --version
    try:
      nvcc_res = subprocess.run(
        ['nvcc', '--version'],
        capture_output=True, text=True, timeout=5
      )
      if nvcc_res.returncode == 0:
        nv_lines = nvcc_res.stdout.strip().split('\n')
        rel_line = [line for line in nv_lines if 'release' in line]
        if rel_line:
          env['gpu']['nvcc_version'] = rel_line[0].strip()
        else:
          env['gpu']['nvcc_version'] = nv_lines[-1].strip()
      else:
        env['gpu']['nvcc_version'] = 'N/A (failed)'
    except Exception:
      env['gpu']['nvcc_version'] = 'N/A (not on PATH)'

    # Try nvidia-smi for RAM info
    try:
      result = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=5
      )
      if result.returncode == 0:
        env['gpu']['memory_mb'] = int(result.stdout.strip())
    except Exception:
      pass
  else:
    env['gpu'] = {'name': 'N/A', 'cuda_version': 'N/A', 'nvcc_version': 'N/A'}

  # RAM
  try:
    import psutil
    env['system']['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
  except ImportError:
    try:
      with open('/proc/meminfo', 'r') as f:
        for line in f:
          if 'MemTotal' in line:
            kb = int(line.split()[1])
            env['system']['ram_gb'] = round(kb / (1024 ** 2), 1)
            break
    except Exception:
      env['system']['ram_gb'] = 'unknown'

  # Additional packages
  try:
    import pandas as pd
    env['packages']['pandas'] = pd.__version__
  except ImportError:
    pass
  try:
    import sklearn
    env['packages']['scikit-learn'] = sklearn.__version__
  except ImportError:
    pass
  try:
    import scipy
    env['packages']['scipy'] = scipy.__version__
  except ImportError:
    pass

  # Git info
  try:
    result = subprocess.run(
      ['git', 'rev-parse', '--short', 'HEAD'],
      capture_output=True, text=True, timeout=5
    )
    env['git_hash'] = result.stdout.strip() if result.returncode == 0 else 'unknown'
  except Exception:
    env['git_hash'] = 'unknown'

  # Dataset info
  from config import DATA_PATH, DATASET_FREEZE_DATE
  env['dataset'] = {
    'path': DATA_PATH,
    'freeze_date': DATASET_FREEZE_DATE,
    'exists': os.path.exists(DATA_PATH),
  }
  if os.path.exists(DATA_PATH):
    env['dataset']['size_bytes'] = os.path.getsize(DATA_PATH)

  return env


def main():
  from config import RESULTS_DIR

  env = capture_environment()

  output_dir = os.path.join(RESULTS_DIR, 'evaluation_database')
  os.makedirs(output_dir, exist_ok=True)
  output_path = os.path.join(output_dir, 'environment.json')

  with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(env, f, indent=2, ensure_ascii=False)

  print(f" Environment captured -> {output_path}")
  print(f"  Python: {env['system']['python']}")
  print(f"  PyTorch: {env['packages']['torch']}")
  print(f"  GPU: {env['gpu'].get('name', 'N/A')}")
  print(f"  NVCC: {env['gpu'].get('nvcc_version', 'N/A')}")
  print(f"  Dataset freeze: {env['dataset']['freeze_date']}")

  return env


if __name__ == '__main__':
  main()
