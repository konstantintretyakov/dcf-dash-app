class ProfitAndLoss:
    """Aggregates P&L line items and computes Earnings Before Tax (EBT)."""

    def compute(self, inputs: dict, period: int) -> dict:
        ebit = inputs.get("ebit", [0.0] * (period + 1))
        interest_expense = inputs.get("interest_expense", [0.0] * (period + 1))

        ebt = [ebit[t] - interest_expense[t] for t in range(period + 1)]

        return {"ebt": ebt}
