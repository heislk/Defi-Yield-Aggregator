import sys
from datetime import datetime
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from data.config import DEFAULT_STRATEGIES, DEFAULT_SIMULATION_PARAMS, APP_CONFIG, COLORS, BORDERS
from data.models import SimulationParams, SimulationResult
from simulation.monte_carlo import MonteCarloSimulator
from cli.views import ViewRenderer
from cli.charts import ASCIIChartRenderer
from reports.exporter import ReportExporter


class Dashboard:
    def __init__(self):
        self.console = Console()
        self.view_renderer = ViewRenderer(self.console)
        self.chart_renderer = ASCIIChartRenderer()
        self.exporter = ReportExporter()
        
        self.strategies = DEFAULT_STRATEGIES
        self.sim_params = DEFAULT_SIMULATION_PARAMS
        self.results: List[SimulationResult] = []
        
        self.current_view = "main"
        self.selected_strategy_idx = 0
        self.running = True
    
    def render_header(self) -> Panel:
        header_text = Text()
        header_text.append("  {} ".format(APP_CONFIG['app_name']), style="bold white")
        header_text.append("v{}\n".format(APP_CONFIG['version']), style="dim white")
        header_text.append("  MODE ", style="dim white")
        header_text.append("{}".format(APP_CONFIG['mode']), style="bright_blue")
        header_text.append("        DATE ", style="dim white")
        header_text.append(datetime.now().strftime("%Y-%m-%d"), style="white")
        
        return Panel(header_text, border_style=BORDERS["main"], padding=(0, 1))
    
    def render_menu(self) -> Panel:
        menu = Text()
        menu.append("\n")
        
        if self.current_view == "main":
            menu.append("  [", style="dim white")
            menu.append("1", style="bright_blue")
            menu.append("] View Charts   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("2", style="bright_blue")
            menu.append("] Run Simulation   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("3", style="bright_blue")
            menu.append("] Export   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("Q", style="bright_red")
            menu.append("] Quit\n", style="dim white")
            menu.append("\n  [", style="dim white")
            menu.append("↑/↓", style="bright_blue")
            menu.append("] Select   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("ENTER", style="bright_blue")
            menu.append("] Details", style="dim white")
        elif self.current_view == "charts":
            menu.append("  [", style="dim white")
            menu.append("1-3", style="bright_blue")
            menu.append("] Select Strategy   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("C", style="bright_blue")
            menu.append("] Comparison   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("ESC", style="bright_red")
            menu.append("] Back", style="dim white")
        elif self.current_view == "export":
            menu.append("  [", style="dim white")
            menu.append("1", style="bright_blue")
            menu.append("] CSV   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("2", style="bright_blue")
            menu.append("] JSON   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("3", style="bright_blue")
            menu.append("] TXT Report   ", style="dim white")
            menu.append("[", style="dim white")
            menu.append("ESC", style="bright_red")
            menu.append("] Back", style="dim white")
        else:
            menu.append("  [", style="dim white")
            menu.append("ESC", style="bright_red")
            menu.append("] Back to Main", style="dim white")
        
        return Panel(menu, title="[{}]CONTROLS[/{}]".format(COLORS['header'], COLORS['header']), border_style=BORDERS["menu"])
    
    def render_main_view(self) -> None:
        self.console.clear()
        self.console.print(self.render_header())
        
        if self.results:
            self.console.print(self.view_renderer.render_strategy_table(self.results))
            
            selected = self.results[self.selected_strategy_idx]
            self.console.print("\n  [bright_blue]▶[/bright_blue] [dim white]Selected:[/dim white] [white]{}[/white]\n".format(selected.strategy_name))
        else:
            self.console.print(Panel(
                "\n  [dim white]No simulation results. Press [bright_blue][2][/bright_blue] to run simulation.[/dim white]\n",
                title="[{}]STRATEGIES[/{}]".format(COLORS['header'], COLORS['header']),
                border_style=BORDERS["panel"]
            ))
        
        self.console.print(self.render_menu())
    
    def render_charts_view(self) -> None:
        self.console.clear()
        self.console.print(self.render_header())
        
        if not self.results:
            self.console.print(Panel(
                "\n  [dim white]No results to display. Run a simulation first.[/dim white]\n",
                border_style=BORDERS["panel"]
            ))
        else:
            selected = self.results[self.selected_strategy_idx]
            self.view_renderer.render_charts_view(selected)
        
        self.console.print(self.render_menu())
    
    def render_comparison_view(self) -> None:
        self.console.clear()
        self.console.print(self.render_header())
        
        if self.results:
            self.view_renderer.render_comparison_chart(self.results)
        
        self.console.print(self.render_menu())
    
    def render_export_view(self) -> None:
        self.console.clear()
        self.console.print(self.render_header())
        export_text = Text()
        export_text.append("\n  Select export format:\n\n", style="white")
        export_text.append("  [", style="dim white")
        export_text.append("1", style="bright_blue")
        export_text.append("] CSV  — Raw simulation data\n", style="dim white")
        export_text.append("  [", style="dim white")
        export_text.append("2", style="bright_blue")
        export_text.append("] JSON — Structured results\n", style="dim white")
        export_text.append("  [", style="dim white")
        export_text.append("3", style="bright_blue")
        export_text.append("] TXT  — Summary report\n", style="dim white")
        
        self.console.print(Panel(
            export_text,
            title="[{}]EXPORT OPTIONS[/{}]".format(COLORS['header'], COLORS['header']),
            border_style=BORDERS["panel"]
        ))
        self.console.print(self.render_menu())
    
    def run_simulation(self) -> None:
        self.console.clear()
        self.console.print(self.render_header())
        
        sim_info = Text()
        sim_info.append("\n  Running Monte Carlo Simulation...\n\n", style="bold white")
        sim_info.append("  Paths:        ", style="dim white")
        sim_info.append("{:,}\n".format(self.sim_params.num_simulations), style="white")
        sim_info.append("  Horizon:      ", style="dim white")
        sim_info.append("{} days\n".format(self.sim_params.time_horizon_days), style="white")
        sim_info.append("  Capital:      ", style="dim white")
        sim_info.append("${:,.0f}\n".format(self.sim_params.initial_capital), style="white")
        
        self.console.print(Panel(sim_info, title="[{}]SIMULATION[/{}]".format(COLORS['header'], COLORS['header']), border_style=BORDERS["main"]))
        
        simulator = MonteCarloSimulator(self.sim_params, seed=42)
        self.results = []
        
        for strategy in self.strategies:
            self.console.print("  [bright_blue]▶[/bright_blue] [dim white]Simulating:[/dim white] [white]{}[/white]".format(strategy.name))
            result = simulator.run_simulation(strategy)
            self.results.append(result)
            sharpe_display = "{:.2f}".format(result.sharpe_ratio) if abs(result.sharpe_ratio) < 100 else ">10"
            self.console.print("    [bright_green]✓[/bright_green] [dim white]Sharpe:[/dim white] [white]{}[/white]  [dim white]MDD:[/dim white] [white]{:.1f}%[/white]".format(sharpe_display, result.max_drawdown*100))
        
        self.console.print("\n  [bright_green]✓[/bright_green] [white]Simulation complete[/white]\n")
        self.console.print("  [dim white]Press any key...[/dim white]")
        self._wait_for_key()
    
    def export_results(self, format_type: str) -> None:
        if not self.results:
            self.console.print(Panel(
                "\n  [bright_red]No results to export. Run a simulation first.[/bright_red]\n",
                border_style=BORDERS["panel"]
            ))
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "csv":
            filepath = "exports/simulation_{}.csv".format(timestamp)
            self.exporter.export_csv(self.results, filepath)
        elif format_type == "json":
            filepath = "exports/simulation_{}.json".format(timestamp)
            self.exporter.export_json(self.results, self.sim_params, filepath)
        elif format_type == "txt":
            filepath = "exports/report_{}.txt".format(timestamp)
            self.exporter.export_txt_report(self.results, self.sim_params, filepath)
        
        self.console.print(self.view_renderer.render_export_confirmation(filepath, format_type))
        self.console.print("\n  [dim white]Press any key...[/dim white]")
        self._wait_for_key()
    
    def _wait_for_key(self) -> str:
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def handle_input(self) -> None:
        key = self._wait_for_key()
        
        if self.current_view == "main":
            if key == "1" and self.results:
                self.current_view = "charts"
            elif key == "2":
                self.run_simulation()
            elif key == "3":
                self.current_view = "export"
            elif key.lower() == "q":
                self.running = False
            elif key == "\x1b":
                next_chars = self._wait_for_key() + self._wait_for_key()
                if next_chars == "[A":
                    self.selected_strategy_idx = max(0, self.selected_strategy_idx - 1)
                elif next_chars == "[B":
                    self.selected_strategy_idx = min(len(self.results) - 1, self.selected_strategy_idx + 1) if self.results else 0
        
        elif self.current_view == "charts":
            if key in "123" and self.results:
                idx = int(key) - 1
                if idx < len(self.results):
                    self.selected_strategy_idx = idx
            elif key.lower() == "c":
                self.render_comparison_view()
                self._wait_for_key()
            elif key == "\x1b" or key.lower() == "b":
                self.current_view = "main"
        
        elif self.current_view == "export":
            if key == "1":
                self.export_results("csv")
            elif key == "2":
                self.export_results("json")
            elif key == "3":
                self.export_results("txt")
            elif key == "\x1b" or key.lower() == "b":
                self.current_view = "main"
    
    def run(self) -> None:
        try:
            while self.running:
                if self.current_view == "main":
                    self.render_main_view()
                elif self.current_view == "charts":
                    self.render_charts_view()
                elif self.current_view == "export":
                    self.render_export_view()
                
                self.handle_input()
        except KeyboardInterrupt:
            pass
        finally:
            self.console.clear()
            self.console.print("\n  [dim white]Thank you for using DeFi Yield Aggregator Simulator[/dim white]\n")
