class EquityFinancing:
    """Computes equity injections, dividends, retained earnings and cumulative equity."""

    def compute(self, inputs: dict, period: int) -> dict:
        initial_equity = float(inputs.get("initial_equity", 0))
        annual_injection = float(inputs.get("annual_equity_injection", 0))
        dividends_pct = float(inputs.get("dividends_pct", 0)) / 100
        net_income = inputs.get("net_income", [0.0] * (period + 1))

        equity_injections = [0.0]
        dividends = [0.0]
        retained_earnings = [0.0]
        paid_in_capital = [initial_equity]

        for t in range(1, period + 1):
            div = max(0.0, net_income[t]) * dividends_pct
            re = retained_earnings[t - 1] + net_income[t] - div
            pic = paid_in_capital[t - 1] + annual_injection

            equity_injections.append(annual_injection)
            dividends.append(div)
            retained_earnings.append(re)
            paid_in_capital.append(pic)

        cumulative_equity = [
            paid_in_capital[t] + retained_earnings[t] for t in range(period + 1)
        ]

        return {
            "equity_injections": equity_injections,
            "dividends": dividends,
            "retained_earnings": retained_earnings,
            "paid_in_capital": paid_in_capital,
            "cumulative_equity": cumulative_equity,
        }
