# DeFi Yield Aggregator

Monte Carlo simulator for DeFi yield strategies. Built this to stress-test staking, lending, and LP positions before committing real capital.

## What it does

Runs thousands of simulated paths for different yield strategies, then spits out risk metrics (Sharpe, drawdown, VaR, etc.). Can pull live APY data from DefiLlama or use defaults.

## Setup

```bash
pip install -r requirements.txt
```

Needs Python 3.9+ and these packages: numpy, pandas, rich, requests

## Running it

Quick sim with defaults:
```bash
python main.py --quick
```

With live data from DefiLlama:
```bash
python main.py --quick --live
```

Full interactive dashboard:
```bash
python main.py
```

Options:
- `-q` / `--quick` — just run and exit
- `-l` / `--live` — fetch live yields
- `-n 5000` — number of monte carlo paths
- `-d 365` — simulation days

## Output

```
STRATEGY                    APR      APY      VOL   SHARPE       MDD    VaR95    CVaR95
──────────────────────────────────────────────────────────────────────────────────────────
ETH Staking               4.20%    4.29%    37.5%    -0.07    -31.2%   -42.0%    -48.8%
USDC Lending              3.10%    3.15%     0.4%     2.13     -0.1%     1.1%      0.9%
ETH/USDC LP              12.50%   13.31%     2.5%     2.18     -1.4%     0.5%     -1.8%
```

## Structure

```
main.py              # entry point
data/                # models, config, API client
strategies/          # staking, lending, LP implementations  
simulation/          # monte carlo engine
analytics/           # risk calcs (sharpe, var, drawdown)
cli/                 # terminal UI and charts
reports/             # CSV/JSON/TXT export
```

## Notes

- Sharpe uses 4.5% risk-free rate
- LP strategy includes impermanent loss modeling
- Token volatility is calibrated per asset type (stables vs volatile)
