from typing import Optional

import numpy as np

from data.models import StrategyConfig
from strategies.base import BaseStrategy


class StakingStrategy(BaseStrategy):
    APR_UPDATE_INTERVAL_DAYS = 7
    
    def __init__(self, config: StrategyConfig) -> None:
        super().__init__(config)
        self._cached_apr: Optional[float] = None
        self._last_apr_update_period: int = -1
    
    def calculate_daily_yield(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        current_period = day // self.APR_UPDATE_INTERVAL_DAYS
        
        if self.config.apr_volatility > 0:
            if self._last_apr_update_period != current_period:
                apr_shock = rng.normal(0, self.config.apr_volatility)
                self._cached_apr = max(0, self.config.base_apr + apr_shock)
                self._last_apr_update_period = current_period
            
            current_apr = self._cached_apr if self._cached_apr is not None else self.config.base_apr
        else:
            current_apr = self.config.base_apr
        
        return self._apr_to_daily_rate(current_apr)
    
    def calculate_price_change(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        if self.config.token_volatility <= 0:
            return 0.0
        
        daily_volatility = self.config.token_volatility / np.sqrt(self.DAYS_PER_YEAR)
        return rng.normal(0, daily_volatility)
