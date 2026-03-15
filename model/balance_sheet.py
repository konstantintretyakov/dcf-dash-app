class BalanceSheet:
    """Aggregates balance sheet: Assets = Liabilities + Equity, with balance check."""

    def compute(self, inputs: dict, period: int) -> dict:
        cash_balance = inputs.get("cash_balance", [0.0] * (period + 1))
        accounts_receivable = inputs.get("accounts_receivable", [0.0] * (period + 1))
        inventory = inputs.get("inventory", [0.0] * (period + 1))
        net_fixed_assets = inputs.get("net_fixed_assets", [0.0] * (period + 1))
        net_intangibles = inputs.get("net_intangibles", [0.0] * (period + 1))
        accounts_payable = inputs.get("accounts_payable", [0.0] * (period + 1))
        debt_balance = inputs.get("debt_balance", [0.0] * (period + 1))
        shl_balance = inputs.get("shl_balance", [0.0] * (period + 1))
        paid_in_capital = inputs.get("paid_in_capital", [0.0] * (period + 1))
        retained_earnings = inputs.get("retained_earnings", [0.0] * (period + 1))

        total_assets = []
        total_liabilities = []
        total_equity = []
        balance_check = []
        balance_diff = []

        for t in range(period + 1):
            ta = (
                cash_balance[t]
                + accounts_receivable[t]
                + inventory[t]
                + net_fixed_assets[t]
                + net_intangibles[t]
            )
            tl = accounts_payable[t] + debt_balance[t] + shl_balance[t]
            te = paid_in_capital[t] + retained_earnings[t]
            diff = ta - (tl + te)

            total_assets.append(ta)
            total_liabilities.append(tl)
            total_equity.append(te)
            balance_check.append(abs(diff) < 1.0)
            balance_diff.append(diff)

        return {
            "bs_total_assets": total_assets,
            "bs_total_liabilities": total_liabilities,
            "bs_total_equity": total_equity,
            "bs_balance_check": balance_check,
            "bs_balance_diff": balance_diff,
        }
