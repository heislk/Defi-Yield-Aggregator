from typing import Dict, List, Optional

import numpy as np

from analytics.risk_metrics import RiskMetricsCalculator
from data.models import (
    SimulationParams,
    SimulationResult,
    StrategyConfig,
    StrategyType,
)
from strategies.base import BaseStrategy
from strategies.staking import StakingStrategy
from strategies.lending import LendingStrategy
from strategies.liquidity_pool import LiquidityPoolStrategy


def create_strategy(config: StrategyConfig) -> BaseStrategy:
    strategy_map = {
        StrategyType.STAKING: StakingStrategy,
        StrategyType.LENDING: LendingStrategy,
        StrategyType.LIQUIDITY_POOL: LiquidityPoolStrategy,
    }
    
    strategy_class = strategy_map.get(config.strategy_type)
    
    if strategy_class is None:
        raise ValueError("Unknown strategy type: {}".format(config.strategy_type))
    
    return strategy_class(config)


class MonteCarloSimulator:
    def __init__(
        self,
        params: SimulationParams,
        seed: Optional[int] = None,
    ) -> None:
        self.params = params
        self._rng = np.random.default_rng(seed)
        self.risk_calculator = RiskMetricsCalculator(params.risk_free_rate)
    
    def run_simulation(self, strategy_config: StrategyConfig) -> SimulationResult:
        strategy = create_strategy(strategy_config)
        
        equity_curves = self._generate_paths(strategy)
        returns = self._calculate_total_returns(equity_curves)
        drawdowns = self._calculate_drawdown_paths(equity_curves)
        
        risk_metrics = self.risk_calculator.calculate_all_metrics(
            equity_curves,
            returns,
            self.params.time_horizon_days,
        )
        
        return SimulationResult(
            strategy_name=strategy_config.name,
            strategy_type=strategy_config.strategy_type,
            equity_curves=equity_curves,
            returns=returns,
            drawdowns=drawdowns,
            apr=strategy.get_effective_apr(),
            apy=strategy.get_effective_apy(),
            volatility=risk_metrics.volatility,
            sharpe_ratio=risk_metrics.sharpe_ratio,
            max_drawdown=risk_metrics.max_drawdown,
            var_95=risk_metrics.var_95,
            cvar_95=risk_metrics.cvar_95,
            mean_return=float(np.mean(returns)),
            median_return=float(np.median(returns)),
        )
    
    def run_all_simulations(
        self,
        strategies: List[StrategyConfig],
    ) -> List[SimulationResult]:
        return [self.run_simulation(config) for config in strategies]
    
    def _generate_paths(self, strategy: BaseStrategy) -> np.ndarray:
        num_sims = self.params.num_simulations
        num_days = self.params.time_horizon_days
        
        equity_curves = np.zeros((num_sims, num_days + 1))
        
        for sim_idx in range(num_sims):
            equity_curves[sim_idx] = strategy.simulate_path(
                self.params.initial_capital,
                num_days,
                self._rng,
            )
        
        return equity_curves
    
    def _calculate_total_returns(self, equity_curves: np.ndarray) -> np.ndarray:
        final_values = equity_curves[:, -1]
        initial_values = equity_curves[:, 0]
        return (final_values - initial_values) / initial_values
    
    def _calculate_drawdown_paths(self, equity_curves: np.ndarray) -> np.ndarray:
        running_max = np.maximum.accumulate(equity_curves, axis=1)
        return (equity_curves - running_max) / running_max
    
    def get_percentile_paths(
        self,
        equity_curves: np.ndarray,
        percentiles: Optional[List[int]] = None,
    ) -> Dict[int, np.ndarray]:
        if percentiles is None:
            percentiles = [5, 25, 50, 75, 95]
        
        return {
            p: np.percentile(equity_curves, p, axis=0)
            for p in percentiles
        }
