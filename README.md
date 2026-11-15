# faa-attribution-01

[![Competition](https://make.fun/badge/polymarket-faa-attribution-01.svg)](https://make.fun/bounty/polymarket-faa-attribution-01)
[![Rank](https://make.fun/badge/polymarket-faa-attribution-01/jajanb923-netizen/faa-attribution-01/rank.svg)](https://make.fun/bounty/polymarket-faa-attribution-01/leaderboard)
[![Reward](https://make.fun/badge/polymarket-faa-attribution-01/jajanb923-netizen/faa-attribution-01/reward.svg)](https://make.fun/bounty/polymarket-faa-attribution-01/leaderboard)

A deterministic Python forecaster for Polymarket FAA attribution — a zero-drift random walk whose sigma comes from the last 360 one-minute raw price moves, shrunk toward 0.0025.

## Model

For each market the median stays at the checkpoint price (zero drift) and the spread widens like a random walk: at horizon h minutes, `q_tau = clamp(x + z_tau * sigma * sqrt(h), 0, 1)`, rounded to 6 decimals, where x is the checkpoint price and z_tau the standard normal quantile at each level (0.05, 0.25, 0.5, 0.75, 0.95).

Sigma is estimated per market from the last 360 one-minute raw price moves (6 hours). The raw estimate is the root mean square of those moves, shrunk toward the prior 0.0025 with weight m / (m + 500), where m is the number of moves used, then floored at 0.0005 and capped at 0.02.

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` reads every `*.in` file in `$MAKEFUN_INPUT_DIR` and writes one `<id>.out` per case to `$MAKEFUN_OUTPUT_DIR`.

Python 3.13, standard library only, no network, deterministic: two runs on the same case write identical bytes.

---

Built for [make.fun](https://make.fun/r/vttfhgk4) — enter with referral code `vttfhgk4`.
