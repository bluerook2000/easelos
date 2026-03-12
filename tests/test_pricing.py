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


def test_size_boundary_small_to_medium():
    # exactly 6 sq in is small; 6.01 sq in is medium
    assert get_size_category(2.0, 3.0) == "small"
    assert get_size_category(2.0, 3.005) == "medium"  # 6.01 sq in


def test_size_boundary_medium_to_large():
    # exactly 24 sq in is medium; 24.01 sq in is large
    assert get_size_category(4.0, 6.0) == "medium"
    assert get_size_category(4.0, 6.0025) == "large"  # 24.01 sq in


def test_price_spot_checks():
    assert get_price_per_part("simple", "small", 1) == 12.88
    assert get_price_per_part("heavy", "large", 10000) == 3.15
    assert get_price_per_part("moderate", "medium", 100) == 2.36


def test_get_all_prices_returns_all_6_tiers():
    prices = get_all_prices(hole_count=4, width_in=3.0, height_in=2.0)
    assert len(prices) == 6
    assert prices[1] == 13.55    # moderate, small, qty 1
    assert prices[10000] == 0.46  # moderate, small, qty 10000
    for tier in QUANTITY_TIERS:
        assert tier in prices
        assert isinstance(prices[tier], float)
        assert prices[tier] > 0


def test_material_multiplier_titanium():
    """Titanium prices are 4x aluminum base."""
    base = get_all_prices(2, 1.0, 1.0)  # simple, small
    ti = get_all_prices(2, 1.0, 1.0, material_multiplier=4.0)
    for qty in base:
        assert ti[qty] == round(base[qty] * 4.0, 2)


def test_process_multiplier_cnc():
    """CNC prices are 2.5x base."""
    base = get_all_prices(2, 1.0, 1.0)
    cnc = get_all_prices(2, 1.0, 1.0, process_multiplier=2.5)
    for qty in base:
        assert cnc[qty] == round(base[qty] * 2.5, 2)


def test_combined_multipliers():
    """Material and process multipliers stack multiplicatively."""
    base = get_all_prices(2, 1.0, 1.0)
    combined = get_all_prices(2, 1.0, 1.0, material_multiplier=2.0, process_multiplier=1.5)
    for qty in base:
        assert combined[qty] == round(base[qty] * 2.0 * 1.5, 2)


def test_default_multipliers_unchanged():
    """Without multipliers, prices are identical to before."""
    prices = get_all_prices(2, 1.0, 1.0)
    assert prices[1] == 12.88  # simple/small/1 — exact Ponoko value
