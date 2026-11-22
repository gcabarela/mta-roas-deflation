"""The 10-minute method: reconcile platform-claimed conversions with analytics converters."""
from dataclasses import dataclass
from typing import Optional, Sequence
import numpy as np
import pandas as pd


@dataclass
class Platform:
    name: str
    spend: float
    roas: float
    claimed_conversions: float
    click_users: Optional[float] = None
    utm_users: Optional[float] = None
    monthly_variation: Optional[float] = None

    @property
    def click_ratio(self):
        if self.click_users and self.utm_users:
            return self.utm_users / self.click_users
        return None


class ROASDeflator:
    BACKEND_GAP = 0.10

    def __init__(self, platforms: Sequence[Platform], converters_all: float, converters_paid: float,
                 backend_customers: Optional[float] = None, cap=(0.8, 1.25), tolerance=0.20):
        self.platforms, self.cap, self.tolerance = list(platforms), cap, tolerance
        self.converters_all, self.converters_paid, self.backend_customers = converters_all, converters_paid, backend_customers

    @property
    def claimed(self):
        return sum(p.claimed_conversions for p in self.platforms)

    @property
    def k_high(self):
        return self.converters_all / self.claimed

    @property
    def k_low(self):
        return self.converters_paid / self.claimed

    @property
    def k_backend(self):
        return None if self.backend_customers is None else self.backend_customers / self.claimed

    @property
    def backend_ok(self):
        return None if self.k_backend is None else abs(self.k_backend - self.k_high) <= self.BACKEND_GAP

    def factors(self):
        r = np.array([p.click_ratio or np.nan for p in self.platforms], dtype=float)
        rho = r / np.exp(np.nanmean(np.log(r))) if np.isfinite(r).any() else r
        stable = np.array([p.monthly_variation is not None and p.monthly_variation <= self.tolerance
                           for p in self.platforms])
        return np.where(stable & np.isfinite(rho), np.clip(rho, *self.cap), 1.0)

    def table(self) -> pd.DataFrame:
        d = pd.DataFrame([vars(p) for p in self.platforms])
        c = d.claimed_conversions
        d["deflated_roas"], d["deflated_roas_low"] = d.roas * self.k_high, d.roas * self.k_low
        d["factor"] = self.factors()
        d["k_p"] = self.k_high * d.factor * c.sum() / (d.factor * c).sum()
        d["deflated_roas_capped"] = d.roas * d.k_p
        return d
