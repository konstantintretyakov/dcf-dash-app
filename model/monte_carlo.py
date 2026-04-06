"""Monte Carlo simulation: sample all uncertain drivers simultaneously,
run DCFModel for each iteration, and return NPV/IRR distributions and
driver contribution-to-variance statistics.
"""

import numpy as np

MC_DRIVERS = [
    {
        "key":       "base_revenue",
        "label":     "Base Revenue",
        "dist":      "lognormal",
        "sigma_pct": 0.10,          # 10 % CV → right-skewed, always positive
    },
    {
        "key":       "revenue_growth_rate",
        "label":     "Revenue Growth Rate",
        "dist":      "normal",
        "sigma_abs": 2.0,           # ± 2 pp std dev
    },
    {
        "key":       "cogs_pct",
        "label":     "COGS %",
        "dist":      "normal_trunc",
        "sigma_abs": 3.0,           # ± 3 pp std dev, clipped to [0, 95]
        "clip":      (0.0, 95.0),
    },
    {
        "key":       "opex_pct",
        "label":     "OpEx %",
        "dist":      "normal_trunc",
        "sigma_abs": 3.0,
        "clip":      (0.0, 95.0),
    },
    {
        "key":       "total_capex",
        "label":     "Total CapEx",
        "dist":      "lognormal",
        "sigma_pct": 0.15,          # 15 % CV → cost overrun skew
    },
    {
        "key":       "wacc",
        "label":     "WACC",
        "dist":      "normal",
        "sigma_abs": 1.5,           # ± 1.5 pp std dev
    },
    {
        "key":       "tax_rate",
        "label":     "Tax Rate",
        "dist":      "uniform",
        "delta_abs": 5.0,           # flat ± 5 pp (policy risk)
    },
]


def _sample(rng: np.random.Generator, driver: dict, base: float, n: int) -> np.ndarray:
    dist = driver["dist"]

    if dist == "lognormal":
        if base <= 0:
            return np.zeros(n)
        # Parameterise so that E[X] = base and CV = sigma_pct
        cv = driver["sigma_pct"]
        sigma_log = np.sqrt(np.log(1.0 + cv ** 2))
        mu_log = np.log(base) - 0.5 * sigma_log ** 2
        return rng.lognormal(mu_log, sigma_log, n)

    elif dist == "normal":
        return rng.normal(base, driver["sigma_abs"], n)

    elif dist == "normal_trunc":
        raw = rng.normal(base, driver["sigma_abs"], n)
        lo, hi = driver.get("clip", (0.0, 100.0))
        return np.clip(raw, lo, hi)

    elif dist == "uniform":
        delta = driver["delta_abs"]
        return rng.uniform(base - delta, base + delta, n)

    return np.full(n, base)


def compute_mc(base_inputs: dict, n_iterations: int = 2000, seed: int = 42) -> dict:
    """Run Monte Carlo simulation.

    Args:
        base_inputs:  full inputs dict (same structure passed to DCFModel.run)
        n_iterations: number of simulation paths
        seed:         RNG seed for reproducibility

    Returns dict with:
        mc_npv, mc_irr       – lists of per-iteration NPV / IRR (%) values
        mc_npv_p{10,50,90}   – NPV percentiles
        mc_irr_p{10,50,90}   – IRR percentiles
        mc_prob_npv_pos      – P(NPV ≥ 0) in %
        mc_prob_irr_wacc     – P(IRR ≥ WACC) in %
        mc_contributions     – list of {label, r2, pct} sorted by r2 desc
        mc_base_wacc         – base WACC value
        mc_n                 – actual iteration count
    """
    from model.dcf_model import DCFModel  # local import avoids circular dependency
    model = DCFModel()
    rng = np.random.default_rng(seed)

    # ── Sample drivers ────────────────────────────────────────────────────
    samples: dict[str, np.ndarray] = {}
    for driver in MC_DRIVERS:
        key = driver["key"]
        base = float(base_inputs.get(key, 0))
        samples[key] = _sample(rng, driver, base, n_iterations)

    # ── Simulate ──────────────────────────────────────────────────────────
    npv_out = np.zeros(n_iterations)
    irr_out = np.full(n_iterations, np.nan)

    for i in range(n_iterations):
        iter_inputs = {**base_inputs}
        for key, arr in samples.items():
            iter_inputs[key] = float(arr[i])
        try:
            res = model.run(iter_inputs)
            npv_out[i] = float(res.get("npv", 0) or 0)
            irr_val = res.get("irr")
            if irr_val is not None and not np.isnan(float(irr_val)):
                irr_out[i] = float(irr_val) * 100.0   # store as %
        except Exception:
            npv_out[i] = 0.0

    valid_irr = irr_out[~np.isnan(irr_out)]
    base_wacc = float(base_inputs.get("wacc", 10))

    # ── Contribution to NPV variance (Pearson R² per driver) ─────────────
    contributions = []
    npv_std = float(npv_out.std())
    for driver in MC_DRIVERS:
        key = driver["key"]
        s = samples[key]
        if s.std() > 0 and npv_std > 0:
            r2 = float(np.corrcoef(s, npv_out)[0, 1]) ** 2
        else:
            r2 = 0.0
        contributions.append({"label": driver["label"], "key": key, "r2": round(r2, 4)})

    total_r2 = sum(c["r2"] for c in contributions) or 1.0
    for c in contributions:
        c["pct"] = round(c["r2"] / total_r2 * 100.0, 1)
    contributions.sort(key=lambda c: c["r2"], reverse=True)

    return {
        "mc_npv":           npv_out.tolist(),
        "mc_irr":           valid_irr.tolist(),
        "mc_n":             n_iterations,
        "mc_npv_p10":       float(np.percentile(npv_out, 10)),
        "mc_npv_p50":       float(np.percentile(npv_out, 50)),
        "mc_npv_p90":       float(np.percentile(npv_out, 90)),
        "mc_irr_p10":       float(np.percentile(valid_irr, 10)) if len(valid_irr) else 0.0,
        "mc_irr_p50":       float(np.percentile(valid_irr, 50)) if len(valid_irr) else 0.0,
        "mc_irr_p90":       float(np.percentile(valid_irr, 90)) if len(valid_irr) else 0.0,
        "mc_prob_npv_pos":   float((npv_out >= 0).mean() * 100.0),
        "mc_prob_irr_wacc":  float((valid_irr >= base_wacc).mean() * 100.0) if len(valid_irr) else 0.0,
        "mc_irr_invalid_n":  int(n_iterations - len(valid_irr)),
        "mc_irr_invalid_pct":float((n_iterations - len(valid_irr)) / n_iterations * 100.0),
        "mc_contributions":  contributions,
        "mc_base_wacc":      base_wacc,
    }
