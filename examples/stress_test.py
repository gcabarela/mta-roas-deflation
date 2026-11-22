"""Reproduces the whitepaper's stress-test table (about 10-20 minutes on a laptop)."""
import pandas as pd
from mta_roas_deflation.stress_test import StressTest

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    st = StressTest()
    print(st.grid().to_string())
    print("\nRole prior wrong (capture platforms 4x more incremental):")
    print(pd.DataFrame({t: st.run(t, 0.0, capture_lift_factor=4) for t in ["baseline", "independent"]}).to_string())
