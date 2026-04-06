class CashFlow:
    """Three-section cash flow statement: Operating, Investing, Financing.

    Toll-road sphere adds Shareholders' Loans (SHL) that automatically fill
    any cash gap and are repaid from surplus cash in subsequent years.
    SHL is interest-free and tracked as a separate liability.

    Cash Sweep is supported for all spheres.  For toll-road the waterfall is:
      senior debt sweep  →  SHL gap-fill / repayment.
    """

    def compute(self, inputs: dict, period: int) -> dict:
        sphere = inputs.get("sphere", "")
        initial_cash = float(inputs.get("initial_cash", 0))
        shl_rate = float(inputs.get("shl_interest_rate", 0)) / 100
        vat_rate = float(inputs.get("vat_rate", 0)) / 100
        vat_factor = 1 + vat_rate
        investment_years = int(inputs.get("investment_years", 0))
        net_income = inputs.get("net_income", [0.0] * (period + 1))
        depreciation = inputs.get("depreciation", [0.0] * (period + 1))
        amortization = inputs.get("amortization", [0.0] * (period + 1))
        change_in_wc = inputs.get("change_in_wc", [0.0] * (period + 1))
        capex = inputs.get("capex", [0.0] * (period + 1))
        major_repair = inputs.get("major_repair", [0.0] * (period + 1))
        intangibles_investment = inputs.get("intangibles_investment", [0.0] * (period + 1))
        new_debt_issuance = inputs.get("new_debt_issuance", [0.0] * (period + 1))
        principal_repayment = inputs.get("principal_repayment", [0.0] * (period + 1))
        equity_injections = inputs.get("equity_injections", [0.0] * (period + 1))
        dividends = inputs.get("dividends", [0.0] * (period + 1))
        revenue = inputs.get("revenue", [0.0] * (period + 1))
        cogs = inputs.get("cogs", [0.0] * (period + 1))
        opex = inputs.get("opex", [0.0] * (period + 1))
        capital_grant = inputs.get("capital_grant", [0.0] * (period + 1))

        repayment_type = inputs.get("repayment_type", "Equal")
        is_sweep = (repayment_type == "Sweep")
        if is_sweep:
            sweep_pct = float(inputs.get("sweep_pct", 100)) / 100
            interest_rate = float(inputs.get("interest_rate", 0)) / 100
            tax_rate = float(inputs.get("tax_rate", 0)) / 100
            initial_debt_val = float(inputs.get("initial_debt", 0))
            new_debt_annual_val = float(inputs.get("new_debt_annual", 0))
            interest_expense_orig = inputs.get("interest_expense", [0.0] * (period + 1))
            ebit = inputs.get("ebit", [0.0] * (period + 1))
            dividends_pct = float(inputs.get("dividends_pct", 0)) / 100
            # Toll-road senior debt starts at 0 (initial_debt=0); generic starts at initial_debt
            sweep_debt_bal = [initial_debt_val]
            sweep_principal = [0.0]
            sweep_interest = [0.0]
            sweep_net_income = [0.0]
            sweep_dividends = [0.0]
            sweep_retained = [0.0]

        operating_cf = [0.0]
        investing_cf = [0.0]
        financing_cf = [0.0]
        free_cash_flow = [0.0]
        net_cash_flow = [0.0]
        cash_balance = [initial_cash]
        vat_cf = [0.0]
        shl_drawdown = [0.0]
        shl_repayment = [0.0]
        shl_balance = [0.0]
        shl_interest = [0.0]

        for t in range(1, period + 1):
            # Net VAT CF: only CapEx / repair input VAT creates a real cash recovery.
            vat = (cogs[t] + opex[t] + capex[t] / vat_factor + major_repair[t] / vat_factor + revenue[t]) * vat_rate \
                  - revenue[t] * vat_rate \
                  - (cogs[t] + opex[t]) * vat_rate
            op = (
                net_income[t]
                + depreciation[t]
                + amortization[t]
                - change_in_wc[t]
                + vat
            )
            inv = -capex[t] - major_repair[t] - intangibles_investment[t]
            fin_base = (
                new_debt_issuance[t]
                - principal_repayment[t]
                + equity_injections[t]
                - dividends[t]
                + capital_grant[t]
            )
            fcf = op + inv

            if sphere == "toll-road":
                shl_int = shl_balance[t - 1] * shl_rate
                prev_shl_bal = shl_balance[t - 1]

                if is_sweep:
                    # ── Recompute net income & dividends with actual sweep interest ──
                    prev_sweep_bal = sweep_debt_bal[t - 1]
                    actual_int = prev_sweep_bal * interest_rate
                    taxable = ebit[t] - actual_int
                    ni = taxable - max(0.0, taxable * tax_rate)
                    div = max(0.0, ni) * dividends_pct
                    re = sweep_retained[t - 1] + ni - div
                    sweep_net_income.append(ni)
                    sweep_dividends.append(div)
                    sweep_retained.append(re)

                    # ── Rebuild op & fin_base with corrected values ──
                    op = ni + depreciation[t] + amortization[t] - change_in_wc[t] + vat
                    fcf = op + inv
                    fin_base = (
                        new_debt_issuance[t]
                        - principal_repayment[t]
                        + equity_injections[t]
                        - div
                        + capital_grant[t]
                    )

                    # ── Pre-SHL cash after senior debt sweep ──
                    # fin_base: new_debt_issuance=drawdown, principal_repayment=0 (from DebtFinancing sweep)
                    pre_sweep = cash_balance[t - 1] + op + inv + fin_base - shl_int
                    # Sweep only in the operating phase; investment years fund drawdown, not repayment
                    if t > investment_years:
                        sweep_amt = min(sweep_pct * max(0.0, pre_sweep), prev_sweep_bal)
                    else:
                        sweep_amt = 0.0
                    new_sweep_bal = max(0.0, prev_sweep_bal + new_debt_issuance[t] - sweep_amt)
                    pre_shl = pre_sweep - sweep_amt
                    sweep_debt_bal.append(new_sweep_bal)
                    sweep_principal.append(sweep_amt)
                    sweep_interest.append(actual_int)
                else:
                    # Equal / Bullet repayment — principal already in fin_base via DebtFinancing
                    pre_shl = cash_balance[t - 1] + op + inv + fin_base - shl_int
                    sweep_amt = 0.0

                if pre_shl < 0:
                    draw = -pre_shl
                    repay = 0.0
                    cash = 0.0
                elif prev_shl_bal > 0:
                    repay = min(prev_shl_bal, pre_shl)
                    draw = 0.0
                    cash = pre_shl - repay
                else:
                    draw = 0.0
                    repay = 0.0
                    cash = pre_shl

                new_shl = max(0.0, prev_shl_bal + draw - repay)
                fin = fin_base - sweep_amt - shl_int + draw - repay
                ncf = op + inv + fin

            else:
                shl_int = 0.0
                draw = 0.0
                repay = 0.0
                new_shl = 0.0

                if is_sweep:
                    prev_sweep_bal = sweep_debt_bal[t - 1]
                    actual_int = prev_sweep_bal * interest_rate
                    # Recompute net income & dividends with actual sweep interest
                    taxable = ebit[t] - actual_int
                    ni = taxable - max(0.0, taxable * tax_rate)
                    div = max(0.0, ni) * dividends_pct
                    re = sweep_retained[t - 1] + ni - div
                    sweep_net_income.append(ni)
                    sweep_dividends.append(div)
                    sweep_retained.append(re)
                    # Rebuild op & fin_base with corrected values
                    op = ni + depreciation[t] + amortization[t] - change_in_wc[t] + vat
                    fin_base = (
                        new_debt_issuance[t]
                        - principal_repayment[t]
                        + equity_injections[t]
                        - div
                        + capital_grant[t]
                    )
                    fcf = op + inv
                    sweep_amt = min(sweep_pct * max(0.0, fcf), prev_sweep_bal)
                    new_sweep_bal = max(0.0, prev_sweep_bal + new_debt_annual_val - sweep_amt)
                    fin = fin_base - sweep_amt
                    sweep_debt_bal.append(new_sweep_bal)
                    sweep_principal.append(sweep_amt)
                    sweep_interest.append(actual_int)
                else:
                    fin = fin_base

                ncf = op + inv + fin
                cash = cash_balance[t - 1] + ncf

            vat_cf.append(vat)
            operating_cf.append(op)
            investing_cf.append(inv)
            financing_cf.append(fin)
            free_cash_flow.append(fcf)
            net_cash_flow.append(ncf)
            cash_balance.append(cash)
            shl_drawdown.append(draw)
            shl_repayment.append(repay)
            shl_balance.append(new_shl)
            shl_interest.append(shl_int)

        result = {
            "vat_cf": vat_cf,
            "operating_cf": operating_cf,
            "investing_cf": investing_cf,
            "financing_cf": financing_cf,
            "free_cash_flow": free_cash_flow,
            "net_cash_flow": net_cash_flow,
            "cash_balance": cash_balance,
            "shl_drawdown": shl_drawdown,
            "shl_repayment": shl_repayment,
            "shl_balance": shl_balance,
            "shl_interest": shl_interest,
        }
        if is_sweep:
            result["debt_balance"] = sweep_debt_bal
            result["principal_repayment"] = sweep_principal
            result["interest_expense"] = sweep_interest
            result["net_income"] = sweep_net_income
            result["dividends"] = sweep_dividends
            result["retained_earnings"] = sweep_retained
            # Recompute EBT for P&L consistency
            result["ebt"] = [ebit[t] - sweep_interest[t] if t < len(sweep_interest) else 0.0
                             for t in range(period + 1)]
        return result
