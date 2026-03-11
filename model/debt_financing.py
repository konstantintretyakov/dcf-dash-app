class DebtFinancing:
    """Computes debt schedule: balances, interest expense, and principal repayments."""

    def compute(self, inputs: dict, period: int) -> dict:
        initial_debt = float(inputs.get("initial_debt", 0))
        interest_rate = float(inputs.get("interest_rate", 0)) / 100
        repayment_type = inputs.get("repayment_type", "Equal")
        new_debt_annual = float(inputs.get("new_debt_annual", 0))

        if repayment_type == "Equal" and period > 0:
            annual_repayment = initial_debt / period
        else:
            annual_repayment = 0.0

        debt_balance = [initial_debt]
        interest_expense = [0.0]
        principal_repayment = [0.0]
        new_debt = [0.0]

        for t in range(1, period + 1):
            prev_balance = debt_balance[t - 1]
            interest = prev_balance * interest_rate

            if repayment_type == "Equal":
                repayment = min(annual_repayment, prev_balance)
            else:  # Bullet: repay full balance at maturity
                repayment = prev_balance if t == period else 0.0

            new_balance = max(0.0, prev_balance - repayment + new_debt_annual)

            debt_balance.append(new_balance)
            interest_expense.append(interest)
            principal_repayment.append(repayment)
            new_debt.append(new_debt_annual)

        return {
            "debt_balance": debt_balance,
            "interest_expense": interest_expense,
            "principal_repayment": principal_repayment,
            "new_debt_issuance": new_debt,
        }
