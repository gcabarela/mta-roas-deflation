"""Hypothetical European outdoor sportswear brand (invented numbers, not client data)."""
import pandas as pd
from mta_roas_deflation import Platform, ROASDeflator

platforms = [
    Platform("Search", 100_000, 6.0, 6_000, 90_000, 81_000, 0.06),
    Platform("Social", 150_000, 4.0, 6_000, 70_000, 45_500, 0.09),
    Platform("Retargeting", 50_000, 9.0, 4_500, 20_000, 19_000, 0.12),
    Platform("Online video", 100_000, 2.5, 2_500, 15_000, 16_500, 0.31),
]
calc = ROASDeflator(platforms, converters_all=12_400, converters_paid=9_100, backend_customers=12_500)

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(f"k high {calc.k_high:.3f} | k low {calc.k_low:.3f} | backend {calc.k_backend:.3f} (ok: {calc.backend_ok})")
    print(calc.table()[["name", "roas", "deflated_roas", "deflated_roas_low", "factor", "k_p", "deflated_roas_capped"]].round(3).to_string(index=False))
