"""Simulated market: exact expectations over the 2^P exposure patterns of a population on an intent grid."""
import itertools
from dataclasses import dataclass
import numpy as np

ROLES = ["capture", "capture", "creation", "creation", "creation", "creation"]
NAMES = ["Search", "Retargeting", "Social", "Short video", "Online video", "Display"]


@dataclass
class PlatformSpec:
    name: str
    role: str
    spend: float
    reach_a: float
    reach_b: float
    reach_k: float
    visit_lift: float
    conv_lift: float
    claim_rate: float
    visibility: float = 1.0

    def reach(self, z):
        return np.clip(self.reach_a + self.reach_b * z ** self.reach_k, 0.0, 0.95)


class MarketGenerator:
    VISIBILITY = {"capture": (0.6, 0.95), "creation": (0.15, 0.6)}

    def __init__(self, rng, tracking="baseline", capture_lift_factor=1.0):
        self.rng, self.tracking, self.capture_lift = rng, tracking, capture_lift_factor

    def platform(self, name, role):
        u = self.rng.uniform
        lu = lambda a, b: float(np.exp(u(np.log(a), np.log(b))))
        if role == "capture":
            p = PlatformSpec(name, role, lu(1e5, 4e5), u(0.0, 0.05), u(0.4, 0.9), u(2, 4),
                             u(0.05, 0.15), lu(0.001, 0.02), u(0.75, 0.95))
        else:
            p = PlatformSpec(name, role, lu(1e5, 5e5), u(0.1, 0.5), u(-0.3, 0.3), 1.0,
                             u(0.01, 0.06), lu(0.003, 0.02), u(0.4, 0.85))
        p.visibility = float(u(*self.VISIBILITY[role]))
        if self.tracking == "independent":
            p.claim_rate = float(u(0.4, 0.95))
        elif self.tracking == "reversed":
            p.claim_rate = float(u(0.4, 0.85) if role == "capture" else u(0.75, 0.95))
        if role == "capture":
            p.conv_lift *= self.capture_lift
        return p

    def market(self):
        base_strength = self.rng.uniform(0.02, 0.10)
        return base_strength, [self.platform(n, r) for n, r in zip(NAMES, ROLES)]


class MarketSimulator:
    def __init__(self, n_bins=50, population=2_000_000, aov=60.0):
        self.z = np.linspace(0, 1, n_bins)
        self.w = np.full(n_bins, population / n_bins)
        self.aov = aov

    @staticmethod
    def combine(base, lifts, e):
        miss = 1 - base
        for lift, x in zip(lifts, e):
            miss = miss * (1 - lift * x)
        return 1 - miss

    def run(self, base_strength, ps):
        z, P = self.z, len(ps)
        base_visit, base_conv = 0.02 + 0.25 * z ** 2, 0.002 + base_strength * z ** 3
        reach = np.array([p.reach(z) for p in ps])
        vl, cl = [p.visit_lift for p in ps], [p.conv_lift for p in ps]
        cr, vis = np.array([p.claim_rate for p in ps]), np.array([p.visibility for p in ps])
        o = {k: np.zeros(P) for k in ["claim", "incr", "platform_uu", "exposed_visitors"]}
        o.update(conv_total=0.0, conv_paid=0.0, seen_conv=0.0, web_all=0.0)
        for e in itertools.product([0, 1], repeat=P):
            e = np.array(e)
            n = self.w * np.prod(np.where(e[:, None] == 1, reach, 1 - reach), axis=0)
            pc = self.combine(base_conv, cl, e)
            conv, visits = (n * pc).sum(), (n * self.combine(base_visit, vl, e)).sum()
            o["conv_total"] += conv
            o["web_all"] += visits
            idx = np.where(e == 1)[0]
            if not len(idx):
                continue
            o["conv_paid"] += conv
            o["seen_conv"] += conv * (1 - np.prod(1 - vis[idx]))
            o["claim"] += e * cr * conv
            o["platform_uu"] += e * cr * visits
            o["exposed_visitors"] += e * visits
            for i in idx:
                e0 = e.copy(); e0[i] = 0
                o["incr"][i] += (n * (pc - self.combine(base_conv, cl, e0))).sum()
        spend = np.array([p.spend for p in ps])
        return dict(
            spend=spend, roles=np.array([p.role for p in ps]), vis=vis,
            raw=o["claim"] * self.aov / spend, iroas=o["incr"] * self.aov / spend,
            claimed=o["claim"].sum(), conv_total=o["conv_total"], conv_paid=o["conv_paid"], seen_conv=o["seen_conv"],
            k_conv=o["conv_paid"] / o["claim"].sum(), k_all=o["web_all"] / o["platform_uu"].sum(),
            platform_uu=o["platform_uu"], any_touch=o["exposed_visitors"] * vis,
        )


class ReallocationDecision:
    """Move a marginal unit of budget from the lowest to the highest estimated platform."""

    @staticmethod
    def captured(estimate, truth):
        oracle = truth.max() - truth.min()
        return truth[np.argmax(estimate)] - truth[np.argmin(estimate)], oracle
