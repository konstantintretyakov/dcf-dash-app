from model.revenues import Revenues
from model.operating_expenses import OperatingExpenses
from model.fixed_assets import FixedAssetsAndIntangibles
from model.working_capital import WorkingCapital
from model.taxes import Taxes
from model.debt_financing import DebtFinancing
from model.equity_financing import EquityFinancing
from model.profit_and_loss import ProfitAndLoss
from model.cash_flow import CashFlow
from model.balance_sheet import BalanceSheet
from model.evaluation import Evaluation


class DCFModel:
    """Orchestrator: instantiates all financial blocks and runs them in dependency order."""

    def __init__(self):
        self.revenues = Revenues()
        self.operating_expenses = OperatingExpenses()
        self.fixed_assets = FixedAssetsAndIntangibles()
        self.working_capital = WorkingCapital()
        self.taxes = Taxes()
        self.debt_financing = DebtFinancing()
        self.equity_financing = EquityFinancing()
        self.profit_and_loss = ProfitAndLoss()
        self.cash_flow = CashFlow()
        self.balance_sheet = BalanceSheet()
        self.evaluation = Evaluation()

    def run(self, inputs: dict) -> dict:
        investment_years = int(inputs.get("investment_years", 0))
        operating_years = int(inputs.get("operating_years", 5))
        period = investment_years + operating_years
        results = {
            "projection_years": period,
            "investment_years": investment_years,
            "operating_years": operating_years,
            "vat_rate": float(inputs.get("vat_rate", 0)),
            "wacc": float(inputs.get("wacc", 10)),
        }

        def merged(extra=None):
            base = {**inputs, **results}
            if extra:
                base.update(extra)
            return base

        # 1. Revenues
        results.update(self.revenues.compute(merged(), period))

        # 2. Operating Expenses (needs revenue)
        results.update(self.operating_expenses.compute(merged(), period))

        # 3. Fixed Assets & Intangibles
        results.update(self.fixed_assets.compute(merged(), period))

        # 4. Debt Financing (independent of other computed values)
        results.update(self.debt_financing.compute(merged(), period))

        # 5. Taxes (needs ebitda, D&A, interest_expense)
        results.update(self.taxes.compute(merged(), period))

        # 6. Equity Financing (needs net_income)
        results.update(self.equity_financing.compute(merged(), period))

        # 7. Working Capital (needs revenue, cogs)
        results.update(self.working_capital.compute(merged(), period))

        # 8. Profit & Loss – derives EBT from ebit and interest_expense
        results.update(self.profit_and_loss.compute(merged(), period))

        # 9. Cash Flow
        results.update(self.cash_flow.compute(merged(), period))

        # 10. Balance Sheet
        results.update(self.balance_sheet.compute(merged(), period))

        # 11. Evaluation (needs free_cash_flow, wacc, initial_investment)
        results.update(self.evaluation.compute(merged(), period))

        return results
