"""Tornado (one-way sensitivity) analysis.

Each driver is perturbed independently (±delta) while all others stay at base.
The resulting NPV swing determines bar width and ranking.
"""

TORNADO_DRIVERS = [
    {"key": "base_revenue",        "label": "Base Revenue",    "delta": 0.15, "mode": "pct", "unit": "₽M"},
    {"key": "wacc",                "label": "WACC",            "delta": 2.0,  "mode": "abs", "unit": "pp"},
    {"key": "cogs_pct",            "label": "COGS %",          "delta": 5.0,  "mode": "abs", "unit": "pp"},
    {"key": "total_capex",         "label": "Total CapEx",     "delta": 0.15, "mode": "pct", "unit": "₽M"},
    {"key": "revenue_growth_rate", "label": "Revenue Growth",  "delta": 3.0,  "mode": "abs", "unit": "pp"},
    {"key": "opex_pct",            "label": "OpEx %",          "delta": 5.0,  "mode": "abs", "unit": "pp"},
    {"key": "interest_rate",       "label": "Interest Rate",   "delta": 2.0,  "mode": "abs", "unit": "pp"},
    {"key": "tax_rate",            "label": "Tax Rate",        "delta": 5.0,  "mode": "abs", "unit": "pp"},
]


def compute_tornado(base_inputs: dict, base_npv: float) -> dict:
    """Run DCFModel for each driver ±delta, collect NPV swings.

    Returns a dict with:
      - tornado_bars: list of bar dicts, sorted by swing descending
      - tornado_base_npv: base case NPV
    """
    from model.dcf_model import DCFModel  # local import avoids circular dependency
    model = DCFModel()

    bars = []
    for driver in TORNADO_DRIVERS:
        key = driver["key"]
        base_val = float(base_inputs.get(key, 0))

        if driver["mode"] == "pct":
            low_val  = base_val * (1 - driver["delta"])
            high_val = base_val * (1 + driver["delta"])
        else:
            low_val  = base_val - driver["delta"]
            high_val = base_val + driver["delta"]

        low_npv  = _run_npv(model, base_inputs, key, low_val)
        high_npv = _run_npv(model, base_inputs, key, high_val)

        bars.append({
            "label":    driver["label"],
            "key":      key,
            "base_val": base_val,
            "low_val":  round(low_val, 4),
            "high_val": round(high_val, 4),
            "low_npv":  round(low_npv, 2),
            "high_npv": round(high_npv, 2),
            "swing":    round(abs(high_npv - low_npv), 2),
            "mode":     driver["mode"],
            "unit":     driver["unit"],
        })

    bars.sort(key=lambda b: b["swing"], reverse=True)
    return {
        "tornado_bars":     bars,
        "tornado_base_npv": round(base_npv, 2),
    }


def _run_npv(model, base_inputs: dict, key: str, val: float) -> float:
    inputs = {**base_inputs, key: val}
    try:
        res = model.run(inputs)
        return float(res.get("npv", 0) or 0)
    except Exception:
        return 0.0
