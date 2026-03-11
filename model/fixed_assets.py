class FixedAssetsAndIntangibles:
    """Computes CapEx, D&A, and net fixed asset / intangibles balances."""

    def compute(self, inputs: dict, period: int) -> dict:
        annual_capex = float(inputs.get("annual_capex", 0))
        intangibles_amt = float(inputs.get("intangibles_investment", 0))
        useful_life = max(1, int(inputs.get("useful_life_years", 10)))
        amort_period = max(1, int(inputs.get("amortization_period", 5)))

        # Opening NFA at Year 0: represents capital already deployed in assets
        # (total funding raised minus cash kept on hand)
        opening_nfa = max(
            0.0,
            float(inputs.get("initial_equity", 0))
            + float(inputs.get("initial_debt", 0))
            - float(inputs.get("initial_cash", 0)),
        )

        capex = [0.0]
        intangibles = [0.0]
        depreciation = [0.0]
        amortization = [0.0]
        nfa = [opening_nfa]
        net_intangibles = [0.0]
        cumulative_capex = opening_nfa  # seed depreciation pool with opening NFA
        cumulative_intang = 0.0

        for t in range(1, period + 1):
            cumulative_capex += annual_capex
            cumulative_intang += intangibles_amt

            dep = cumulative_capex / useful_life
            amort = cumulative_intang / amort_period

            new_nfa = max(0.0, nfa[t - 1] + annual_capex - dep)
            new_intang = max(0.0, net_intangibles[t - 1] + intangibles_amt - amort)

            capex.append(annual_capex)
            intangibles.append(intangibles_amt)
            depreciation.append(dep)
            amortization.append(amort)
            nfa.append(new_nfa)
            net_intangibles.append(new_intang)

        return {
            "capex": capex,
            "intangibles_investment": intangibles,
            "depreciation": depreciation,
            "amortization": amortization,
            "net_fixed_assets": nfa,
            "net_intangibles": net_intangibles,
        }
