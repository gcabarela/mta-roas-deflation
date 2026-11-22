# MTA ROAS Deflation

Every ad platform claims the sale. Add up their conversions and you usually sold more than you did.

This repo goes with the whitepaper **"MTA ROAS Deflation: When Everyone Claims the Sale"**. It holds the 10-minute calculator in Python and the simulation behind the paper's stress test.

## The method in one line

```
deflator k   = unique converters in your web analytics / sum of conversions claimed by all platforms
deflated ROAS = platform ROAS x k
```

- **High end:** all analytics converters. **Low end:** converters with a paid-UTM session.
- **Cross-check:** backend customers should give a k within ~0.10 of the high end.
- **Optional refinement:** a per-platform deflator from the click ratio, capped to 0.8-1.25 and used only when it is stable month to month.

What it fixes: the level. What it does not fix: ranking or incrementality. Deflated ROAS is deduplicated, not incremental: it still includes baseline demand. Lift tests are the next step.

k is almost always below 1. If yours is above 1, platform tracking loss is outweighing double counting: treat it as a tracking alarm, not good news.

## Quick start

```bash
pip install -r requirements.txt
python -m examples.worked_example   # the paper's hypothetical example
python -m pytest -q
```

```python
from mta_roas_deflation import Platform, ROASDeflator

calc = ROASDeflator(
    [Platform("Search", spend=100_000, roas=6.0, claimed_conversions=6_000),
     Platform("Social", spend=150_000, roas=4.0, claimed_conversions=6_000)],
    converters_all=8_000, converters_paid=6_200)
print(calc.k_high, calc.table())
```

Prefer a spreadsheet? There is a free one with the same formulas: *(link)*.

## Reproduce the paper

| Script | What it shows | Runtime |
| --- | --- | --- |
| `examples/worked_example.py` | The hypothetical outdoor sportswear brand (§5) | instant |
| `examples/converter_range.py` | The low-high range brackets the true factor | ~5 s |
| `examples/stress_test.py` | Which deflators hold up when tracking loss and click bias go wrong (§6) | ~35 s |

The simulation uses 1,000 markets of 2M people and six platforms (two demand-capture, four demand-creation). It computes exact expectations over all 64 exposure patterns, so the only randomness is in drawing the markets (seed 7). Truth is each platform's leave-one-out incremental ROAS. The score is the share of the best possible budget-reallocation gain that each deflator captures.

## Layout

```
mta_roas_deflation/
  calculator.py    the method, for real data
  market.py        simulated markets and the reallocation score
  variants.py      the per-platform deflators compared
  stress_test.py   scenarios: tracking loss baseline / independent / reversed, click bias
examples/          scripts that reproduce the paper's numbers
tests/
```

## Caveats

Simulations show what a method does when its assumptions hold or break in the ways we chose to break them. They do not show it works on your data. Check k against your backend, and test before you trust.

## License

MIT
