"""Does [paid-UTM converters, all converters] / claimed conversions bracket the true deduplication factor?"""
import numpy as np
from mta_roas_deflation.market import MarketGenerator, MarketSimulator

if __name__ == "__main__":
    gen, sim = MarketGenerator(np.random.default_rng(7)), MarketSimulator()
    rows = []
    for _ in range(1000):
        m = sim.run(*gen.market())
        rows.append((m["seen_conv"] / m["claimed"], m["k_conv"], m["conv_total"] / m["claimed"]))
    a = np.array(rows)
    print("median low / true / high:", np.median(a, axis=0).round(3))
    print("coverage:", np.mean((a[:, 0] <= a[:, 1]) & (a[:, 1] <= a[:, 2])))
    print("share with high end > 1:", np.mean(a[:, 2] > 1))
