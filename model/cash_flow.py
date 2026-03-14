class CashFlow:
    """Three-section cash flow statement: Operating, Investing, Financing."""

    def compute(self, inputs: dict, period: int) -> dict:
        initial_cash = float(inputs.get("initial_cash", 0))
        vat_rate = float(inputs.get("vat_rate", 0)) / 100
        net_income = inputs.get("net_income", [0.0] * (period + 1))
        depreciation = inputs.get("depreciation", [0.0] * (period + 1))
        amortization = inputs.get("amortization", [0.0] * (period + 1))
        change_in_wc = inputs.get("change_in_wc", [0.0] * (period + 1))
        capex = inputs.get("capex", [0.0] * (period + 1))
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

        for t in range(1, period + 1):
            # Net VAT CF: input VAT recoverable on costs minus output VAT payable on revenue.
            # Negative = net payment to the government; positive = VAT refund.
            vat = (cogs[t] + opex[t] + capex[t]) * vat_rate - revenue[t] * vat_rate
            op = (
                net_income[t]
                + depreciation[t]
                + amortization[t]
                - change_in_wc[t]
                + vat
            )
            inv = -capex[t] - intangibles_investment[t]
            fin = (
                new_debt_issuance[t]
                - principal_repayment[t]
                + equity_injections[t]
                - dividends[t]
            )
            fcf = op + inv
            ncf = op + inv + fin
            cash = cash_balance[t - 1] + ncf

            vat_cf.append(vat)
            operating_cf.append(op)
            investing_cf.append(inv)
            financing_cf.append(fin)
            free_cash_flow.append(fcf)
            net_cash_flow.append(ncf)
            cash_balance.append(cash)

        return {
            "vat_cf": vat_cf,
            "operating_cf": operating_cf,
            "investing_cf": investing_cf,
            "financing_cf": financing_cf,
            "free_cash_flow": free_cash_flow,
            "net_cash_flow": net_cash_flow,
            "cash_balance": cash_balance,
        }
