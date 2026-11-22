"""Per-platform deflators compared in the stress test. All add up to the uniform k's total."""
import numpy as np


class Deflators:
    CAP = (0.8, 1.25)

    @staticmethod
    def rescale(m, w):
        uu = m["platform_uu"]
        return m["k_all"] * w * uu.sum() / (w * uu).sum()

    @classmethod
    def build(cls, m, click_bias):
        uu = m["platform_uu"]
        r = (m["any_touch"] / (m["vis"] * click_bias)) / uu
        rel = r / np.exp(np.mean(np.log(r)))
        bounded = np.clip(rel, *cls.CAP)
        role = np.where(m["roles"] == "creation", 2.0, 1.0)
        return {
            "Uniform k (original)": np.full(len(uu), m["k_all"]),
            "Full click ratio": cls.rescale(m, r),
            "Half-strength click ratio": cls.rescale(m, rel ** 0.5),
            "Bounded click ratio (0.8-1.25)": cls.rescale(m, bounded),
            "Naive: double creation platforms": cls.rescale(m, role),
            "Bounded click ratio x role prior": cls.rescale(m, bounded * role),
        }
