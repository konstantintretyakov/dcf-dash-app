"""All Plotly figure builders. Each function accepts only results: dict and returns go.Figure."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


TEAL_COLORS = ["#1abc9c", "#16a085", "#0e6655", "#0a4f41", "#07362c"]
BLUE_COLORS = ["#2980b9", "#1f618d", "#154360", "#1a5276", "#2e86c1"]
RED_COLOR = "#e74c3c"
GREEN_COLOR = "#27ae60"
ORANGE_COLOR = "#f39c12"
GREY_COLOR = "#95a5a6"

LAYOUT_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="#fafafa",
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(l=60, r=30, t=50, b=50),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#ccc", borderwidth=1),
)


def _years(results: dict):
    period = results.get("projection_years", 5)
    inv = results.get("investment_years", 0)
    years = list(range(period + 1))
    labels = []
    for t in years:
        if t == 0:
            labels.append("Base")
        elif t <= inv:
            labels.append(f"Inv {t}")
        else:
            labels.append(f"Op {t - inv}")
    return years, labels


def _inv_shapes(results: dict, labels: list) -> list:
    """Return a list of vrect shapes that shade the investment phase columns."""
    inv = results.get("investment_years", 0)
    if inv == 0:
        return []
    # x-axis is categorical: shade from "Base" up to and including the last Inv label
    last_inv_label = f"Inv {inv}"
    return [
        dict(
            type="rect",
            xref="paper", yref="paper",
            x0=0, x1=inv / (len(labels) - 1) if len(labels) > 1 else 0,
            y0=0, y1=1,
            fillcolor="rgba(230,126,34,0.08)",
            line_width=0,
            layer="below",
        )
    ]


# ─────────────────────────────────────────────
# Tab 2 – Revenues
# ─────────────────────────────────────────────
def revenue_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    revenue = results.get("revenue", [0] * len(years))
    growth_rate = float(results.get("revenue_growth_rate", 0))
    inv = results.get("investment_years", 0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    bar_colors = [
        ORANGE_COLOR if (t > 0 and t <= inv) else TEAL_COLORS[0]
        for t in years
    ]
    fig.add_trace(
        go.Bar(
            x=labels, y=revenue, name="Revenue", marker_color=bar_colors,
            text=[f"{v:,.2f}" for v in revenue], textposition="outside",
        ),
        secondary_y=False,
    )

    growth_vals = [growth_rate if t > 0 else 0 for t in years]
    fig.add_trace(
        go.Scatter(
            x=labels, y=growth_vals, name="Growth Rate (%)",
            mode="lines+markers", line=dict(color=ORANGE_COLOR, width=2, dash="dot"),
            marker=dict(size=7),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Revenue & Growth Rate"
              + (f"  |  <span style='color:{ORANGE_COLOR}'>▓ Investment Phase</span>" if inv else ""),
        **LAYOUT_BASE,
    )
    fig.update_yaxes(title_text="Revenue (₽M)", secondary_y=False)
    fig.update_yaxes(title_text="Growth Rate (%)", secondary_y=True, ticksuffix="%")
    return fig


# ─────────────────────────────────────────────
# Tab 3 – Operating Expenses
# ─────────────────────────────────────────────
def opex_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    revenue = results.get("revenue", [0] * len(years))
    cogs = results.get("cogs", [0] * len(years))
    opex = results.get("opex", [0] * len(years))
    ebitda = results.get("ebitda", [0] * len(years))

    ebitda_margin = [
        (ebitda[t] / revenue[t] * 100) if revenue[t] else 0 for t in years
    ]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=labels, y=cogs, name="COGS", marker_color=BLUE_COLORS[0]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=labels, y=opex, name="OpEx (SG&A/R&D)", marker_color=BLUE_COLORS[2]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=labels, y=ebitda_margin, name="EBITDA Margin (%)",
            mode="lines+markers", line=dict(color=GREEN_COLOR, width=2),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Operating Expenses (Stacked)", barmode="stack", **LAYOUT_BASE
    )
    fig.update_yaxes(title_text="Amount (₽M)", secondary_y=False)
    fig.update_yaxes(title_text="EBITDA Margin (%)", secondary_y=True, ticksuffix="%")
    return fig


# ─────────────────────────────────────────────
# Tab 4 – Fixed Assets & Intangibles
# ─────────────────────────────────────────────
def fa_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    nfa = results.get("net_fixed_assets", [0] * len(years))
    net_intang = results.get("net_intangibles", [0] * len(years))
    dep = results.get("depreciation", [0] * len(years))
    amort = results.get("amortization", [0] * len(years))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=nfa, name="Net Fixed Assets",
                             mode="lines+markers", line=dict(color=TEAL_COLORS[0], width=2)))
    fig.add_trace(go.Scatter(x=labels, y=net_intang, name="Net Intangibles",
                             mode="lines+markers", line=dict(color=BLUE_COLORS[0], width=2)))
    fig.add_trace(go.Scatter(x=labels, y=dep, name="Depreciation",
                             mode="lines+markers", line=dict(color=RED_COLOR, width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=labels, y=amort, name="Amortization",
                             mode="lines+markers", line=dict(color=ORANGE_COLOR, width=2, dash="dot")))

    fig.update_layout(title="Fixed Assets & Intangibles Over Time", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Amount (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 5 – Working Capital
# ─────────────────────────────────────────────
def wc_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    ar = results.get("accounts_receivable", [0] * len(years))
    inv = results.get("inventory", [0] * len(years))
    ap = results.get("accounts_payable", [0] * len(years))
    nwc = results.get("net_working_capital", [0] * len(years))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=ar, name="Accounts Receivable", marker_color=TEAL_COLORS[0]))
    fig.add_trace(go.Bar(x=labels, y=inv, name="Inventory", marker_color=BLUE_COLORS[0]))
    fig.add_trace(go.Bar(x=labels, y=[-v for v in ap], name="Accounts Payable (−)",
                         marker_color=RED_COLOR))
    fig.add_trace(go.Scatter(x=labels, y=nwc, name="Net Working Capital",
                             mode="lines+markers", line=dict(color=ORANGE_COLOR, width=3)))

    fig.update_layout(title="Working Capital Components", barmode="relative", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Amount (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 6 – Taxes
# ─────────────────────────────────────────────
def tax_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    ebt = results.get("ebt", [0] * len(years))
    tax = results.get("tax", [0] * len(years))
    net_income = results.get("net_income", [0] * len(years))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=ebt, name="EBT", marker_color=BLUE_COLORS[0]))
    fig.add_trace(go.Bar(x=labels, y=[-v for v in tax], name="Tax (−)",
                         marker_color=RED_COLOR, opacity=0.7))
    fig.add_trace(go.Scatter(x=labels, y=net_income, name="Net Income",
                             mode="lines+markers", line=dict(color=GREEN_COLOR, width=3)))

    fig.update_layout(title="Taxes: EBT → Tax → Net Income", barmode="relative", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Amount (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 7 – Debt Financing
# ─────────────────────────────────────────────
def debt_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    debt = results.get("debt_balance", [0] * len(years))
    interest = results.get("interest_expense", [0] * len(years))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=labels, y=debt, name="Debt Balance",
                   mode="lines", fill="tozeroy",
                   line=dict(color=RED_COLOR, width=2),
                   fillcolor="rgba(231,76,60,0.2)"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(x=labels, y=interest, name="Interest Expense",
               marker_color=ORANGE_COLOR, opacity=0.8),
        secondary_y=True,
    )

    fig.update_layout(title="Debt Balance & Interest Expense", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Debt Balance (₽M)", secondary_y=False)
    fig.update_yaxes(title_text="Interest Expense (₽M)", secondary_y=True)
    return fig


# ─────────────────────────────────────────────
# Tab 8 – Equity Financing
# ─────────────────────────────────────────────
def equity_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    paid_in = results.get("paid_in_capital", [0] * len(years))
    retained = results.get("retained_earnings", [0] * len(years))
    dividends = results.get("dividends", [0] * len(years))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=paid_in, name="Paid-in Capital",
                             stackgroup="equity", mode="none",
                             fillcolor="rgba(41,128,185,0.5)"))
    fig.add_trace(go.Scatter(x=labels, y=[max(0.0, r) for r in retained],
                             name="Retained Earnings",
                             stackgroup="equity", mode="none",
                             fillcolor="rgba(39,174,96,0.5)"))
    fig.add_trace(go.Scatter(x=labels, y=dividends, name="Dividends Paid",
                             mode="lines+markers",
                             line=dict(color=RED_COLOR, width=2, dash="dot")))

    fig.update_layout(title="Equity Components Over Time", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Amount (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 9 – P&L (Waterfall for Year N)
# ─────────────────────────────────────────────
def pnl_chart(results: dict) -> go.Figure:
    period = results.get("projection_years", 5)
    t = period  # Show waterfall for final year

    revenue = results.get("revenue", [0] * (period + 1))
    cogs = results.get("cogs", [0] * (period + 1))
    opex = results.get("opex", [0] * (period + 1))
    dep = results.get("depreciation", [0] * (period + 1))
    amort = results.get("amortization", [0] * (period + 1))
    interest = results.get("interest_expense", [0] * (period + 1))
    tax = results.get("tax", [0] * (period + 1))
    net_income = results.get("net_income", [0] * (period + 1))

    measures = ["absolute", "relative", "total", "relative", "total",
                "relative", "relative", "total", "relative", "total"]
    x_labels = ["Revenue", "− COGS", "Gross Profit", "− OpEx",
                "EBITDA", "− D&A", "− Interest", "EBT", "− Tax", "Net Income"]
    y_vals = [
        revenue[t],
        -cogs[t],
        0,  # total (auto)
        -opex[t],
        0,  # total
        -(dep[t] + amort[t]),
        -interest[t],
        0,  # total
        -tax[t],
        0,  # total
    ]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_vals,
        connector={"line": {"color": "#636efa"}},
        decreasing={"marker": {"color": RED_COLOR}},
        increasing={"marker": {"color": TEAL_COLORS[0]}},
        totals={"marker": {"color": BLUE_COLORS[1]}},
        text=[f"{v:,.2f}" if v != 0 else "" for v in y_vals],
        textposition="outside",
    ))

    fig.update_layout(title=f"P&L Waterfall — Year {t}", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Amount (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 10 – Cash Flow
# ─────────────────────────────────────────────
def cashflow_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    op = results.get("operating_cf", [0] * len(years))
    inv = results.get("investing_cf", [0] * len(years))
    fin = results.get("financing_cf", [0] * len(years))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=op, name="Operating CF", marker_color=GREEN_COLOR))
    fig.add_trace(go.Bar(x=labels, y=inv, name="Investing CF", marker_color=RED_COLOR))
    fig.add_trace(go.Bar(x=labels, y=fin, name="Financing CF", marker_color=BLUE_COLORS[0]))

    fig.update_layout(title="Cash Flow by Section", barmode="group", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Cash Flow (₽M)")
    return fig


# ─────────────────────────────────────────────
# Tab 11 – Balance Sheet
# ─────────────────────────────────────────────
def balance_sheet_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    cash = results.get("cash_balance", [0] * len(years))
    ar = results.get("accounts_receivable", [0] * len(years))
    inv = results.get("inventory", [0] * len(years))
    nfa = results.get("net_fixed_assets", [0] * len(years))
    net_intang = results.get("net_intangibles", [0] * len(years))
    ap = results.get("accounts_payable", [0] * len(years))
    debt = results.get("debt_balance", [0] * len(years))
    equity = results.get("bs_total_equity", [0] * len(years))

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Assets", "Liabilities & Equity"))

    # Assets
    asset_traces = [
        ("Cash", cash, TEAL_COLORS[0]),
        ("Accounts Receivable", ar, TEAL_COLORS[1]),
        ("Inventory", inv, TEAL_COLORS[2]),
        ("Net Fixed Assets", nfa, BLUE_COLORS[0]),
        ("Net Intangibles", net_intang, BLUE_COLORS[2]),
    ]
    for name, vals, color in asset_traces:
        fig.add_trace(go.Bar(x=labels, y=vals, name=name, marker_color=color,
                             showlegend=True), row=1, col=1)

    # Liabilities & Equity
    le_traces = [
        ("Accounts Payable", ap, ORANGE_COLOR),
        ("Debt", debt, RED_COLOR),
        ("Total Equity", equity, GREEN_COLOR),
    ]
    for name, vals, color in le_traces:
        fig.add_trace(go.Bar(x=labels, y=vals, name=name, marker_color=color,
                             showlegend=True), row=1, col=2)

    fig.update_layout(
        title="Balance Sheet: Assets vs Liabilities & Equity",
        barmode="stack",
        **LAYOUT_BASE,
    )
    return fig


# ─────────────────────────────────────────────
# Tab 12 – Evaluation: FCF Bar + Cumulative
# ─────────────────────────────────────────────
def fcf_chart(results: dict) -> go.Figure:
    years, labels = _years(results)
    fcf = results.get("free_cash_flow", [0] * len(years))
    cumulative = []
    running = 0.0
    for v in fcf:
        running += v
        cumulative.append(running)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    colors = [GREEN_COLOR if v >= 0 else RED_COLOR for v in fcf]
    fig.add_trace(
        go.Bar(x=labels, y=fcf, name="Free Cash Flow", marker_color=colors),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=labels, y=cumulative, name="Cumulative FCF",
                   mode="lines+markers", line=dict(color=BLUE_COLORS[0], width=2)),
        secondary_y=True,
    )

    fig.update_layout(title="Free Cash Flow & Cumulative FCF", **LAYOUT_BASE)
    fig.update_yaxes(title_text="Annual FCF (₽M)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative FCF (₽M)", secondary_y=True)
    return fig


# ─────────────────────────────────────────────
# Tab 12 – NPV Sensitivity Heatmap
# ─────────────────────────────────────────────
def npv_sensitivity_chart(results: dict) -> go.Figure:
    matrix = results.get("sensitivity_matrix", [[0] * 5] * 5)
    x_labels = results.get("sensitivity_growth_labels", [str(i) for i in range(5)])
    y_labels = results.get("sensitivity_wacc_labels", [str(i) for i in range(5)])

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#e74c3c"],
            [0.5, "#f9f9f9"],
            [1.0, "#27ae60"],
        ],
        zmid=0,
        text=[[f"{v:,.2f}" for v in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="NPV (₽M)"),
    ))

    fig.update_layout(
        title="NPV Sensitivity: WACC vs Revenue Growth",
        xaxis_title="Revenue Growth Rate",
        yaxis_title="WACC",
        **LAYOUT_BASE,
    )
    return fig


# ─────────────────────────────────────────────
# Tab 12 – IRR vs WACC Gauge
# ─────────────────────────────────────────────
def irr_gauge_chart(results: dict) -> go.Figure:
    irr = results.get("irr")
    wacc = float(results.get("wacc", 10))

    irr_val = (irr * 100) if irr is not None else 0.0
    wacc_val = wacc

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=irr_val,
        delta={"reference": wacc_val, "valueformat": ".1f",
               "increasing": {"color": GREEN_COLOR},
               "decreasing": {"color": RED_COLOR}},
        number={"suffix": "%", "valueformat": ".2f"},
        title={"text": "IRR vs WACC"},
        gauge={
            "axis": {"range": [0, max(irr_val * 1.5, wacc_val * 2, 30)], "ticksuffix": "%"},
            "bar": {"color": GREEN_COLOR if irr_val >= wacc_val else RED_COLOR},
            "steps": [
                {"range": [0, wacc_val], "color": "rgba(231,76,60,0.15)"},
                {"range": [wacc_val, max(irr_val * 1.5, wacc_val * 2, 30)],
                 "color": "rgba(39,174,96,0.15)"},
            ],
            "threshold": {
                "line": {"color": BLUE_COLORS[0], "width": 4},
                "thickness": 0.75,
                "value": wacc_val,
            },
        },
    ))

    fig.update_layout(margin=dict(l=30, r=30, t=60, b=30), paper_bgcolor="white")
    return fig
