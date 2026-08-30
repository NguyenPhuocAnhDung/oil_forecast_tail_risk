#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time

PROJECT_ROOT = "/data/quyhv/oil_forecast_tail_risk"
sys.path.insert(0, PROJECT_ROOT)

print("="*60)
print("GPU WORKLOAD REBALANCER (GPU 0 & GPU 3)")
print("="*60)

# Target PIDs to kill (schedulers for H1,3 on GPU 0, and H5,7,3 on GPU 3)
# We want to keep the H60 scheduler (GPU 0, 2 slots) running.
target_patterns = [
    r"smart_fill_scheduler.py --gpus 0 --slots 3 --horizons 1,3",
    r"smart_fill_scheduler.py --gpus 3 --slots 3 --horizons 5,7",
    r"smart_fill_scheduler.py --gpus 3 --slots 2 --horizons 7",
    r"smart_fill_scheduler.py --gpus 3 --slots 1 --horizons 3"
]

def get_running_schedulers():
    try:
        output = subprocess.check_output(["ps", "-ef"]).decode('utf-8')
    except Exception as e:
        print(f"Error running ps: {e}")
        return []
    
    pids = []
    for line in output.splitlines():
        if "smart_fill_scheduler.py" in line and "grep" not in line:
            parts = line.split()
            if len(parts) >= 8:
                pid = int(parts[1])
                cmd = " ".join(parts[7:])
                pids.append((pid, cmd))
    return pids

running = get_running_schedulers()
to_kill = []

print("Currently running schedulers:")
for pid, cmd in running:
    is_target = False
    for pattern in target_patterns:
        if pattern in cmd:
            is_target = True
            break
    status = "[TARGET TO KILL]" if is_target else "[KEEP RUNNING]"
    print(f"  PID {pid:7d}: {cmd} {status}")
    if is_target:
        to_kill.append((pid, cmd))

if not to_kill:
    print("\nNo target schedulers found running. Maybe already rebalanced?")
else:
    print(f"\nFound {len(to_kill)} target schedulers to terminate.")
    
    # Confirm action
    # (Since this script can be run by user, we perform the kill directly when executed)
    for pid, cmd in to_kill:
        try:
            print(f"Terminating PID {pid}...")
            os.kill(pid, signal.SIGINT) # Send SIGINT for graceful shutdown
        except Exception as e:
            print(f"Failed to kill PID {pid}: {e}")
            
    print("Waiting 5 seconds for processes to exit...")
    time.sleep(5)

# Verify termination
running_after = get_running_schedulers()
still_alive = [pid for pid, cmd in running_after if pid in [p for p, _ in to_kill]]

if still_alive:
    print(f"Warning: Schedulers {still_alive} are still alive. Sending SIGKILL...")
    for pid in still_alive:
        try:
            os.kill(pid, signal.SIGKILL)
        except:
            pass
    time.sleep(2)

print("\nStarting the new joint scheduler for GPU 0 and GPU 3...")
log_path = os.path.join(PROJECT_ROOT, "logs_v4", "smart_scheduler", "gpu0_3_rebalanced.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# command to run:
# python3 scripts/smart_fill_scheduler.py --gpus 0,3 --slots 3 --horizons 1,3,5,7
cmd = [
    "/usr/bin/python3",
    os.path.join(PROJECT_ROOT, "scripts", "smart_fill_scheduler.py"),
    "--gpus", "0,3",
    "--slots", "3",
    "--horizons", "1,3,5,7"
]

print(f"Command: {' '.join(cmd)}")
print(f"Redirecting output to: {log_path}")

log_file = open(log_path, "w", encoding="utf-8")
try:
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=log_file, cwd=PROJECT_ROOT)
    print(f"Successfully started joint scheduler with PID: {proc.pid}")
except Exception as e:
    print(f"Failed to start joint scheduler: {e}")
    log_file.close()

print("\nRebalancing completed successfully!")
print("="*60)
