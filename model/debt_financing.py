class DebtFinancing:
    """Computes debt schedule: balances, interest expense, and principal repayments.

    Toll-road sphere uses a dedicated senior-debt model:
      - Drawdown = CapEx × (1 + VAT rate) each investment year
      - Equal repayment over the operating phase
    All other spheres use the generic initial_debt / new_debt_annual model.
    """

    def compute(self, inputs: dict, period: int) -> dict:
        sphere = inputs.get("sphere", "")
        interest_rate = float(inputs.get("interest_rate", 0)) / 100
        investment_years = int(inputs.get("investment_years", 0))
        operating_years = int(inputs.get("operating_years", period))

        if sphere == "toll-road":
            return self._toll_road(inputs, period, interest_rate, investment_years, operating_years)

        # ── Generic logic ────────────────────────────────────────────────
        initial_debt = float(inputs.get("initial_debt", 0))
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
            else:  # Bullet
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

    def _toll_road(self, inputs, period, interest_rate, investment_years, operating_years):
        """Senior debt = CapEx (already incl. VAT). Repaid equally over the operating phase."""
        capex = inputs.get("capex", [0.0] * (period + 1))

        # capex already includes VAT (entered as such in the UI)
        total_senior_debt = sum(capex[t] for t in range(1, period + 1))
        equal_repayment = total_senior_debt / operating_years if operating_years > 0 else 0.0

        debt_balance = [0.0]
        interest_expense = [0.0]
        principal_repayment = [0.0]
        new_debt = [0.0]

        for t in range(1, period + 1):
            prev_balance = debt_balance[t - 1]
            interest = prev_balance * interest_rate

            drawdown = capex[t] if t <= investment_years else 0.0
            repayment = min(equal_repayment, prev_balance) if t > investment_years else 0.0

            new_balance = max(0.0, prev_balance + drawdown - repayment)

            debt_balance.append(new_balance)
            interest_expense.append(interest)
            principal_repayment.append(repayment)
            new_debt.append(drawdown)

        return {
            "debt_balance": debt_balance,
            "interest_expense": interest_expense,
            "principal_repayment": principal_repayment,
            "new_debt_issuance": new_debt,
        }
