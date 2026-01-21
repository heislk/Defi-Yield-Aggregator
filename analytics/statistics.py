from typing import Dict, List, Optional, Tuple

import numpy as np


def calculate_percentiles(
    data: np.ndarray,
    percentiles: Optional[List[int]] = None,
) -> Dict[int, float]:
    if percentiles is None:
        percentiles = [5, 25, 50, 75, 95]
    
    return {p: float(np.percentile(data, p)) for p in percentiles}


def calculate_distribution_stats(data: np.ndarray) -> Dict[str, float]:
    return {
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "skewness": _calculate_skewness(data),
        "kurtosis": _calculate_kurtosis(data),
    }


def _calculate_skewness(data: np.ndarray) -> float:
    n = len(data)
    mean = np.mean(data)
    std = np.std(data)
    
    if std == 0:
        return 0.0
    
    skew = np.sum(((data - mean) / std) ** 3) / n
    return float(skew)


def _calculate_kurtosis(data: np.ndarray) -> float:
    n = len(data)
    mean = np.mean(data)
    std = np.std(data)
    
    if std == 0:
        return 0.0
    
    kurt = np.sum(((data - mean) / std) ** 4) / n - 3
    return float(kurt)


def create_histogram_bins(
    data: np.ndarray,
    num_bins: int = 20,
) -> Tuple[np.ndarray, np.ndarray]:
    return np.histogram(data, bins=num_bins)


def calculate_tail_risk(
    returns: np.ndarray,
    threshold: float = -0.10,
) -> Dict[str, float]:
    tail_returns = returns[returns < threshold]
    
    return {
        "tail_count": len(tail_returns),
        "tail_probability": len(tail_returns) / len(returns) if len(returns) > 0 else 0.0,
        "tail_mean": float(np.mean(tail_returns)) if len(tail_returns) > 0 else 0.0,
        "tail_min": float(np.min(tail_returns)) if len(tail_returns) > 0 else 0.0,
    }


def rolling_statistics(
    data: np.ndarray,
    window: int,
) -> Tuple[np.ndarray, np.ndarray]:
    n = len(data)
    
    if n < window:
        return np.array([]), np.array([])
    
    output_length = n - window + 1
    rolling_mean = np.zeros(output_length)
    rolling_std = np.zeros(output_length)
    
    for i in range(output_length):
        window_data = data[i : i + window]
        rolling_mean[i] = np.mean(window_data)
        rolling_std[i] = np.std(window_data)
    
    return rolling_mean, rolling_std
