---
name: benchmark
description: Performance Engineer — benchmark model performance, page load, throughput. Kích hoạt khi nói "benchmark", "đo performance", "so sánh tốc độ", "profile model", "how fast", "throughput test".
---

# ⚡ Performance Benchmark

Bạn là **Performance Engineer** cho `oil_forecast_tail_risk`. Nhiệm vụ: **đo baseline performance, compare trước/sau mỗi thay đổi**.

---

## ML Model Benchmarks

### Inference Speed
```python
# .agents/benchmark_scripts/benchmark_inference.py
"""
Benchmark inference throughput và latency.
Chạy: python .agents/benchmark_scripts/benchmark_inference.py
"""
import sys, time, torch
sys.path.insert(0, '.')

def benchmark_inference(model, input_shape, n_warmup=10, n_runs=100, device='cpu'):
    """
    Args:
        model: PyTorch model
        input_shape: tuple e.g. (1, 10, 1) for (batch, seq, features)
        n_warmup: warmup runs (không tính)
        n_runs: actual benchmark runs
        device: 'cpu' hoặc 'cuda'
    """
    model = model.to(device)
    model.eval()
    x = torch.randn(*input_shape).to(device)
    
    # Warmup
    print(f"Warming up ({n_warmup} runs)...")
    with torch.no_grad():
        for _ in range(n_warmup):
            _ = model(x)
    
    # Sync GPU nếu dùng CUDA
    if device == 'cuda':
        torch.cuda.synchronize()
    
    # Benchmark
    print(f"Benchmarking ({n_runs} runs)...")
    times = []
    with torch.no_grad():
        for _ in range(n_runs):
            start = time.perf_counter()
            _ = model(x)
            if device == 'cuda':
                torch.cuda.synchronize()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms
    
    times_sorted = sorted(times)
    print(f"\n=== Inference Benchmark ===")
    print(f"Device: {device}")
    print(f"Input shape: {input_shape}")
    print(f"Batch size: {input_shape[0]}")
    print(f"Latency p50:  {times_sorted[len(times_sorted)//2]:.2f} ms")
    print(f"Latency p95:  {times_sorted[int(len(times_sorted)*0.95)]:.2f} ms")
    print(f"Latency p99:  {times_sorted[int(len(times_sorted)*0.99)]:.2f} ms")
    print(f"Latency mean: {sum(times)/len(times):.2f} ms")
    print(f"Throughput:   {input_shape[0] / (sum(times)/len(times) / 1000):.1f} samples/sec")
    return times

# Usage — adapt model class name:
try:
    from src.models.gumnet_family import GumNet  # Thay bằng class thực tế
    model = GumNet()
    benchmark_inference(model, input_shape=(1, 10, 1))   # single sample
    benchmark_inference(model, input_shape=(32, 10, 1))  # batch=32
except Exception as e:
    print(f"Benchmark error: {e} — adjust model class name in script")
```

### Training Step Speed
```python
# .agents/benchmark_scripts/benchmark_training.py
"""
Benchmark training throughput.
"""
import sys, time, torch
sys.path.insert(0, '.')

def benchmark_training_step(model, optimizer, criterion, input_shape, n_steps=50):
    model.train()
    times = []
    
    for i in range(n_steps):
        x = torch.randn(*input_shape)
        y = torch.randn(input_shape[0], 1)  # adjust target shape
        
        start = time.perf_counter()
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        end = time.perf_counter()
        
        times.append((end - start) * 1000)
    
    print(f"Training step: {sum(times)/len(times):.2f} ms/step")
    print(f"Throughput: {input_shape[0] / (sum(times)/len(times) / 1000):.1f} samples/sec")
```

### Memory Profile
```python
# .agents/benchmark_scripts/profile_memory.py
"""
Profile GPU/CPU memory usage.
"""
import sys, torch
sys.path.insert(0, '.')

def profile_memory(model, input_shape):
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        model = model.cuda()
        x = torch.randn(*input_shape).cuda()
        
        with torch.no_grad():
            _ = model(x)
        
        peak_mb = torch.cuda.max_memory_allocated() / 1024**2
        print(f"GPU Peak Memory: {peak_mb:.1f} MB")
    else:
        import tracemalloc
        tracemalloc.start()
        x = torch.randn(*input_shape)
        with torch.no_grad():
            _ = model(x)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"CPU Peak Memory: {peak/1024**2:.1f} MB")
```

---

## Benchmark Comparison Report

```markdown
## Benchmark Report
**Date**: [date]
**Branch**: [branch]
**Commit**: [hash]

### Inference Latency
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| p50 (ms) | [X] | [Y] | [±Z%] |
| p95 (ms) | [X] | [Y] | [±Z%] |
| Throughput (samples/s) | [X] | [Y] | [±Z%] |

### Model Quality
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| CRPS | [X] | [Y] | [±Z%] |
| Coverage 90% | [X] | [Y] | [±Z%] |
| MAE | [X] | [Y] | [±Z%] |

### Memory
| | Before | After |
|--|--------|-------|
| GPU Peak (MB) | [X] | [Y] |
| Model Params (M) | [X] | [Y] |

### Verdict
[Faster/Slower by X% with Y% quality change — acceptable/not acceptable]
```

---

## Automated Benchmark in CI

```bash
# Chạy benchmark tự động và compare với baseline
python .agents/benchmark_scripts/benchmark_inference.py 2>&1 | tee .agents/benchmark_results/$(date +%Y%m%d_%H%M%S).txt

# So sánh với baseline
python .agents/benchmark_scripts/compare_benchmarks.py \
  .agents/benchmark_results/baseline.txt \
  .agents/benchmark_results/current.txt
```
