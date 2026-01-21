from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import requests

from data.models import StrategyConfig, StrategyType, CompoundingFrequency


@dataclass
class LiveYieldData:
    protocol: str
    chain: str
    pool: str
    symbol: str
    apy: float
    tvl: float
    il_risk: bool = False
    
    def to_strategy_config(self) -> StrategyConfig:
        symbol_lower = self.symbol.lower()
        pool_lower = self.pool.lower()
        
        is_stablecoin = any(
            token in symbol_lower 
            for token in ["usd", "dai", "usdt", "usdc", "busd", "frax", "tusd"]
        )
        is_staking = any(
            term in pool_lower 
            for term in ["stake", "staking", "steth", "reth"]
        )
        is_lending = any(
            term in pool_lower 
            for term in ["lend", "supply", "aave", "compound", "borrow"]
        )
        
        if is_staking:
            strategy_type = StrategyType.STAKING
            token_volatility = 0.02 if is_stablecoin else 0.45
            apr_volatility = 0.005
        elif is_lending:
            strategy_type = StrategyType.LENDING
            token_volatility = 0.005 if is_stablecoin else 0.35
            apr_volatility = 0.02
        else:
            strategy_type = StrategyType.LIQUIDITY_POOL
            token_volatility = 0.05 if is_stablecoin else 0.55
            apr_volatility = 0.04
        
        if self.il_risk:
            token_volatility *= 1.3
        
        apr = self._convert_apy_to_apr(self.apy)
        
        return StrategyConfig(
            name="{} {}".format(self.protocol, self.symbol),
            strategy_type=strategy_type,
            base_apr=apr,
            apr_volatility=apr_volatility,
            compounding=CompoundingFrequency.DAILY,
            token_volatility=token_volatility,
        )
    
    @staticmethod
    def _convert_apy_to_apr(apy: float) -> float:
        if apy <= 0:
            return 0.0
        
        compounding_periods = 365
        apr = compounding_periods * (np.power(1 + apy, 1 / compounding_periods) - 1)
        return float(apr)


class DefiLlamaProvider:
    BASE_URL = "https://yields.llama.fi"
    REQUEST_TIMEOUT = 10
    
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "User-Agent": "DeFi-Yield-Aggregator/1.0",
        })
    
    def fetch_top_yields(
        self,
        limit: int = 10,
        min_tvl: float = 1_000_000,
        chains: Optional[List[str]] = None,
    ) -> List[LiveYieldData]:
        try:
            response = self._session.get(
                "{}/pools".format(self.BASE_URL), 
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            
            pools = data.get("data", [])
            filtered = self._filter_pools(pools, min_tvl, chains)
            
            return self._select_diverse_strategies(filtered, limit)
            
        except requests.RequestException:
            return []
    
    def _filter_pools(
        self,
        pools: List[Dict],
        min_tvl: float,
        chains: Optional[List[str]],
    ) -> List[LiveYieldData]:
        filtered = []
        
        for pool in pools:
            tvl = pool.get("tvlUsd", 0) or 0
            apy = pool.get("apy", 0) or 0
            
            if tvl < min_tvl:
                continue
            if apy <= 0 or apy > 500:
                continue
            if chains:
                chain_lower = pool.get("chain", "").lower()
                if chain_lower not in [c.lower() for c in chains]:
                    continue
            
            yield_data = LiveYieldData(
                protocol=pool.get("project", "Unknown"),
                chain=pool.get("chain", "Unknown"),
                pool=pool.get("pool", "Unknown"),
                symbol=pool.get("symbol", "Unknown"),
                apy=apy / 100,
                tvl=tvl,
                il_risk=pool.get("ilRisk", "") == "yes",
            )
            filtered.append(yield_data)
        
        filtered.sort(key=lambda x: x.tvl, reverse=True)
        return filtered
    
    def _select_diverse_strategies(
        self,
        pools: List[LiveYieldData],
        limit: int,
    ) -> List[LiveYieldData]:
        selected: Dict[str, List[LiveYieldData]] = {
            "staking": [],
            "lending": [],
            "lp": [],
        }
        
        for pool in pools:
            pool_lower = pool.pool.lower()
            
            if len(selected["staking"]) < 2 and "stake" in pool_lower:
                selected["staking"].append(pool)
            elif len(selected["lending"]) < 2 and any(
                term in pool_lower for term in ["lend", "supply"]
            ):
                selected["lending"].append(pool)
            elif len(selected["lp"]) < 3:
                selected["lp"].append(pool)
            
            total_selected = sum(len(v) for v in selected.values())
            if total_selected >= limit:
                break
        
        result = selected["staking"] + selected["lending"] + selected["lp"]
        return result[:limit]


class LiveDataManager:
    def __init__(self) -> None:
        self._provider = DefiLlamaProvider()
        self._cached_yields: List[LiveYieldData] = []
    
    def refresh_data(
        self,
        source: str = "defillama",
        **kwargs,
    ) -> List[LiveYieldData]:
        if source == "defillama":
            self._cached_yields = self._provider.fetch_top_yields(**kwargs)
        return self._cached_yields
    
    def get_strategy_configs(self, limit: int = 5) -> List[StrategyConfig]:
        if not self._cached_yields:
            self.refresh_data(limit=limit)
        
        return [
            yield_data.to_strategy_config()
            for yield_data in self._cached_yields[:limit]
        ]
    
    def get_cached_yields(self) -> List[LiveYieldData]:
        return self._cached_yields
