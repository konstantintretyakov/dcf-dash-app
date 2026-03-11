class Taxes:
    """Computes EBIT, taxable income, tax charge, NOPAT and net income."""

    def compute(self, inputs: dict, period: int) -> dict:
        tax_rate = float(inputs.get("tax_rate", 0)) / 100
        ebitda = inputs.get("ebitda", [0.0] * (period + 1))
        depreciation = inputs.get("depreciation", [0.0] * (period + 1))
        amortization = inputs.get("amortization", [0.0] * (period + 1))
        interest_expense = inputs.get("interest_expense", [0.0] * (period + 1))

        ebit = [0.0]
        taxable_income = [0.0]
        tax = [0.0]
        nopat = [0.0]
        net_income = [0.0]

        for t in range(1, period + 1):
            e = ebitda[t] - depreciation[t] - amortization[t]
            ti = e - interest_expense[t]
            t_tax = max(0.0, ti * tax_rate)
            no = e * (1.0 - tax_rate)
            ni = ti - t_tax

            ebit.append(e)
            taxable_income.append(ti)
            tax.append(t_tax)
            nopat.append(no)
            net_income.append(ni)

        return {
            "ebit": ebit,
            "taxable_income": taxable_income,
            "tax": tax,
            "nopat": nopat,
            "net_income": net_income,
        }
