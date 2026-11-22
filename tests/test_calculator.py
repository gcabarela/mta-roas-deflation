import numpy as np
import pytest
from mta_roas_deflation import Platform, ROASDeflator
from examples.worked_example import calc


def test_worked_example():
    t = calc.table()
    assert calc.k_high == pytest.approx(0.6526, abs=1e-4)
    assert calc.k_low == pytest.approx(0.4789, abs=1e-4)
    assert calc.backend_ok
    assert t.k_p.round(3).tolist() == [0.692, 0.544, 0.730, 0.680]


def test_capped_deflators_add_up_to_analytics_converters():
    t = calc.table()
    assert (t.k_p * t.claimed_conversions).sum() == pytest.approx(calc.converters_all)


def test_uniform_k_keeps_ranking():
    t = calc.table()
    assert (np.argsort(t.roas) == np.argsort(t.deflated_roas)).all()


def test_unstable_or_missing_ratio_gets_factor_one():
    ps = [Platform("A", 1, 2, 100, 100, 50, 0.5), Platform("B", 1, 2, 100), Platform("C", 1, 2, 100, 100, 90, 0.1)]
    f = ROASDeflator(ps, 200, 150).factors()
    assert f[0] == 1.0 and f[1] == 1.0
