import csv
import json
import os
from datetime import datetime
from typing import List

from data.models import SimulationParams, SimulationResult


class ReportExporter:
    def __init__(self, output_dir: str = "exports") -> None:
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export_csv(
        self,
        results: List[SimulationResult],
        filepath: str,
    ) -> str:
        full_path = os.path.join(self.output_dir, os.path.basename(filepath))
        
        with open(full_path, "w", newline="") as file:
            writer = csv.writer(file)
            
            writer.writerow([
                "Strategy",
                "Type",
                "APR",
                "APY",
                "Volatility",
                "Sharpe Ratio",
                "Max Drawdown",
                "VaR 95%",
                "CVaR 95%",
                "Mean Return",
                "Median Return",
            ])
            
            for result in results:
                writer.writerow([
                    result.strategy_name,
                    result.strategy_type.value,
                    "{:.6f}".format(result.apr),
                    "{:.6f}".format(result.apy),
                    "{:.6f}".format(result.volatility),
                    "{:.4f}".format(result.sharpe_ratio),
                    "{:.6f}".format(result.max_drawdown),
                    "{:.6f}".format(result.var_95),
                    "{:.6f}".format(result.cvar_95),
                    "{:.6f}".format(result.mean_return),
                    "{:.6f}".format(result.median_return),
                ])
        
        return full_path
    
    def export_json(
        self,
        results: List[SimulationResult],
        params: SimulationParams,
        filepath: str,
    ) -> str:
        full_path = os.path.join(self.output_dir, os.path.basename(filepath))
        
        export_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
            },
            "simulation_parameters": {
                "initial_capital": params.initial_capital,
                "time_horizon_days": params.time_horizon_days,
                "num_simulations": params.num_simulations,
                "risk_free_rate": params.risk_free_rate,
            },
            "results": [
                {
                    "strategy_name": r.strategy_name,
                    "strategy_type": r.strategy_type.value,
                    "yield_metrics": {
                        "apr": r.apr,
                        "apy": r.apy,
                        "mean_return": r.mean_return,
                        "median_return": r.median_return,
                    },
                    "risk_metrics": {
                        "volatility": r.volatility,
                        "sharpe_ratio": r.sharpe_ratio,
                        "max_drawdown": r.max_drawdown,
                        "var_95": r.var_95,
                        "cvar_95": r.cvar_95,
                    },
                }
                for r in results
            ],
        }
        
        with open(full_path, "w") as file:
            json.dump(export_data, file, indent=2)
        
        return full_path
    
    def export_txt_report(
        self,
        results: List[SimulationResult],
        params: SimulationParams,
        filepath: str,
    ) -> str:
        full_path = os.path.join(self.output_dir, os.path.basename(filepath))
        
        lines = self._build_report_lines(results, params)
        
        with open(full_path, "w") as file:
            file.write("\n".join(lines))
        
        return full_path
    
    def _build_report_lines(
        self,
        results: List[SimulationResult],
        params: SimulationParams,
    ) -> List[str]:
        separator = "=" * 72
        subseparator = "-" * 72
        
        lines = [
            separator,
            "DEFI YIELD AGGREGATOR SIMULATOR",
            "Analysis Report",
            separator,
            "",
            "Generated: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            "",
            "SIMULATION PARAMETERS",
            subseparator,
            "Initial Capital:     ${:>12,.2f}".format(params.initial_capital),
            "Time Horizon:        {:>12} days".format(params.time_horizon_days),
            "Monte Carlo Paths:   {:>12,}".format(params.num_simulations),
            "Risk-Free Rate:      {:>12.2f}%".format(params.risk_free_rate * 100),
            "",
            "STRATEGY PERFORMANCE",
            subseparator,
            "",
        ]
        
        for result in results:
            sharpe_display = (
                "{:.2f}".format(result.sharpe_ratio)
                if abs(result.sharpe_ratio) < 10
                else ">10" if result.sharpe_ratio > 0 else "<-10"
            )
            
            lines.extend([
                "Strategy: {}".format(result.strategy_name),
                "Type:     {}".format(result.strategy_type.value),
                "",
                "  Yield Metrics:",
                "    APR:             {:>10.2f}%".format(result.apr * 100),
                "    APY:             {:>10.2f}%".format(result.apy * 100),
                "    Mean Return:     {:>10.2f}%".format(result.mean_return * 100),
                "    Median Return:   {:>10.2f}%".format(result.median_return * 100),
                "",
                "  Risk Metrics:",
                "    Volatility:      {:>10.1f}%".format(result.volatility * 100),
                "    Max Drawdown:    {:>10.1f}%".format(result.max_drawdown * 100),
                "    Sharpe Ratio:    {:>10}".format(sharpe_display),
                "    VaR (95%):       {:>10.1f}%".format(result.var_95 * 100),
                "    CVaR (95%):      {:>10.1f}%".format(result.cvar_95 * 100),
                "",
                subseparator,
                "",
            ])
        
        lines.extend([
            "DISCLAIMER",
            subseparator,
            "This report is for research and educational purposes only.",
            "Past performance does not guarantee future results.",
            "DeFi investments carry significant risks including total loss.",
            "",
            separator,
            "END OF REPORT",
            separator,
        ])
        
        return lines
