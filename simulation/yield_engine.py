from typing import Tuple

import numpy as np

from data.models import CompoundingFrequency


class YieldEngine:
    @staticmethod
    def apr_to_apy(apr: float, compounding: CompoundingFrequency) -> float:
        if compounding == CompoundingFrequency.CONTINUOUS:
            return np.exp(apr) - 1
        else:
            n = compounding.value
            return (1 + apr / n) ** n - 1
    
    @staticmethod
    def apy_to_apr(apy: float, compounding: CompoundingFrequency) -> float:
        if compounding == CompoundingFrequency.CONTINUOUS:
            return np.log(1 + apy)
        else:
            n = compounding.value
            return n * ((1 + apy) ** (1 / n) - 1)
    
    @staticmethod
    def effective_daily_rate(apr: float, compounding: CompoundingFrequency) -> float:
        if compounding == CompoundingFrequency.CONTINUOUS:
            return np.exp(apr / 365) - 1
        elif compounding == CompoundingFrequency.DAILY:
            return apr / 365
        elif compounding == CompoundingFrequency.WEEKLY:
            weekly_rate = apr / 52
            return (1 + weekly_rate) ** (1 / 7) - 1
        elif compounding == CompoundingFrequency.MONTHLY:
            monthly_rate = apr / 12
            return (1 + monthly_rate) ** (1 / 30) - 1
        else:
            return apr / 365
    
    @staticmethod
    def calculate_yield_drag(apr: float, volatility: float) -> float:
        return 0.5 * volatility ** 2
    
    @staticmethod
    def volatility_adjusted_return(apr: float, volatility: float) -> float:
        drag = YieldEngine.calculate_yield_drag(apr, volatility)
        return apr - drag
    
    @staticmethod
    def compound_returns(
        principal: float,
        apr: float,
        days: int,
        compounding: CompoundingFrequency
    ) -> float:
        if compounding == CompoundingFrequency.CONTINUOUS:
            return principal * np.exp(apr * days / 365)
        else:
            n = compounding.value
            periods = (days / 365) * n
            rate_per_period = apr / n
            return principal * (1 + rate_per_period) ** periods
    
    @staticmethod
    def calculate_total_return(initial: float, final: float) -> float:
        return (final - initial) / initial
    
    @staticmethod
    def annualize_return(total_return: float, days: int) -> float:
        if days <= 0:
            return 0.0
        return (1 + total_return) ** (365 / days) - 1
    
    @staticmethod
    def calculate_apr_apy_spread(
        apr: float, 
        compounding: CompoundingFrequency
    ) -> Tuple[float, float]:
        apy = YieldEngine.apr_to_apy(apr, compounding)
        spread = apy - apr
        return apy, spread
