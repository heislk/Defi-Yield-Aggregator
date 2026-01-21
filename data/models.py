from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


class StrategyType(Enum):
    STAKING = "STAKING"
    LENDING = "LENDING"
    LIQUIDITY_POOL = "LP (AMM)"


class CompoundingFrequency(Enum):
    DAILY = 365
    WEEKLY = 52
    MONTHLY = 12
    CONTINUOUS = -1


@dataclass
class StrategyConfig:
    name: str
    strategy_type: StrategyType
    base_apr: float
    apr_volatility: float = 0.0
    compounding: CompoundingFrequency = CompoundingFrequency.DAILY
    utilization_rate: float = 0.0
    fee_rate: float = 0.0
    token_volatility: float = 0.0
    
    def __post_init__(self) -> None:
        if self.base_apr > 1.0:
            self.base_apr = self.base_apr / 100.0


@dataclass
class SimulationParams:
    initial_capital: float = 10000.0
    time_horizon_days: int = 180
    num_simulations: int = 1000
    risk_free_rate: float = 0.045
    
    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if self.time_horizon_days <= 0:
            raise ValueError("Time horizon must be positive")
        if self.num_simulations <= 0:
            raise ValueError("Number of simulations must be positive")


@dataclass
class SimulationResult:
    strategy_name: str
    strategy_type: StrategyType
    equity_curves: np.ndarray
    returns: np.ndarray
    drawdowns: np.ndarray
    apr: float
    apy: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    mean_return: float
    median_return: float
    final_values: np.ndarray = field(default_factory=lambda: np.array([]))
    
    def __post_init__(self) -> None:
        if self.equity_curves.size > 0:
            if self.equity_curves.ndim > 1:
                self.final_values = self.equity_curves[:, -1]
            else:
                self.final_values = self.equity_curves


@dataclass
class RiskMetrics:
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    var_99: float = 0.0
    cvar_99: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
