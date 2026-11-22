"""Share of the oracle reallocation gain each deflator captures, under tracking and bias scenarios."""
import numpy as np
import pandas as pd
from .market import MarketGenerator, MarketSimulator, ReallocationDecision
from .variants import Deflators


class StressTest:
    def __init__(self, n_markets=1000, seed=7):
        self.n, self.seed, self.sim = n_markets, seed, MarketSimulator()

    def run(self, tracking="baseline", click_bias_sd=0.0, capture_lift_factor=1.0) -> pd.Series:
        rng = np.random.default_rng(self.seed)
        gen = MarketGenerator(rng, tracking, capture_lift_factor)
        gain, oracle = {}, 0.0
        for _ in range(self.n):
            m = self.sim.run(*gen.market())
            bias = np.exp(rng.normal(0, click_bias_sd, len(m["roles"]))) if click_bias_sd else np.ones(len(m["roles"]))
            for name, kp in Deflators.build(m, bias).items():
                g, o = ReallocationDecision.captured(m["raw"] * kp, m["iroas"])
                gain[name] = gain.get(name, 0.0) + g
            oracle += o
        return (pd.Series(gain) / oracle).round(3)

    def grid(self):
        cols = {f"{t} | bias {b}": self.run(t, b) for t in ["baseline", "independent", "reversed"] for b in [0.0, 0.3]}
        out = pd.DataFrame(cols)
        out["mean"] = out.mean(axis=1).round(3)
        return out
