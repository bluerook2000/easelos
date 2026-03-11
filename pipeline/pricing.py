# pipeline/pricing.py
"""Ponoko pricing matrix — exact values from PriceEstimator.tsx."""

QUANTITY_TIERS = (1, 10, 100, 500, 1000, 10000)

# [complexity][size][quantity] -> USD per part
_PRICE_MATRIX: dict[str, dict[str, dict[int, float]]] = {
    "simple": {
        "small":  {1: 12.88, 10: 2.34, 100: 0.85, 500: 0.57, 1000: 0.52, 10000: 0.36},
        "medium": {1: 14.70, 10: 3.71, 100: 1.80, 500: 1.44, 1000: 1.24, 10000: 0.80},
        "large":  {1: 17.57, 10: 4.80, 100: 3.16, 500: 2.47, 1000: 2.29, 10000: 1.43},
    },
    "moderate": {
        "small":  {1: 13.55, 10: 3.02, 100: 1.01, 500: 0.81, 1000: 0.71, 10000: 0.46},
        "medium": {1: 16.05, 10: 3.98, 100: 2.36, 500: 1.81, 1000: 1.61, 10000: 0.96},
        "large":  {1: 19.59, 10: 6.03, 100: 3.92, 500: 3.00, 1000: 2.79, 10000: 1.59},
    },
    "heavy": {
        "small":  {1: 20.22, 10: 6.64, 100: 3.45, 500: 2.47, 1000: 2.15, 10000: 1.07},
        "medium": {1: 29.42, 10: 9.47, 100: 6.33, 500: 4.70, 1000: 4.02, 10000: 1.93},
        "large":  {1: 30.39, 10: 14.13, 100: 9.71, 500: 6.92, 1000: 5.88, 10000: 3.15},
    },
}


def get_complexity(hole_count: int) -> str:
    """Classify part complexity by hole count."""
    if hole_count <= 2:
        return "simple"
    if hole_count <= 8:
        return "moderate"
    return "heavy"


def get_size_category(width_in: float, height_in: float) -> str:
    """Classify part size by area in square inches."""
    area = width_in * height_in
    if area <= 6:
        return "small"
    if area <= 24:
        return "medium"
    return "large"


def get_price_per_part(complexity: str, size: str, quantity: int) -> float:
    """Look up price per part from the Ponoko matrix."""
    return _PRICE_MATRIX[complexity][size][quantity]


def get_all_prices(
    hole_count: int,
    width_in: float,
    height_in: float,
) -> dict[int, float]:
    """Get prices for all quantity tiers given part specs."""
    complexity = get_complexity(hole_count)
    size = get_size_category(width_in, height_in)
    return {qty: _PRICE_MATRIX[complexity][size][qty] for qty in QUANTITY_TIERS}
