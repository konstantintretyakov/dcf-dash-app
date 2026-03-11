class Revenues:
    """Computes revenue projections based on base revenue and growth rate."""

    def compute(self, inputs: dict, period: int) -> dict:
        base_revenue = float(inputs.get("base_revenue", 0))
        growth_rate = float(inputs.get("revenue_growth_rate", 0)) / 100

        revenue = [0.0]  # Year 0: no revenue (investment year)
        for t in range(1, period + 1):
            revenue.append(base_revenue * (1 + growth_rate) ** (t - 1))

        return {"revenue": revenue}
