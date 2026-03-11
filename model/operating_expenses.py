class OperatingExpenses:
    """Computes COGS, OpEx, Gross Profit and EBITDA from revenue percentages."""

    def compute(self, inputs: dict, period: int) -> dict:
        cogs_pct = float(inputs.get("cogs_pct", 0)) / 100
        opex_pct = float(inputs.get("opex_pct", 0)) / 100
        revenue = inputs.get("revenue", [0.0] * (period + 1))

        cogs = [0.0]
        opex = [0.0]
        gross_profit = [0.0]
        ebitda = [0.0]

        for t in range(1, period + 1):
            c = revenue[t] * cogs_pct
            o = revenue[t] * opex_pct
            gp = revenue[t] - c
            eb = gp - o
            cogs.append(c)
            opex.append(o)
            gross_profit.append(gp)
            ebitda.append(eb)

        return {
            "cogs": cogs,
            "opex": opex,
            "gross_profit": gross_profit,
            "ebitda": ebitda,
        }
