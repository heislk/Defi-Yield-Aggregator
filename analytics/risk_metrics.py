from dataclasses import dataclass

import numpy as np


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


class RiskMetricsCalculator:
    TRADING_DAYS_PER_YEAR = 252
    CALENDAR_DAYS_PER_YEAR = 365
    MAX_RATIO_VALUE = 10.0
    
    def __init__(self, risk_free_rate: float = 0.045) -> None:
        self.risk_free_rate = risk_free_rate
    
    def calculate_all_metrics(
        self,
        equity_curves: np.ndarray,
        returns: np.ndarray,
        time_horizon_days: int,
    ) -> RiskMetrics:
        return RiskMetrics(
            volatility=self._calculate_volatility(equity_curves),
            sharpe_ratio=self._calculate_sharpe_ratio(equity_curves, time_horizon_days),
            max_drawdown=self._calculate_max_drawdown(equity_curves),
            var_95=self._calculate_var(returns, 0.95),
            cvar_95=self._calculate_cvar(returns, 0.95),
            var_99=self._calculate_var(returns, 0.99),
            cvar_99=self._calculate_cvar(returns, 0.99),
            sortino_ratio=self._calculate_sortino_ratio(equity_curves, time_horizon_days),
            calmar_ratio=self._calculate_calmar_ratio(equity_curves, time_horizon_days),
        )
    
    def _calculate_volatility(self, equity_curves: np.ndarray) -> float:
        daily_returns = self._compute_daily_returns(equity_curves)
        daily_volatility = np.std(daily_returns)
        return daily_volatility * np.sqrt(self.TRADING_DAYS_PER_YEAR)
    
    def _calculate_sharpe_ratio(
        self,
        equity_curves: np.ndarray,
        time_horizon_days: int,
    ) -> float:
        total_return = self._compute_average_total_return(equity_curves)
        annualized_return = self._annualize_return(total_return, time_horizon_days)
        
        daily_returns = self._compute_daily_returns(equity_curves)
        annualized_volatility = np.std(daily_returns) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        
        if annualized_volatility < 0.001:
            return 0.0
        
        sharpe = (annualized_return - self.risk_free_rate) / annualized_volatility
        return float(np.clip(sharpe, -self.MAX_RATIO_VALUE, self.MAX_RATIO_VALUE))
    
    def _calculate_max_drawdown(self, equity_curves: np.ndarray) -> float:
        if equity_curves.ndim == 1:
            running_max = np.maximum.accumulate(equity_curves)
            drawdowns = (equity_curves - running_max) / running_max
            return float(np.min(drawdowns))
        
        running_max = np.maximum.accumulate(equity_curves, axis=1)
        drawdowns = (equity_curves - running_max) / running_max
        max_drawdown_per_sim = np.min(drawdowns, axis=1)
        return float(np.mean(max_drawdown_per_sim))
    
    def _calculate_var(self, returns: np.ndarray, confidence: float) -> float:
        percentile = (1 - confidence) * 100
        return float(np.percentile(returns, percentile))
    
    def _calculate_cvar(self, returns: np.ndarray, confidence: float) -> float:
        var = self._calculate_var(returns, confidence)
        tail_returns = returns[returns <= var]
        
        if len(tail_returns) == 0:
            return var
        return float(np.mean(tail_returns))
    
    def _calculate_sortino_ratio(
        self,
        equity_curves: np.ndarray,
        time_horizon_days: int,
    ) -> float:
        total_return = self._compute_average_total_return(equity_curves)
        annualized_return = self._annualize_return(total_return, time_horizon_days)
        
        daily_returns = self._compute_daily_returns(equity_curves)
        downside_returns = daily_returns[daily_returns < 0]
        
        if len(downside_returns) == 0:
            return self.MAX_RATIO_VALUE
        
        downside_deviation = np.std(downside_returns) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        
        if downside_deviation < 0.001:
            return self.MAX_RATIO_VALUE
        
        sortino = (annualized_return - self.risk_free_rate) / downside_deviation
        return float(np.clip(sortino, -self.MAX_RATIO_VALUE, self.MAX_RATIO_VALUE))
    
    def _calculate_calmar_ratio(
        self,
        equity_curves: np.ndarray,
        time_horizon_days: int,
    ) -> float:
        max_drawdown = self._calculate_max_drawdown(equity_curves)
        
        if max_drawdown >= -0.001:
            return self.MAX_RATIO_VALUE
        
        total_return = self._compute_average_total_return(equity_curves)
        annualized_return = self._annualize_return(total_return, time_horizon_days)
        
        calmar = annualized_return / abs(max_drawdown)
        return float(np.clip(calmar, -self.MAX_RATIO_VALUE, self.MAX_RATIO_VALUE))
    
    def _compute_daily_returns(self, equity_curves: np.ndarray) -> np.ndarray:
        if equity_curves.ndim == 1:
            return np.diff(equity_curves) / equity_curves[:-1]
        
        daily_returns = np.diff(equity_curves, axis=1) / equity_curves[:, :-1]
        return daily_returns.flatten()
    
    def _compute_average_total_return(self, equity_curves: np.ndarray) -> float:
        if equity_curves.ndim == 1:
            return (equity_curves[-1] / equity_curves[0]) - 1
        
        final_values = equity_curves[:, -1]
        initial_values = equity_curves[:, 0]
        return float(np.mean((final_values / initial_values) - 1))
    
    def _annualize_return(self, total_return: float, days: int) -> float:
        return (1 + total_return) ** (self.CALENDAR_DAYS_PER_YEAR / days) - 1
