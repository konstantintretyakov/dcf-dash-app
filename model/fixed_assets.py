class FixedAssetsAndIntangibles:
    """Computes CapEx, D&A, and net fixed asset / intangibles balances."""

    def compute(self, inputs: dict, period: int) -> dict:
        total_capex = float(inputs.get("total_capex", 0))
        capex_pct_schedule = inputs.get("capex_pct_schedule", [])   # list of % per inv year
        investment_years = int(inputs.get("investment_years", 0))
        intangibles_amt = float(inputs.get("intangibles_investment", 0))
        repair_interval = int(inputs.get("repair_interval", 0))
        repair_cost = float(inputs.get("repair_cost", 0))
        repair_growth = float(inputs.get("repair_growth_rate", 0)) / 100
        vat_rate = float(inputs.get("vat_rate", 0)) / 100
        vat_factor = 1 + vat_rate  # capex and repairs entered incl. VAT; NFA uses ex-VAT cost

        # Opening NFA at Year 0: represents capital already deployed in assets
        opening_nfa = max(
            0.0,
            float(inputs.get("initial_equity", 0))
            + float(inputs.get("initial_debt", 0))
            - float(inputs.get("initial_cash", 0)),
        )

        capex = [0.0]
        major_repair = [0.0]
        intangibles = [0.0]
        depreciation = [0.0]
        amortization = [0.0]
        nfa = [opening_nfa]
        net_intangibles = [0.0]
        for t in range(1, period + 1):
            # CapEx only during investment phase, distributed by % schedule
            if t <= investment_years:
                pct = float(capex_pct_schedule[t - 1]) / 100.0 if t <= len(capex_pct_schedule) else 0.0
                annual_capex = total_capex * pct
            else:
                annual_capex = 0.0

            # Major repairs: fire every repair_interval years during the operating phase
            op_year = t - investment_years
            is_repair = (
                repair_interval > 0
                and repair_cost > 0
                and op_year > 0
                and op_year % repair_interval == 0
            )
            repair = repair_cost * (1 + repair_growth) ** op_year if is_repair else 0.0

            # Strip VAT: NFA and depreciation are based on ex-VAT cost
            annual_capex_excl = annual_capex / vat_factor
            repair_excl = repair / vat_factor

            nfa_before_dep = nfa[t - 1] + annual_capex_excl + repair_excl
            intang_before_amort = net_intangibles[t - 1] + intangibles_amt

            # D&A only during operating phase; spread over remaining operating periods
            if t > investment_years:
                remaining_op = period - t + 1
                dep = nfa_before_dep / remaining_op if remaining_op > 0 else nfa_before_dep
                amort = intang_before_amort / remaining_op if remaining_op > 0 else intang_before_amort
            else:
                dep = 0.0
                amort = 0.0

            new_nfa = max(0.0, nfa_before_dep - dep)
            new_intang = max(0.0, intang_before_amort - amort)

            capex.append(annual_capex)
            major_repair.append(repair)
            intangibles.append(intangibles_amt)
            depreciation.append(dep)
            amortization.append(amort)
            nfa.append(new_nfa)
            net_intangibles.append(new_intang)

        return {
            "capex": capex,
            "major_repair": major_repair,
            "intangibles_investment": intangibles,
            "depreciation": depreciation,
            "amortization": amortization,
            "net_fixed_assets": nfa,
            "net_intangibles": net_intangibles,
        }
