from typing import Dict, List, Union

from data.models import (
    StrategyConfig,
    StrategyType,
    CompoundingFrequency,
    SimulationParams,
)


DEFAULT_STRATEGIES: List[StrategyConfig] = [
    StrategyConfig(
        name="ETH Staking",
        strategy_type=StrategyType.STAKING,
        base_apr=0.042,
        apr_volatility=0.005,
        compounding=CompoundingFrequency.DAILY,
        token_volatility=0.45,
    ),
    StrategyConfig(
        name="USDC Lending",
        strategy_type=StrategyType.LENDING,
        base_apr=0.058,
        apr_volatility=0.02,
        compounding=CompoundingFrequency.DAILY,
        utilization_rate=0.82,
        token_volatility=0.005,
    ),
    StrategyConfig(
        name="ETH/USDC LP",
        strategy_type=StrategyType.LIQUIDITY_POOL,
        base_apr=0.125,
        apr_volatility=0.035,
        compounding=CompoundingFrequency.DAILY,
        fee_rate=0.003,
        token_volatility=0.50,
    ),
]


DEFAULT_SIMULATION_PARAMS = SimulationParams(
    initial_capital=10000.0,
    time_horizon_days=180,
    num_simulations=1000,
    risk_free_rate=0.045,
)


APP_CONFIG: Dict[str, Union[str, int]] = {
    "app_name": "DEFI YIELD AGGREGATOR",
    "version": "1.0",
    "mode": "SIMULATION",
    "refresh_rate": 4,
    "chart_height": 15,
    "chart_width": 60,
}


COLORS: Dict[str, Union[str, List[str]]] = {
    "primary": "bright_blue",
    "secondary": "dim white",
    "text": "white",
    "text_dim": "dim white",
    "header": "bold white",
    "subheader": "dim white",
    "label": "bright_white",
    "value": "white",
    "muted": "dim white",
    "positive": "bright_green",
    "negative": "bright_red",
    "warning": "bright_yellow",
    "neutral": "white",
    "chart_equity": "bright_cyan",
    "chart_positive": "bright_green",
    "chart_negative": "bright_magenta",
    "chart_drawdown": "bright_red",
    "chart_histogram_pos": "bright_green",
    "chart_histogram_neg": "bright_magenta",
    "chart_scatter": [
        "bright_cyan",
        "bright_magenta",
        "bright_yellow",
        "bright_green",
        "bright_red",
    ],
}

BORDERS: Dict[str, str] = {
    "main": "bright_blue",
    "table": "dim white",
    "panel": "dim white",
    "chart": "dim white",
    "menu": "bright_blue",
}


TABLE_FORMAT: Dict[str, int] = {
    "strategy_width": 22,
    "metric_width": 9,
    "total_width": 72,
}
