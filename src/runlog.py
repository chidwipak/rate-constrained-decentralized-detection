"""
runlog.py — Append-only experiment logging to resultsD1.md / resultsD2.md, plus
structured artifact saving (data .npz/.json, configs). Never overwrites; always appends.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _hardware_string():
    cores = os.cpu_count()
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
    except Exception:
        pass
    mem = "unknown"
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    mem = f"{kb/1024/1024:.0f} GiB"
                    break
    except Exception:
        pass
    return f"{platform.system()} {platform.machine()}, {cores} CPU cores, {mem} RAM"


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "n/a"


def save_data(direction: str, exp_id: str, arrays: dict, meta: dict):
    """Save numeric arrays (.npz) and metadata (.json) under results/<dir>/data/."""
    d = os.path.join(ROOT, "results", direction, "data")
    os.makedirs(d, exist_ok=True)
    npz_path = os.path.join(d, f"{exp_id}.npz")
    json_path = os.path.join(d, f"{exp_id}.json")
    np.savez_compressed(npz_path, **{k: np.asarray(v) for k, v in arrays.items()})
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    return npz_path, json_path


def save_config(exp_id: str, config: dict):
    d = os.path.join(ROOT, "configs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{exp_id}.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=2, default=str)
    return path


def append_experiment(direction: str, *, exp_id: str, purpose: str, theory: str,
                      config: dict, seeds, params: dict, runtime_s: float,
                      raw_results: str, figures: list, tables: str,
                      interpretation: str, supports: str, unexpected: str = "",
                      ideas: str = "", improvements: str = "", reviewer_qs: str = "",
                      future_work: str = ""):
    """Append a standardized experiment block to resultsD1.md or resultsD2.md.

    `direction` is 'd1' or 'd2'. Never overwrites — appends only.
    """
    fname = os.path.join(ROOT, f"results{direction.upper()}.md")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    figs_md = "\n".join(f"  - `{f}`" for f in figures) if figures else "  - (none)"
    seeds_str = seeds if isinstance(seeds, str) else ", ".join(map(str, np.atleast_1d(seeds)))
    params_str = "\n".join(f"  - {k}: {v}" for k, v in params.items())
    config_str = json.dumps(config, indent=2, default=str)

    block = f"""
---

## Experiment {exp_id}

- **Timestamp:** {ts}
- **Purpose:** {purpose}
- **Theory being validated:** {theory}
- **Hardware:** {_hardware_string()}
- **Git commit:** {git_commit()}
- **Runtime:** {runtime_s:.1f} s
- **Random seeds:** {seeds_str}

### Parameters
{params_str}

### Configuration
```json
{config_str}
```

### Raw numerical results
{raw_results}

### Tables
{tables}

### Figures produced
{figs_md}

### Interpretation
{interpretation}

### Supports theorem?
{supports}

### Unexpected observations
{unexpected or "None noted."}

### Ideas generated
{ideas or "None noted."}

### Potential improvements
{improvements or "None noted."}

### Reviewer questions answered
{reviewer_qs or "None noted."}

### Future work
{future_work or "None noted."}
"""
    with open(fname, "a") as f:
        f.write(block)
    return fname


def ensure_results_header(direction: str, title: str, preamble: str):
    """Create resultsD?.md with a header if it does not yet exist (idempotent)."""
    fname = os.path.join(ROOT, f"results{direction.upper()}.md")
    if not os.path.exists(fname):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with open(fname, "w") as f:
            f.write(f"# {title}\n\n*Append-only experiment log. Created {ts}.*\n\n{preamble}\n")
    return fname


class Timer:
    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        self.dt = time.time() - self.t0
