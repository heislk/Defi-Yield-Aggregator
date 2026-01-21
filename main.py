#!/usr/bin/env python3
"""
DeFi Yield Aggregator Simulator
"""

import argparse
import sys
from datetime import datetime
from typing import List

from rich.console import Console
from rich.text import Text

from cli.dashboard import Dashboard
from data.config import (
    DEFAULT_STRATEGIES,
    DEFAULT_SIMULATION_PARAMS,
    TABLE_FORMAT,
)
from data.live_provider import LiveDataManager
from data.models import SimulationResult
from simulation.monte_carlo import MonteCarloSimulator


def create_console() -> Console:
    return Console(width=120)


def print_banner(console: Console) -> None:
    banner = Text()
    banner.append("\n")
    banner.append("  ╔═══════════════════════════════════════════════════════════╗\n", style="bright_blue")
    banner.append("  ║                                                           ║\n", style="bright_blue")
    banner.append("  ║   ", style="bright_blue")
    banner.append("DEFI YIELD AGGREGATOR SIMULATOR", style="bold white")
    banner.append("                    ║\n", style="bright_blue")
    banner.append("  ║                                                           ║\n", style="bright_blue")
    banner.append("  ║   ", style="bright_blue")
    banner.append("Quantitative Research & Risk Modeling Tool", style="dim white")
    banner.append("           ║\n", style="bright_blue")
    banner.append("  ║                                                           ║\n", style="bright_blue")
    banner.append("  ╚═══════════════════════════════════════════════════════════╝\n", style="bright_blue")
    
    console.print(banner)


def format_results_table(results: List[SimulationResult]) -> str:
    lines = []
    
    header = (
        "  {:<22} {:>8} {:>8} {:>8} {:>8} {:>9} {:>8} {:>9}"
    ).format("STRATEGY", "APR", "APY", "VOL", "SHARPE", "MDD", "VaR95", "CVaR95")
    
    lines.append(header)
    lines.append("  " + "─" * 90)
    
    for result in results:
        sharpe_display = _format_ratio(result.sharpe_ratio)
        
        row = (
            "  {:<22} {:>7.2f}% {:>7.2f}% {:>7.1f}% {:>8} {:>8.1f}% {:>7.1f}% {:>8.1f}%"
        ).format(
            result.strategy_name[:22],
            result.apr * 100,
            result.apy * 100,
            result.volatility * 100,
            sharpe_display,
            result.max_drawdown * 100,
            result.var_95 * 100,
            result.cvar_95 * 100,
        )
        lines.append(row)
    
    return "\n".join(lines)


def _format_ratio(value: float) -> str:
    if abs(value) >= 10:
        return ">10" if value > 0 else "<-10"
    return "{:.2f}".format(value)


def run_quick_simulation(
    console: Console,
    use_live_data: bool = False,
    num_simulations: int = 1000,
    time_horizon: int = 180,
) -> None:
    console.print("\n  [dim white]Initializing simulation engine...[/dim white]\n")
    
    strategies = _load_strategies(console, use_live_data)
    
    sim_params = DEFAULT_SIMULATION_PARAMS
    sim_params.num_simulations = num_simulations
    sim_params.time_horizon_days = time_horizon
    
    console.print("  [bright_blue]▶[/bright_blue] [dim white]Running Monte Carlo simulation[/dim white]")
    console.print(
        "    [dim white]Paths:[/dim white] [white]{:,}[/white]  "
        "[dim white]Horizon:[/dim white] [white]{} days[/white]  "
        "[dim white]Capital:[/dim white] [white]${:,.0f}[/white]\n".format(
            num_simulations, time_horizon, sim_params.initial_capital
        )
    )
    
    simulator = MonteCarloSimulator(sim_params, seed=42)
    results = simulator.run_all_simulations(strategies)
    
    console.print("  [bright_green]✓[/bright_green] [dim white]Simulation complete[/dim white]\n")
    
    console.print("[bold white]{}[/bold white]".format(format_results_table(results)))
    console.print()


def _load_strategies(console: Console, use_live_data: bool):
    if not use_live_data:
        return DEFAULT_STRATEGIES
    
    console.print("  [bright_blue]▶[/bright_blue] [dim white]Fetching live yield data from DefiLlama[/dim white]")
    
    manager = LiveDataManager()
    manager.refresh_data(limit=5, min_tvl=10_000_000)
    strategies = manager.get_strategy_configs(limit=3)
    
    if not strategies:
        console.print("  [bright_red]✗[/bright_red] [dim white]Could not fetch live data, using defaults[/dim white]\n")
        return DEFAULT_STRATEGIES
    
    console.print("  [bright_green]✓[/bright_green] [dim white]Loaded {} live strategies[/dim white]\n".format(len(strategies)))
    
    for strategy in strategies:
        console.print(
            "    [dim white]•[/dim white] [white]{}[/white] "
            "[dim white]({})[/dim white]".format(strategy.name, strategy.strategy_type.value)
        )
    console.print()
    
    return strategies


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="DeFi Yield Aggregator Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run simulation and exit",
    )
    parser.add_argument(
        "--live", "-l",
        action="store_true",
        help="Fetch live yield data from DeFi protocols",
    )
    parser.add_argument(
        "--simulations", "-n",
        type=int,
        default=1000,
        metavar="N",
        help="Number of Monte Carlo simulations",
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=180,
        metavar="DAYS",
        help="Simulation time horizon in days",
    )
    
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    console = create_console()
    
    print_banner(console)
    
    if args.quick:
        run_quick_simulation(
            console,
            use_live_data=args.live,
            num_simulations=args.simulations,
            time_horizon=args.days,
        )
        return 0
    
    try:
        dashboard = Dashboard()
        
        if args.live:
            console.print("  [bright_blue]▶[/bright_blue] [dim white]Fetching live yield data[/dim white]")
            
            manager = LiveDataManager()
            manager.refresh_data(limit=5, min_tvl=10_000_000)
            strategies = manager.get_strategy_configs(limit=3)
            
            if strategies:
                dashboard.strategies = strategies
                console.print(
                    "  [bright_green]✓[/bright_green] "
                    "[dim white]Loaded {} live strategies[/dim white]\n".format(len(strategies))
                )
        
        if args.simulations != 1000:
            dashboard.sim_params.num_simulations = args.simulations
        if args.days != 180:
            dashboard.sim_params.time_horizon_days = args.days
        
        dashboard.run()
        
    except KeyboardInterrupt:
        console.print("\n  [dim white]Goodbye[/dim white]\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
