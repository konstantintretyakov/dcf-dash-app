import numpy as np

try:
    import numpy_financial as npf
except ImportError:
    npf = None


class Evaluation:
    """Computes NPV, IRR, PBP, DPBP and sensitivity analysis."""

    def compute(self, inputs: dict, period: int) -> dict:
        wacc = float(inputs.get("wacc", 10)) / 100
        initial_investment = float(inputs.get("initial_investment", 0))
        free_cash_flow = inputs.get("free_cash_flow", [0.0] * (period + 1))

        fcfs = [free_cash_flow[t] for t in range(1, period + 1)]

        # --- NPV ---
        npv = (
            sum(fcf / (1 + wacc) ** t for t, fcf in enumerate(fcfs, 1))
            - initial_investment
        )

        # --- IRR ---
        irr = None
        if npf is not None:
            try:
                irr_cf = [-initial_investment] + fcfs
                irr_val = npf.irr(irr_cf)
                if irr_val is not None and not np.isnan(irr_val) and not np.isinf(irr_val):
                    irr = float(irr_val)
            except Exception:
                irr = None

        # --- Payback Period (undiscounted) ---
        pbp = None
        cumulative = 0.0
        for t, fcf in enumerate(fcfs, 1):
            prev = cumulative
            cumulative += fcf
            if cumulative >= initial_investment and fcf != 0:
                pbp = (t - 1) + (initial_investment - prev) / fcf
                break

        # --- Discounted Payback Period ---
        dpbp = None
        cum_disc = 0.0
        for t, fcf in enumerate(fcfs, 1):
            prev = cum_disc
            disc_fcf = fcf / (1 + wacc) ** t
            cum_disc += disc_fcf
            if cum_disc >= initial_investment and disc_fcf != 0:
                dpbp = (t - 1) + (initial_investment - prev) / disc_fcf
                break

        # --- Sensitivity: NPV vs WACC (±2%) and Revenue Growth (±2%) ---
        base_rev = float(inputs.get("base_revenue", 0))
        base_growth = float(inputs.get("revenue_growth_rate", 0)) / 100
        cogs_pct = float(inputs.get("cogs_pct", 40)) / 100
        opex_pct = float(inputs.get("opex_pct", 20)) / 100
        margin = 1.0 - cogs_pct - opex_pct

        wacc_deltas = [-0.02, -0.01, 0.0, 0.01, 0.02]
        growth_deltas = [-0.02, -0.01, 0.0, 0.01, 0.02]

        sensitivity_matrix = []
        for w_delta in wacc_deltas:
            row = []
            for g_delta in growth_deltas:
                if w_delta == 0.0 and g_delta == 0.0:
                    row.append(round(npv, 0))
                    continue
                w = wacc + w_delta
                g = base_growth + g_delta
                sens_fcfs = [
                    base_rev * (1 + g) ** (t - 1) * margin
                    for t in range(1, period + 1)
                ]
                sens_npv = (
                    sum(f / (1 + w) ** t for t, f in enumerate(sens_fcfs, 1))
                    - initial_investment
                )
                row.append(round(sens_npv, 0))
            sensitivity_matrix.append(row)

        wacc_labels = [f"{(wacc + d) * 100:.1f}%" for d in wacc_deltas]
        growth_labels = [f"{(base_growth + d) * 100:.1f}%" for d in growth_deltas]

        return {
            "npv": npv,
            "irr": irr,
            "pbp": pbp,
            "dpbp": dpbp,
            "sensitivity_matrix": sensitivity_matrix,
            "sensitivity_wacc_labels": wacc_labels,
            "sensitivity_growth_labels": growth_labels,
        }
