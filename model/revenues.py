class Revenues:
    """Computes revenue projections based on base revenue and growth rate.

    Revenue is zero during the investment phase and starts at base_revenue in
    the first operating year, growing at revenue_growth_rate each year after.
    """

    def compute(self, inputs: dict, period: int) -> dict:
        base_revenue = float(inputs.get("base_revenue", 0))
        growth_rate = float(inputs.get("revenue_growth_rate", 0)) / 100
        investment_years = int(inputs.get("investment_years", 0))

        revenue = [0.0]  # Year 0: always zero (base year)
        for t in range(1, period + 1):
            if t <= investment_years:
                revenue.append(0.0)          # investment phase: no revenue yet
            else:
                op_year = t - investment_years   # 1-indexed within operating phase
                revenue.append(base_revenue * (1 + growth_rate) ** (op_year - 1))

        return {"revenue": revenue}
