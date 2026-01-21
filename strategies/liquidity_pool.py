import numpy as np

from data.models import StrategyConfig
from strategies.base import BaseStrategy


class LiquidityPoolStrategy(BaseStrategy):
    def __init__(self, config: StrategyConfig) -> None:
        super().__init__(config)
        self._initial_price = 1.0
        self._current_price = 1.0
    
    def simulate_path(
        self,
        initial_capital: float,
        days: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        self._current_price = 1.0
        self._initial_price = 1.0
        return super().simulate_path(initial_capital, days, rng)
    
    def calculate_daily_yield(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        base_daily_yield = self._apr_to_daily_rate(self.config.base_apr)
        
        if self.config.apr_volatility > 0:
            daily_vol = self.config.apr_volatility / np.sqrt(self.DAYS_PER_YEAR)
            volume_factor = rng.lognormal(0, daily_vol)
            return base_daily_yield * volume_factor
        
        return base_daily_yield
    
    def calculate_price_change(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        if self.config.token_volatility <= 0:
            return 0.0
        
        daily_volatility = self.config.token_volatility / np.sqrt(self.DAYS_PER_YEAR)
        price_return = rng.normal(0, daily_volatility)
        
        previous_price = self._current_price
        self._current_price *= (1 + price_return)
        
        current_il = self._compute_impermanent_loss(
            self._current_price / self._initial_price
        )
        previous_il = self._compute_impermanent_loss(
            previous_price / self._initial_price
        )
        
        return current_il - previous_il
    
    def _compute_impermanent_loss(self, price_ratio: float) -> float:
        if price_ratio <= 0:
            return -1.0
        
        return 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
