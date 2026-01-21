from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from data.models import StrategyConfig, CompoundingFrequency


class BaseStrategy(ABC):
    DAYS_PER_YEAR = 365
    
    def __init__(self, config: StrategyConfig) -> None:
        self.config = config
        self.name = config.name
        self.strategy_type = config.strategy_type
    
    @abstractmethod
    def calculate_daily_yield(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        pass
    
    @abstractmethod
    def calculate_price_change(
        self,
        day: int,
        rng: np.random.Generator,
    ) -> float:
        pass
    
    def simulate_path(
        self,
        initial_capital: float,
        days: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        equity = np.zeros(days + 1)
        equity[0] = initial_capital
        
        for day in range(1, days + 1):
            daily_yield = self.calculate_daily_yield(day, rng)
            price_change = self.calculate_price_change(day, rng)
            
            combined_return = (1 + daily_yield) * (1 + price_change) - 1
            equity[day] = equity[day - 1] * (1 + combined_return)
        
        return equity
    
    def get_effective_apr(self) -> float:
        return self.config.base_apr
    
    def get_effective_apy(self) -> float:
        return self._convert_apr_to_apy(self.get_effective_apr())
    
    def _convert_apr_to_apy(
        self,
        apr: float,
        compounding: Optional[CompoundingFrequency] = None,
    ) -> float:
        if compounding is None:
            compounding = self.config.compounding
        
        if compounding == CompoundingFrequency.CONTINUOUS:
            return np.exp(apr) - 1
        
        periods = compounding.value
        return (1 + apr / periods) ** periods - 1
    
    def _apr_to_daily_rate(self, apr: float) -> float:
        return apr / self.DAYS_PER_YEAR
