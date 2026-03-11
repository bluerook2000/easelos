# tests/test_pricing.py
from pipeline.pricing import (
    get_complexity,
    get_size_category,
    get_price_per_part,
    get_all_prices,
    QUANTITY_TIERS,
)


def test_complexity_simple():
    assert get_complexity(0) == "simple"
    assert get_complexity(1) == "simple"
    assert get_complexity(2) == "simple"


def test_complexity_moderate():
    assert get_complexity(3) == "moderate"
    assert get_complexity(8) == "moderate"


def test_complexity_heavy():
    assert get_complexity(9) == "heavy"
    assert get_complexity(50) == "heavy"


def test_size_small():
    # 2" x 3" = 6 sq in
    assert get_size_category(2.0, 3.0) == "small"


def test_size_medium():
    # 4" x 4" = 16 sq in
    assert get_size_category(4.0, 4.0) == "medium"


def test_size_large():
    # 5" x 5" = 25 sq in
    assert get_size_category(5.0, 5.0) == "large"


def test_size_boundary_small():
    # exactly 6 sq in is small
    assert get_size_category(2.0, 3.0) == "small"


def test_size_boundary_medium():
    # exactly 24 sq in is medium
    assert get_size_category(4.0, 6.0) == "medium"


def test_price_simple_small_qty1():
    assert get_price_per_part("simple", "small", 1) == 12.88


def test_price_heavy_large_qty10000():
    assert get_price_per_part("heavy", "large", 10000) == 3.15


def test_price_moderate_medium_qty100():
    assert get_price_per_part("moderate", "medium", 100) == 2.36


def test_get_all_prices():
    prices = get_all_prices(hole_count=4, width_in=3.0, height_in=2.0)
    assert len(prices) == 6
    assert prices[1] == 13.55    # moderate, small, qty 1
    assert prices[10000] == 0.46  # moderate, small, qty 10000


def test_quantity_tiers():
    assert QUANTITY_TIERS == (1, 10, 100, 500, 1000, 10000)


def test_get_all_prices_returns_all_tiers():
    prices = get_all_prices(hole_count=0, width_in=1.0, height_in=1.0)
    for tier in QUANTITY_TIERS:
        assert tier in prices
        assert isinstance(prices[tier], float)
        assert prices[tier] > 0
