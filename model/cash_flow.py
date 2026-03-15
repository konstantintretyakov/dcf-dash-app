class CashFlow:
    """Three-section cash flow statement: Operating, Investing, Financing.

    Toll-road sphere adds Shareholders' Loans (SHL) that automatically fill
    any cash gap and are repaid from surplus cash in subsequent years.
    SHL is interest-free and tracked as a separate liability.
    """

    def compute(self, inputs: dict, period: int) -> dict:
        sphere = inputs.get("sphere", "")
        initial_cash = float(inputs.get("initial_cash", 0))
        shl_rate = float(inputs.get("shl_interest_rate", 0)) / 100
        vat_rate = float(inputs.get("vat_rate", 0)) / 100
        vat_factor = 1 + vat_rate
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
            # Net VAT CF: input VAT recoverable on costs minus output VAT payable on revenue.
            # Negative = net payment to the government; positive = VAT refund.
            # VAT on revenue and on COGS/OpEx are each neutral (collected/paid then recovered/remitted).
            # Only CapEx and major repair input VAT generates a real cash recovery.
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
            )
            fcf = op + inv

            if sphere == "toll-road":
                # SHL interest on prior-year balance (known, no circularity)
                shl_int = shl_balance[t - 1] * shl_rate
                # Pre-SHL cash position after all known flows incl. SHL interest payment
                pre_shl = cash_balance[t - 1] + op + inv + fin_base - shl_int
                prev_shl_bal = shl_balance[t - 1]

                if pre_shl < 0:
                    # Cash gap — shareholders inject a loan to cover it
                    draw = -pre_shl
                    repay = 0.0
                    cash = 0.0
                elif prev_shl_bal > 0:
                    # Surplus cash — repay SHL first
                    repay = min(prev_shl_bal, pre_shl)
                    draw = 0.0
                    cash = pre_shl - repay
                else:
                    draw = 0.0
                    repay = 0.0
                    cash = pre_shl

                new_shl = max(0.0, prev_shl_bal + draw - repay)
                fin = fin_base - shl_int + draw - repay
                ncf = op + inv + fin
            else:
                shl_int = 0.0
                draw = 0.0
                repay = 0.0
                new_shl = 0.0
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

        return {
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
