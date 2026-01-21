from typing import List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import numpy as np

from data.models import SimulationResult
from data.config import COLORS, BORDERS
from cli.charts import ASCIIChartRenderer


class ViewRenderer:
    def __init__(self, console: Console):
        self.console = console
        self.chart_renderer = ASCIIChartRenderer(width=60, height=12)
    
    def render_strategy_table(self, results: List[SimulationResult]) -> Table:
        table = Table(
            show_header=True,
            header_style="bold white",
            border_style=BORDERS["table"],
            expand=True,
            title="[{}]STRATEGY PERFORMANCE[/{}]".format(COLORS['header'], COLORS['header']),
            title_style=COLORS["header"],
            padding=(0, 1)
        )
        
        table.add_column("STRATEGY", style="white", width=18)
        table.add_column("APR", justify="right", style="dim white", width=8)
        table.add_column("APY", justify="right", style="dim white", width=8)
        table.add_column("VOL", justify="right", style="dim white", width=8)
        table.add_column("SHARPE", justify="right", width=8)
        table.add_column("MDD", justify="right", width=9)
        table.add_column("VaR 95", justify="right", style="dim white", width=9)
        
        for result in results:
            if result.sharpe_ratio > 1.0:
                sharpe_style = COLORS["positive"]
            elif result.sharpe_ratio > 0.5:
                sharpe_style = "white"
            else:
                sharpe_style = COLORS["negative"]
            
            if result.max_drawdown > -0.10:
                mdd_style = COLORS["positive"]
            elif result.max_drawdown > -0.25:
                mdd_style = COLORS["warning"]
            else:
                mdd_style = COLORS["negative"]
            
            sharpe_display = "{:.2f}".format(result.sharpe_ratio) if abs(result.sharpe_ratio) < 100 else ">10"
            
            table.add_row(
                result.strategy_name,
                "{:.2f}%".format(result.apr * 100),
                "{:.2f}%".format(result.apy * 100),
                "{:.1f}%".format(result.volatility * 100),
                "[{}]{}[/{}]".format(sharpe_style, sharpe_display, sharpe_style),
                "[{}]{:.1f}%[/{}]".format(mdd_style, result.max_drawdown * 100, mdd_style),
                "{:.1f}%".format(result.var_95 * 100)
            )
        
        return table
    
    def render_detailed_metrics(self, result: SimulationResult) -> Panel:
        content = Text()
        content.append("\n  Strategy: ", style="dim white")
        content.append("{}\n".format(result.strategy_name), style="bold white")
        content.append("  Type: ", style="dim white")
        content.append("{}\n\n".format(result.strategy_type.value), style="white")
        
        content.append("  YIELD METRICS\n", style="bold bright_blue")
        content.append("    APR:           {:>8.2f}%\n".format(result.apr * 100), style="white")
        content.append("    APY:           {:>8.2f}%\n".format(result.apy * 100), style="white")
        content.append("    Mean Return:   {:>8.2f}%\n".format(result.mean_return * 100), style="white")
        content.append("    Median Return: {:>8.2f}%\n\n".format(result.median_return * 100), style="white")
        
        content.append("  RISK METRICS\n", style="bold bright_blue")
        content.append("    Volatility:    {:>8.1f}%\n".format(result.volatility * 100), style="dim white")
        content.append("    Max Drawdown:  {:>8.1f}%\n".format(result.max_drawdown * 100), style="dim white")
        content.append("    VaR (95%):     {:>8.1f}%\n".format(result.var_95 * 100), style="dim white")
        content.append("    CVaR (95%):    {:>8.1f}%\n\n".format(result.cvar_95 * 100), style="dim white")
        
        content.append("  PERFORMANCE RATIOS\n", style="bold bright_blue")
        sharpe_val = "{:.2f}".format(result.sharpe_ratio) if abs(result.sharpe_ratio) < 100 else ">10"
        content.append("    Sharpe Ratio:  {:>8}\n".format(sharpe_val), style="white")
        
        return Panel(
            content, 
            title="[{}]DETAILED METRICS[/{}]".format(COLORS['header'], COLORS['header']), 
            border_style=BORDERS["panel"]
        )
    
    def render_charts_view(self, result: SimulationResult) -> None:
        median_path = np.median(result.equity_curves, axis=0)
        equity_chart = self.chart_renderer.render_equity_curve(
            median_path, 
            title="{} — Equity Curve (Median)".format(result.strategy_name)
        )
        
        histogram = self.chart_renderer.render_histogram(
            result.returns,
            title="{} — Return Distribution".format(result.strategy_name)
        )
        
        drawdown_chart = self.chart_renderer.render_drawdown_curve(
            result.drawdowns,
            title="{} — Drawdown".format(result.strategy_name)
        )
        
        self.console.print(equity_chart)
        self.console.print(histogram)
        self.console.print(drawdown_chart)
    
    def render_comparison_chart(self, results: List[SimulationResult]) -> None:
        volatilities = [r.volatility for r in results]
        returns = [r.mean_return for r in results]
        labels = [r.strategy_name for r in results]
        
        scatter = self.chart_renderer.render_risk_return_scatter(
            volatilities, returns, labels,
            title="Risk vs Return Comparison"
        )
        
        self.console.print(scatter)
    
    def render_export_confirmation(self, filepath: str, format_type: str) -> Panel:
        content = Text()
        content.append("\n  ✓ Export Successful\n\n", style="bold bright_green")
        content.append("  Format: ", style="dim white")
        content.append("{}\n".format(format_type.upper()), style="white")
        content.append("  File:   ", style="dim white")
        content.append("{}\n".format(filepath), style="bright_blue")
        
        return Panel(
            content, 
            title="[{}]EXPORT[/{}]".format(COLORS['header'], COLORS['header']), 
            border_style=BORDERS["panel"]
        )
