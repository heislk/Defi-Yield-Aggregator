from typing import Optional

import numpy as np

from data.models import StrategyConfig
from strategies.base import BaseStrategy


class LendingStrategy(BaseStrategy):
    OPTIMAL_UTILIZATION = 0.80
    MIN_UTILIZATION = 0.30
    MAX_UTILIZATION = 0.95
    UTILIZATION_DAILY_VOL = 0.02
    
    def __init__(self, config: StrategyConfig) -> None:
        super().__init__(config)
        self._current_utilization = config.utilization_rate
        self._cached_daily_rate: Optional[float] = None
        self._last_update_day: int = -1
    
    def calculate_daily_yield(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        if self._last_update_day != day:
            self._update_utilization(rng)
            current_apr = self._compute_utilization_rate()
            
            if self.config.apr_volatility > 0:
                daily_apr_vol = self.config.apr_volatility / np.sqrt(self.DAYS_PER_YEAR)
                apr_shock = rng.normal(0, daily_apr_vol)
                current_apr = max(0, current_apr + apr_shock)
            
            self._cached_daily_rate = self._apr_to_daily_rate(current_apr)
            self._last_update_day = day
        
        return self._cached_daily_rate if self._cached_daily_rate is not None else 0.0
    
    def calculate_price_change(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        if self.config.token_volatility <= 0:
            return 0.0
        
        daily_volatility = self.config.token_volatility / np.sqrt(self.DAYS_PER_YEAR)
        return rng.normal(0, daily_volatility)
    
    def get_effective_apr(self) -> float:
        return self._compute_utilization_rate()
    
    def _update_utilization(self, rng: np.random.Generator) -> None:
        change = rng.normal(0, self.UTILIZATION_DAILY_VOL)
        self._current_utilization = np.clip(
            self._current_utilization + change,
            self.MIN_UTILIZATION,
            self.MAX_UTILIZATION,
        )
    
    def _compute_utilization_rate(self) -> float:
        utilization = self._current_utilization
        
        if utilization < self.OPTIMAL_UTILIZATION:
            rate_factor = utilization / self.OPTIMAL_UTILIZATION
            return self.config.base_apr * rate_factor
        
        excess = (utilization - self.OPTIMAL_UTILIZATION) / (1 - self.OPTIMAL_UTILIZATION)
        surge_multiplier = 2.0
        return self.config.base_apr * (1 + surge_multiplier * excess)
