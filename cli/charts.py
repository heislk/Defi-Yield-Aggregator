from typing import List, Optional, Dict

import numpy as np
from rich.panel import Panel

from data.config import COLORS, BORDERS


class ASCIIChartRenderer:
    def __init__(self, width: int = 60, height: int = 15):
        self.width = width
        self.height = height
    
    def render_equity_curve(
        self, 
        data: np.ndarray, 
        title: str = "Equity Curve",
        percentile_paths: Optional[Dict] = None
    ) -> Panel:
        if percentile_paths is not None:
            median = percentile_paths.get(50, data)
        else:
            median = data
        
        sampled = self._sample_data(median, self.width)
        
        min_val = np.min(sampled)
        max_val = np.max(sampled)
        value_range = max_val - min_val if max_val > min_val else 1
        
        lines = []
        for row in range(self.height, 0, -1):
            threshold = min_val + value_range * row / self.height
            prev_threshold = min_val + value_range * (row - 1) / self.height
            line = ""
            for val in sampled:
                if val >= threshold:
                    line += "█"
                elif val >= prev_threshold:
                    line += "▄"
                else:
                    line += " "
            
            if row == self.height:
                label = "${:>9,.0f}".format(max_val)
            elif row == self.height // 2:
                mid_val = (max_val + min_val) / 2
                label = "${:>9,.0f}".format(mid_val)
            elif row == 1:
                label = "${:>9,.0f}".format(min_val)
            else:
                label = " " * 10
            
            lines.append("[dim white]{}[/dim white] [dim]│[/dim][{}]{}[/{}][dim]│[/dim]".format(
                label, COLORS['chart_equity'], line, COLORS['chart_equity']
            ))
        
        x_axis = " " * 11 + "[dim]└" + "─" * self.width + "┘[/dim]"
        lines.append(x_axis)
        
        n_days = len(data) - 1 if len(data) > 1 else 1
        lines.append("[dim white]{:^11}{:^{}}{:>{}}[/dim white]".format(
            'Day 0', 'Day ' + str(n_days//2), self.width//2, 'Day ' + str(n_days), self.width//2
        ))
        
        chart_text = "\n".join(lines)
        
        return Panel(
            chart_text, 
            title="[{}]{}[/{}]".format(COLORS['header'], title, COLORS['header']), 
            border_style=BORDERS["chart"],
            padding=(0, 1)
        )
    
    def render_histogram(
        self, 
        data: np.ndarray, 
        title: str = "Return Distribution",
        num_bins: int = 15
    ) -> Panel:
        counts, bin_edges = np.histogram(data, bins=num_bins)
        max_count = max(counts) if max(counts) > 0 else 1
        
        bar_width = self.width - 10
        
        lines = []
        for i in range(len(counts)):
            bin_center = (bin_edges[i] + bin_edges[i + 1]) / 2
            bar_length = int((counts[i] / max_count) * bar_width)
            
            if bin_center < 0:
                color = COLORS["chart_histogram_neg"]
            else:
                color = COLORS["chart_histogram_pos"]
            
            bar = "█" * bar_length
            label = "{:>+6.1f}%".format(bin_center * 100)
            lines.append("[dim white]{}[/dim white] [dim]│[/dim][{}]{}[/{}]".format(
                label, color, bar, color
            ))
        
        chart_text = "\n".join(lines)
        
        return Panel(
            chart_text, 
            title="[{}]{}[/{}]".format(COLORS['header'], title, COLORS['header']), 
            border_style=BORDERS["chart"],
            padding=(0, 1)
        )
    
    def render_drawdown_curve(
        self, 
        drawdowns: np.ndarray, 
        title: str = "Drawdown Curve"
    ) -> Panel:
        if drawdowns.ndim > 1:
            mean_dd = np.mean(drawdowns, axis=0)
        else:
            mean_dd = drawdowns
        
        sampled = self._sample_data(mean_dd, self.width)
        
        min_val = np.min(sampled)
        max_val = min(0, np.max(sampled))
        value_range = abs(min_val - max_val) if min_val != max_val else 0.01
        
        lines = []
        for row in range(self.height, 0, -1):
            threshold = max_val - value_range * (self.height - row) / self.height
            line = ""
            for val in sampled:
                if val <= threshold:
                    line += "█"
                else:
                    line += " "
            
            if row == self.height:
                label = "{:>+7.1f}%".format(max_val * 100)
            elif row == 1:
                label = "{:>+7.1f}%".format(min_val * 100)
            else:
                label = " " * 8
            
            lines.append("[dim white]{}[/dim white] [dim]│[/dim][{}]{}[/{}][dim]│[/dim]".format(
                label, COLORS['chart_drawdown'], line, COLORS['chart_drawdown']
            ))
        
        x_axis = " " * 9 + "[dim]└" + "─" * self.width + "┘[/dim]"
        lines.append(x_axis)
        
        chart_text = "\n".join(lines)
        
        return Panel(
            chart_text, 
            title="[{}]{}[/{}]".format(COLORS['header'], title, COLORS['header']), 
            border_style=BORDERS["chart"],
            padding=(0, 1)
        )
    
    def render_risk_return_scatter(
        self, 
        volatilities: List[float],
        returns: List[float],
        labels: List[str],
        title: str = "Risk vs Return"
    ) -> Panel:
        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        vol_margin = 0.1
        ret_margin = 0.1
        
        min_vol = min(volatilities) * (1 - vol_margin)
        max_vol = max(volatilities) * (1 + vol_margin)
        min_ret = min(returns) - abs(min(returns)) * ret_margin
        max_ret = max(returns) + abs(max(returns)) * ret_margin
        
        vol_range = max_vol - min_vol if max_vol > min_vol else 0.01
        ret_range = max_ret - min_ret if max_ret > min_ret else 0.01
        
        markers = ['●', '■', '▲', '◆', '★']
        colors = COLORS["chart_scatter"]
        
        legend = []
        for i, (vol, ret, label) in enumerate(zip(volatilities, returns, labels)):
            x = int((vol - min_vol) / vol_range * (self.width - 1))
            y = int((ret - min_ret) / ret_range * (self.height - 1))
            
            x = max(0, min(self.width - 1, x))
            y = max(0, min(self.height - 1, y))
            
            canvas[self.height - 1 - y][x] = markers[i % len(markers)]
            short_label = label[:12] + "..." if len(label) > 15 else label
            legend.append("[{}]{}[/{}] {}".format(
                colors[i % len(colors)], markers[i % len(markers)], colors[i % len(colors)], short_label
            ))
        
        lines = []
        for row_idx, row in enumerate(canvas):
            if row_idx == 0:
                label = "{:>+6.1f}%".format(max_ret * 100)
            elif row_idx == self.height - 1:
                label = "{:>+6.1f}%".format(min_ret * 100)
            else:
                label = " " * 7
            
            row_content = ""
            for char_idx, char in enumerate(row):
                if char != ' ':
                    for idx, (vol, ret, _) in enumerate(zip(volatilities, returns, labels)):
                        x = int((vol - min_vol) / vol_range * (self.width - 1))
                        y = int((ret - min_ret) / ret_range * (self.height - 1))
                        x = max(0, min(self.width - 1, x))
                        y = max(0, min(self.height - 1, y))
                        if self.height - 1 - y == row_idx and x == char_idx:
                            row_content += "[{}]{}[/{}]".format(
                                colors[idx % len(colors)], char, colors[idx % len(colors)]
                            )
                            break
                else:
                    row_content += char
            
            lines.append("[dim white]{}[/dim white] [dim]│[/dim]{}[dim]│[/dim]".format(label, row_content))
        
        x_axis = " " * 8 + "[dim]└" + "─" * self.width + "┘[/dim]"
        lines.append(x_axis)
        lines.append("[dim white]        {:.0f}%{}{}%[/dim white]".format(
            min_vol * 100, ' ' * (self.width - 8), max_vol * 100
        ))
        lines.append("[dim white]        {:^{}}[/dim white]".format('Annualized Volatility', self.width))
        lines.append("")
        lines.append("[dim white]  " + "   ".join(legend) + "[/dim white]")
        
        chart_text = "\n".join(lines)
        
        return Panel(
            chart_text, 
            title="[{}]{}[/{}]".format(COLORS['header'], title, COLORS['header']), 
            border_style=BORDERS["chart"],
            padding=(0, 1)
        )
    
    def _sample_data(self, data: np.ndarray, target_size: int) -> np.ndarray:
        if len(data) <= target_size:
            return data
        
        indices = np.linspace(0, len(data) - 1, target_size).astype(int)
        return data[indices]
