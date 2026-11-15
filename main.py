#!/usr/bin/env python3
"""Zero-drift random-walk forecaster for Polymarket FAA attribution prices.

Reads one case per run from $MAKEFUN_INPUT_DIR (default /input): every
*.in file, in name order. For each market in a case it forecasts the Yes
price at every minute of the next 240 minutes as five quantiles
(0.05, 0.25, 0.5, 0.75, 0.95) and writes one <id>.out per case to
$MAKEFUN_OUTPUT_DIR (default /output).

Model
-----
Zero drift: the median forecast stays at the checkpoint price. The spread
widens like a random walk: at horizon h minutes,
    q_tau = clamp(x + z_tau * sigma * sqrt(h), 0, 1),
rounded to 6 decimals, where x is the checkpoint price and z_tau is the
standard normal quantile at each level.

sigma is estimated per market from the last 360 one-minute raw price
changes (6 hours of history). The raw estimate is the root mean square of
those changes, shrunk toward the prior 0.0025 with weight m / (m + 500),
where m is the number of usable changes, then floored at 0.0005 and
capped at 0.02. A raw change is the simple difference of consecutive
prices; with no usable change, sigma is the prior 0.0025.

Python 3.13, standard library only, no network, deterministic.
"""

import json
import math
import os
from glob import glob

Z = (-1.644854, -0.674490, 0.0, 0.674490, 1.644854)
PRIOR_SIGMA = 0.0025
SIGMA_FLOOR = 0.0005
SIGMA_CAP = 0.02
SHRINK_M = 500.0
LOOKBACK_CHANGES = 360


def estimate_sigma(prices):
    """Per-minute volatility from the last 360 usable one-minute raw changes."""
    changes = []
    start = max(1, len(prices) - LOOKBACK_CHANGES)
    for i in range(start, len(prices)):
        changes.append(prices[i] - prices[i - 1])
    m = len(changes)
    if m == 0:
        return PRIOR_SIGMA
    raw = math.sqrt(sum(d * d for d in changes) / m)
    w = m / (m + SHRINK_M)
    sigma = w * raw + (1.0 - w) * PRIOR_SIGMA
    return min(SIGMA_CAP, max(SIGMA_FLOOR, sigma))


def forecast_market(prices, horizon):
    x = prices[-1]
    sigma = estimate_sigma(prices)
    rows = []
    for h in range(1, horizon + 1):
        spread = sigma * math.sqrt(h)
        row = []
        for z in Z:
            q = x + z * spread
            if q < 0.0:
                q = 0.0
            elif q > 1.0:
                q = 1.0
            row.append(round(q, 6))
        rows.append(row)
    return rows


def forecast_case(case):
    horizon = int(case.get("horizon_minutes", 240))
    forecasts = []
    for market in case["markets"]:
        prices = [float(p) for p in market["prices"]]
        forecasts.append({"id": market["id"], "q": forecast_market(prices, horizon)})
    return {"forecasts": forecasts}


def main():
    input_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    for path in sorted(glob(os.path.join(input_dir, "*.in"))):
        case_id = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            case = json.load(f)
        out = forecast_case(case)
        out_path = os.path.join(output_dir, case_id + ".out")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
            f.write("\n")


if __name__ == "__main__":
    main()
