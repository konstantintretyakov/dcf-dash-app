"""DCF Financial Model — Plotly Dash App (OOP Architecture)
Run: python app.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from model.dcf_model import DCFModel
from components.tables import build_table
from components.charts import (
    revenue_chart, opex_chart, fa_chart, wc_chart, tax_chart,
    debt_chart, equity_chart, pnl_chart, cashflow_chart,
    balance_sheet_chart, fcf_chart, npv_sensitivity_chart, irr_gauge_chart,
)

# ─────────────────────────────────────────────
# App Initialisation
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="DCF Financial Model",
    suppress_callback_exceptions=True,
)
server = app.server

dcf_model = DCFModel()

# ─────────────────────────────────────────────
# Default Inputs per Project Sphere
# ─────────────────────────────────────────────
SPHERE_DEFAULTS = {
    "production": {
        # General manufacturing / industrial production
        "vat_rate": 22,
        "investment_years": 1,
        "operating_years": 5,
        "base_revenue": 1.0,
        "revenue_growth_rate": 12,
        "cogs_pct": 35,
        "opex_pct": 20,
        "annual_capex": 0.08,
        "intangibles_investment": 0.03,
        "useful_life_years": 10,
        "amortization_period": 5,
        "dso": 30,
        "dpo": 30,
        "dio": 45,
        "tax_rate": 25,
        "initial_debt": 0.3,
        "interest_rate": 6,
        "repayment_type": "Equal",
        "new_debt_annual": 0,
        "initial_equity": 0.5,
        "annual_equity_injection": 0,
        "dividends_pct": 20,
        "wacc": 10,
        "initial_cash": 0.1,
        "initial_investment": 0,  # Year-0 seed; investment-phase FCFs capture build costs
    },
    "toll-road": {
        # Concession-based infrastructure; near-cash tolls, heavy debt, long life
        "vat_rate": 22,
        "investment_years": 3,
        "operating_years": 12,
        "base_revenue": 5.0,
        "revenue_growth_rate": 4,
        "cogs_pct": 8.78,
        "opex_pct": 14.05,
        "annual_capex": 0.4,
        "intangibles_investment": 0.15,      # concession rights
        "useful_life_years": 30,
        "amortization_period": 20,
        "dso": 3,                            # tolls collected on the spot
        "dpo": 45,
        "dio": 0,                            # no inventory
        "tax_rate": 25,
        "initial_debt": 8.0,
        "interest_rate": 5,
        "repayment_type": "Equal",
        "new_debt_annual": 0,
        "initial_equity": 3.0,
        "annual_equity_injection": 0,
        "dividends_pct": 40,
        "wacc": 7,
        "initial_cash": 0.5,
        "initial_investment": 0,
        "avg_daily_traffic": 74096,
        "tariff_rub_per_km": 58.51,
        "road_length_km": 16.2,
        "tariff_growth_rate": 3.98,
        "traffic_growth_rate": 0.78,
    },
    "agriculture": {
        # Farm / agribusiness; long harvest cycles, seasonal inventory, lower tax
        "vat_rate": 22,
        "investment_years": 2,
        "operating_years": 10,
        "base_revenue": 0.8,
        "revenue_growth_rate": 5,
        "cogs_pct": 55,
        "opex_pct": 15,
        "annual_capex": 0.06,
        "intangibles_investment": 0.01,      # land-use permits
        "useful_life_years": 15,
        "amortization_period": 10,
        "dso": 30,
        "dpo": 30,
        "dio": 120,                          # long harvest & storage cycle
        "tax_rate": 25,
        "initial_debt": 0.35,
        "interest_rate": 6,
        "repayment_type": "Equal",
        "new_debt_annual": 0,
        "initial_equity": 0.3,
        "annual_equity_injection": 0,
        "dividends_pct": 20,
        "wacc": 9,
        "initial_cash": 0.1,
        "initial_investment": 0,
    },
    "mining": {
        # Extractive industry; Year-0 capex already embedded in opening NFA;
        # ongoing sustaining capex is low, making annual FCF strongly positive.
        "vat_rate": 22,
        "investment_years": 3,
        "operating_years": 12,
        "base_revenue": 8.0,
        "revenue_growth_rate": 3,
        "cogs_pct": 50,
        "opex_pct": 18,
        "annual_capex": 0.5,                 # sustaining capex only
        "intangibles_investment": 0.1,       # exploration licence renewals
        "useful_life_years": 20,
        "amortization_period": 10,
        "dso": 15,
        "dpo": 45,
        "dio": 30,
        "tax_rate": 25,
        "initial_debt": 3.0,
        "interest_rate": 6,
        "repayment_type": "Equal",
        "new_debt_annual": 0,
        "initial_equity": 3.0,
        "annual_equity_injection": 0,
        "dividends_pct": 30,
        "wacc": 11,
        "initial_cash": 1.0,
        "initial_investment": 0,
    },
    "port": {
        # Port / terminal; stable throughput fees; WACC reflects infrastructure risk
        "vat_rate": 22,
        "investment_years": 4,
        "operating_years": 16,
        "base_revenue": 3.0,
        "revenue_growth_rate": 5,
        "cogs_pct": 10,
        "opex_pct": 25,
        "annual_capex": 0.3,
        "intangibles_investment": 0.05,      # concession / operating licences
        "useful_life_years": 25,
        "amortization_period": 15,
        "dso": 30,
        "dpo": 60,
        "dio": 10,
        "tax_rate": 25,
        "initial_debt": 6.0,
        "interest_rate": 5,
        "repayment_type": "Equal",
        "new_debt_annual": 0,
        "initial_equity": 3.5,
        "annual_equity_injection": 0,
        "dividends_pct": 35,
        "wacc": 6,                           # infrastructure WACC
        "initial_cash": 0.5,
        "initial_investment": 0,
    },
}

# Alias used by any code that still references DEFAULTS
DEFAULTS = SPHERE_DEFAULTS["production"]

SPHERE_OPTIONS = [
    {"label": "🏭  Production",   "value": "production"},
    {"label": "🛣️  Toll Road",    "value": "toll-road"},
    {"label": "🌾  Agriculture",  "value": "agriculture"},
    {"label": "⛏️  Mining",       "value": "mining"},
    {"label": "🚢  Port",         "value": "port"},
]


# ─────────────────────────────────────────────
# Helper: format currency
# ─────────────────────────────────────────────
def fmt_currency(v):
    if v is None:
        return "N/A"
    sign = "-" if v < 0 else ""
    return f"{sign}₽{abs(v):,.2f}M"


def fmt_pct(v):
    if v is None:
        return "N/A"
    return f"{v * 100:.2f}%"


def fmt_years(v):
    if v is None:
        return "N/A"
    return f"{v:.1f} yrs"


# ─────────────────────────────────────────────
# Layout Helpers
# ─────────────────────────────────────────────
def input_group(label, input_id, value, input_type="number", suffix=None, min_val=None, step=None):
    addon = dbc.InputGroupText(suffix) if suffix else None
    children = [
        dbc.Input(
            id=input_id,
            type=input_type,
            value=value,
            debounce=True,
            **({"min": min_val} if min_val is not None else {}),
            **({"step": step} if step is not None else {}),
        )
    ]
    if addon:
        children.append(addon)
    return dbc.Col([
        dbc.Label(label, className="fw-semibold small"),
        dbc.InputGroup(children, size="sm"),
    ], md=6, className="mb-3")


def section_header(title):
    return html.H6(title, className="text-primary border-bottom pb-1 mt-3 mb-2 fw-bold")


# ─────────────────────────────────────────────
# Tab 1 – Inputs Panel
# ─────────────────────────────────────────────
def build_inputs_tab():
    sphere_card = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Project Sphere", className="fw-bold fs-6 mb-2"),
                    html.Div(
                        dbc.RadioItems(
                            id="inp-sphere",
                            options=SPHERE_OPTIONS,
                            value="production",
                            inline=True,
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary me-2 mb-1",
                            labelCheckedClassName="btn btn-primary me-2 mb-1",
                        ),
                        className="d-flex flex-wrap",
                    ),
                ]),
            ]),
        ]),
        className="mb-4 border-primary",
        style={"borderWidth": "2px"},
    )

    return dbc.Container([
        sphere_card,
        dbc.Row([
            dbc.Col([
                section_header("📈 Revenue"),
                html.Div(id="div-base-revenue", children=[
                    dbc.Row([
                        input_group("Base Revenue (Year 1, ₽M)", "inp-base-revenue",
                                    DEFAULTS["base_revenue"], step=0.01),
                    ]),
                ]),
                html.Div(id="div-toll-revenue", style={"display": "none"}, children=[
                    dbc.Row([
                        input_group("Avg Daily Traffic (vehicles/day)", "inp-adt",
                                    74096, step=100, min_val=0),
                        input_group("Tariff (₽/km, excl. VAT)", "inp-tariff",
                                    58.51, step=0.1, min_val=0),
                        input_group("Road Length (km)", "inp-road-length",
                                    16.2, step=0.1, min_val=0.1),
                        dbc.Col([
                            dbc.Label("Computed Base Revenue", className="fw-semibold small text-muted"),
                            html.Div(id="div-computed-revenue", className="fw-bold text-primary mt-1"),
                        ], md=6, className="mb-3"),
                    ]),
                ]),
                html.Div(id="div-revenue-growth", children=[
                    dbc.Row([
                        input_group("Revenue Growth Rate", "inp-growth-rate",
                                    DEFAULTS["revenue_growth_rate"], suffix="%", step=0.5),
                    ]),
                ]),
                html.Div(id="div-toll-growth", style={"display": "none"}, children=[
                    dbc.Row([
                        input_group("Tariff Growth Rate", "inp-tariff-growth",
                                    3.98, suffix="%", step=0.1),
                        input_group("Traffic Growth Rate", "inp-traffic-growth",
                                    0.78, suffix="%", step=0.1),
                    ]),
                ]),
                section_header("💸 Operating Expenses"),
                dbc.Row([
                    input_group("COGS % of Revenue", "inp-cogs-pct",
                                DEFAULTS["cogs_pct"], suffix="%", step=0.5),
                    input_group("OpEx % of Revenue", "inp-opex-pct",
                                DEFAULTS["opex_pct"], suffix="%", step=0.5),
                ]),
                section_header("🏗️ Fixed Assets & Intangibles"),
                dbc.Row([
                    input_group("Annual CapEx (₽M)", "inp-annual-capex",
                                DEFAULTS["annual_capex"], step=0.01),
                    input_group("Annual Intangibles Investment (₽M)", "inp-intangibles",
                                DEFAULTS["intangibles_investment"], step=0.01),
                    input_group("Useful Life (years)", "inp-useful-life",
                                DEFAULTS["useful_life_years"], min_val=1, step=1),
                    input_group("Amortization Period (years)", "inp-amort-period",
                                DEFAULTS["amortization_period"], min_val=1, step=1),
                ]),
                section_header("🔄 Working Capital"),
                dbc.Row([
                    input_group("DSO (days)", "inp-dso", DEFAULTS["dso"], min_val=0, step=1),
                    input_group("DPO (days)", "inp-dpo", DEFAULTS["dpo"], min_val=0, step=1),
                    input_group("DIO (days)", "inp-dio", DEFAULTS["dio"], min_val=0, step=1),
                ]),
            ], md=6),

            dbc.Col([
                section_header("🧾 Taxes"),
                dbc.Row([
                    input_group("Tax Rate", "inp-tax-rate", DEFAULTS["tax_rate"],
                                suffix="%", step=0.5),
                    input_group("VAT Rate", "inp-vat-rate", 22,
                                suffix="%", step=0.5),
                ]),
                section_header("🏦 Debt Financing"),
                dbc.Row([
                    input_group("Initial Debt (₽M)", "inp-initial-debt",
                                DEFAULTS["initial_debt"], step=0.01),
                    input_group("Interest Rate", "inp-interest-rate",
                                DEFAULTS["interest_rate"], suffix="%", step=0.25),
                    input_group("New Annual Debt Issuance (₽M)", "inp-new-debt",
                                DEFAULTS["new_debt_annual"], step=0.01),
                    dbc.Col([
                        dbc.Label("Repayment Schedule", className="fw-semibold small"),
                        dcc.Dropdown(
                            id="inp-repayment-type",
                            options=[
                                {"label": "Equal Annual Repayment", "value": "Equal"},
                                {"label": "Bullet (Lump Sum at Maturity)", "value": "Bullet"},
                            ],
                            value=DEFAULTS["repayment_type"],
                            clearable=False,
                        ),
                    ], md=6, className="mb-3"),
                ]),
                section_header("💼 Equity Financing"),
                dbc.Row([
                    input_group("Initial Equity (₽M)", "inp-initial-equity",
                                DEFAULTS["initial_equity"], step=0.01),
                    input_group("Annual Equity Injection (₽M)", "inp-equity-injection",
                                DEFAULTS["annual_equity_injection"], step=0.01),
                    input_group("Dividend Payout %", "inp-dividends-pct",
                                DEFAULTS["dividends_pct"], suffix="%", step=1),
                ]),
                section_header("🎯 Valuation"),
                dbc.Row([
                    input_group("WACC", "inp-wacc", DEFAULTS["wacc"], suffix="%", step=0.25),
                    input_group("Initial Investment (₽M)", "inp-initial-investment",
                                DEFAULTS["initial_investment"], step=0.01),
                    input_group("Initial Cash Balance (₽M)", "inp-initial-cash",
                                DEFAULTS["initial_cash"], step=0.01),
                ]),
                section_header("📅 Projection Horizon"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label(
                            [html.Span("🏗️ ", style={"color": "#e67e22"}),
                             "Investment Phase (years)"],
                            className="fw-semibold small",
                        ),
                        dbc.InputGroup([
                            dbc.Input(
                                id="inp-investment-years",
                                type="number",
                                value=DEFAULTS["investment_years"],
                                min=0, max=15, step=1,
                                debounce=True,
                            ),
                            dbc.InputGroupText("yrs"),
                        ], size="sm"),
                        dbc.FormText("Pre-revenue construction / ramp-up period"),
                    ], md=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label(
                            [html.Span("📈 ", style={"color": "#27ae60"}),
                             "Operating Phase (years)"],
                            className="fw-semibold small",
                        ),
                        dbc.InputGroup([
                            dbc.Input(
                                id="inp-operating-years",
                                type="number",
                                value=DEFAULTS["operating_years"],
                                min=1, max=30, step=1,
                                debounce=True,
                            ),
                            dbc.InputGroupText("yrs"),
                        ], size="sm"),
                        dbc.FormText("Revenue-generating operations period"),
                    ], md=4, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Total", className="fw-semibold small text-muted"),
                        html.Div(
                            dbc.Badge(
                                id="badge-total-years",
                                children=f"{DEFAULTS['investment_years'] + DEFAULTS['operating_years']} yrs",
                                color="secondary",
                                className="fs-6 px-3 py-2",
                            ),
                            className="mt-1",
                        ),
                    ], md=2, className="mb-3"),
                ]),
            ], md=6),
        ]),

        dbc.Row([
            dbc.Col(width=4),
            dbc.Col([
                dbc.Button(
                    "▶ Run Model",
                    id="btn-run",
                    color="success",
                    size="lg",
                    className="w-100 mt-3 fw-bold",
                    n_clicks=0,
                ),
            ], md=4),
            dbc.Col(width=4),
        ]),
        html.Div(id="run-status", className="mt-2 text-center"),
    ], fluid=True, className="py-3")


# ─────────────────────────────────────────────
# Tab 12 – KPI Cards
# ─────────────────────────────────────────────
def kpi_card(title, value_id, icon, color):
    return dbc.Card([
        dbc.CardBody([
            html.P([html.Span(icon + " "), title], className="text-muted small mb-1"),
            html.H3(id=value_id, className=f"fw-bold text-{color} mb-0"),
        ])
    ], className="shadow-sm h-100 text-center")


# ─────────────────────────────────────────────
# App Layout
# ─────────────────────────────────────────────
NAVBAR = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            html.Span([
                html.Span("📊 ", style={"fontSize": "1.4rem"}),
                "DCF Financial Model",
            ]),
            className="fw-bold fs-4 text-white",
        ),
        html.Small("Interactive Discounted Cash Flow Analyser", className="text-white-50"),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-0",
    sticky="top",
)

TABS = dbc.Tabs(
    id="main-tabs",
    children=[
        dbc.Tab(build_inputs_tab(), label="📥 Inputs", tab_id="tab-inputs"),
        dbc.Tab(html.Div(id="tab-revenue-content"), label="📈 Revenues", tab_id="tab-revenues"),
        dbc.Tab(html.Div(id="tab-opex-content"), label="💸 OpEx", tab_id="tab-opex"),
        dbc.Tab(html.Div(id="tab-fa-content"), label="🏗️ FA & Intangibles", tab_id="tab-fa"),
        dbc.Tab(html.Div(id="tab-wc-content"), label="🔄 Working Capital", tab_id="tab-wc"),
        dbc.Tab(html.Div(id="tab-tax-content"), label="🧾 Taxes", tab_id="tab-taxes"),
        dbc.Tab(html.Div(id="tab-debt-content"), label="🏦 Debt", tab_id="tab-debt"),
        dbc.Tab(html.Div(id="tab-equity-content"), label="💼 Equity", tab_id="tab-equity"),
        dbc.Tab(html.Div(id="tab-pnl-content"), label="📊 P&L", tab_id="tab-pnl"),
        dbc.Tab(html.Div(id="tab-cf-content"), label="💰 Cash Flow", tab_id="tab-cf"),
        dbc.Tab(html.Div(id="tab-bs-content"), label="⚖️ Balance Sheet", tab_id="tab-bs"),
        dbc.Tab(html.Div(id="tab-eval-content"), label="🎯 Evaluation", tab_id="tab-eval"),
    ],
    active_tab="tab-inputs",
    className="mt-0",
)

app.layout = html.Div([
    NAVBAR,
    dcc.Store(id="store-results"),
    dcc.Store(id="store-inputs"),
    TABS,
])


# ─────────────────────────────────────────────
# Callback: Sphere → Populate Inputs
# ─────────────────────────────────────────────
@callback(
    Output("badge-total-years", "children"),
    Input("inp-investment-years", "value"),
    Input("inp-operating-years", "value"),
)
def update_total_years_badge(inv, op):
    total = (inv or 0) + (op or 0)
    return f"{total} yrs"


@callback(
    Output("div-base-revenue", "style"),
    Output("div-toll-revenue", "style"),
    Output("div-revenue-growth", "style"),
    Output("div-toll-growth", "style"),
    Input("inp-sphere", "value"),
)
def toggle_revenue_inputs(sphere):
    if sphere == "toll-road":
        return {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}, {"display": "block"}, {"display": "none"}


@callback(
    Output("div-computed-revenue", "children"),
    Input("inp-adt", "value"),
    Input("inp-tariff", "value"),
    Input("inp-road-length", "value"),
)
def update_computed_revenue(adt, tariff, length):
    try:
        rev = (float(adt or 0) * float(tariff or 0) * float(length or 0) * 365) / 1_000_000
        return f"₽{round(rev):,}M / year"
    except Exception:
        return "N/A"


@callback(
    Output("inp-vat-rate", "value"),
    Output("inp-investment-years", "value"),
    Output("inp-operating-years", "value"),
    Output("inp-base-revenue", "value"),
    Output("inp-growth-rate", "value"),
    Output("inp-cogs-pct", "value"),
    Output("inp-opex-pct", "value"),
    Output("inp-annual-capex", "value"),
    Output("inp-intangibles", "value"),
    Output("inp-useful-life", "value"),
    Output("inp-amort-period", "value"),
    Output("inp-dso", "value"),
    Output("inp-dpo", "value"),
    Output("inp-dio", "value"),
    Output("inp-tax-rate", "value"),
    Output("inp-initial-debt", "value"),
    Output("inp-interest-rate", "value"),
    Output("inp-repayment-type", "value"),
    Output("inp-new-debt", "value"),
    Output("inp-initial-equity", "value"),
    Output("inp-equity-injection", "value"),
    Output("inp-dividends-pct", "value"),
    Output("inp-wacc", "value"),
    Output("inp-initial-investment", "value"),
    Output("inp-initial-cash", "value"),
    Output("inp-adt", "value"),
    Output("inp-tariff", "value"),
    Output("inp-road-length", "value"),
    Output("inp-tariff-growth", "value"),
    Output("inp-traffic-growth", "value"),
    Input("inp-sphere", "value"),
)
def update_sphere_inputs(sphere):
    d = SPHERE_DEFAULTS.get(sphere, DEFAULTS)
    return (
        d.get("vat_rate", 20),
        d["investment_years"],
        d["operating_years"],
        d["base_revenue"],
        d["revenue_growth_rate"],
        d["cogs_pct"],
        d["opex_pct"],
        d["annual_capex"],
        d["intangibles_investment"],
        d["useful_life_years"],
        d["amortization_period"],
        d["dso"],
        d["dpo"],
        d["dio"],
        d["tax_rate"],
        d["initial_debt"],
        d["interest_rate"],
        d["repayment_type"],
        d["new_debt_annual"],
        d["initial_equity"],
        d["annual_equity_injection"],
        d["dividends_pct"],
        d["wacc"],
        d["initial_investment"],
        d["initial_cash"],
        d.get("avg_daily_traffic", 74096),
        d.get("tariff_rub_per_km", 58.51),
        d.get("road_length_km", 16.2),
        d.get("tariff_growth_rate", 3.98),
        d.get("traffic_growth_rate", 0.78),
    )


# ─────────────────────────────────────────────
# Callback: Run Model → Store Results
# ─────────────────────────────────────────────
@callback(
    Output("store-results", "data"),
    Output("run-status", "children"),
    Input("btn-run", "n_clicks"),
    State("inp-investment-years", "value"),
    State("inp-operating-years", "value"),
    State("inp-base-revenue", "value"),
    State("inp-growth-rate", "value"),
    State("inp-cogs-pct", "value"),
    State("inp-opex-pct", "value"),
    State("inp-annual-capex", "value"),
    State("inp-intangibles", "value"),
    State("inp-useful-life", "value"),
    State("inp-amort-period", "value"),
    State("inp-dso", "value"),
    State("inp-dpo", "value"),
    State("inp-dio", "value"),
    State("inp-tax-rate", "value"),
    State("inp-initial-debt", "value"),
    State("inp-interest-rate", "value"),
    State("inp-repayment-type", "value"),
    State("inp-new-debt", "value"),
    State("inp-initial-equity", "value"),
    State("inp-equity-injection", "value"),
    State("inp-dividends-pct", "value"),
    State("inp-wacc", "value"),
    State("inp-initial-investment", "value"),
    State("inp-initial-cash", "value"),
    State("inp-vat-rate", "value"),
    State("inp-sphere", "value"),
    State("inp-adt", "value"),
    State("inp-tariff", "value"),
    State("inp-road-length", "value"),
    State("inp-tariff-growth", "value"),
    State("inp-traffic-growth", "value"),
    prevent_initial_call=False,
)
def run_model(n_clicks, *args):
    keys = [
        "investment_years", "operating_years",
        "base_revenue", "revenue_growth_rate",
        "cogs_pct", "opex_pct", "annual_capex", "intangibles_investment",
        "useful_life_years", "amortization_period",
        "dso", "dpo", "dio", "tax_rate",
        "initial_debt", "interest_rate", "repayment_type", "new_debt_annual",
        "initial_equity", "annual_equity_injection", "dividends_pct",
        "wacc", "initial_investment", "initial_cash",
        "vat_rate",
    ]
    sphere = args[len(keys)]
    adt = args[len(keys) + 1]
    tariff = args[len(keys) + 2]
    road_length = args[len(keys) + 3]
    tariff_growth = args[len(keys) + 4]
    traffic_growth = args[len(keys) + 5]

    inputs = {}
    for key, val in zip(keys, args):
        inputs[key] = val if val is not None else DEFAULTS.get(key, 0)

    if sphere == "toll-road":
        inputs["base_revenue"] = (
            float(adt or 0) * float(tariff or 0) * float(road_length or 0) * 365
        ) / 1_000_000
        tg = float(tariff_growth or 0) / 100
        trg = float(traffic_growth or 0) / 100
        inputs["revenue_growth_rate"] = ((1 + tg) * (1 + trg) - 1) * 100

    try:
        results = dcf_model.run(inputs)
        status = dbc.Alert("✅ Model computed successfully.", color="success",
                           dismissable=True, duration=3000, className="py-1")
        return results, status
    except Exception as e:
        status = dbc.Alert(f"❌ Error: {str(e)}", color="danger", dismissable=True)
        return {}, status


# ─────────────────────────────────────────────
# Helper: tab layout builder
# ─────────────────────────────────────────────
def tab_layout(table, chart, extra_charts=None):
    children = [
        html.Div(table, className="mb-3"),
        dcc.Graph(figure=chart, config={"displayModeBar": True}),
    ]
    if extra_charts:
        for c in extra_charts:
            children.append(dcc.Graph(figure=c, config={"displayModeBar": True}))
    return dbc.Container(children, fluid=True, className="py-3")


# ─────────────────────────────────────────────
# Callback: Update all result tabs from store
# ─────────────────────────────────────────────
@callback(
    Output("tab-revenue-content", "children"),
    Output("tab-opex-content", "children"),
    Output("tab-fa-content", "children"),
    Output("tab-wc-content", "children"),
    Output("tab-tax-content", "children"),
    Output("tab-debt-content", "children"),
    Output("tab-equity-content", "children"),
    Output("tab-pnl-content", "children"),
    Output("tab-cf-content", "children"),
    Output("tab-bs-content", "children"),
    Output("tab-eval-content", "children"),
    Input("store-results", "data"),
    prevent_initial_call=False,
)
def update_all_tabs(results):
    if not results:
        placeholder = dbc.Alert(
            "Click '▶ Run Model' on the Inputs tab to compute results.",
            color="info", className="m-4",
        )
        return [placeholder] * 11

    period = results.get("projection_years", 5)
    inv = results.get("investment_years", 0)

    def tbl(items, tid):
        return build_table(items, period, tid, investment_years=inv)

    # ── Revenues ──
    rev_items = {
        "Revenue (₽M)": results.get("revenue", []),
    }
    rev_tab = tab_layout(tbl(rev_items, "tbl-revenue"), revenue_chart(results))

    # ── OpEx ──
    opex_items = {
        "Revenue (₽M)": results.get("revenue", []),
        "COGS (₽M)": results.get("cogs", []),
        "Gross Profit (₽M)": results.get("gross_profit", []),
        "OpEx (₽M)": results.get("opex", []),
        "EBITDA (₽M)": results.get("ebitda", []),
    }
    opex_tab = tab_layout(tbl(opex_items, "tbl-opex"), opex_chart(results))

    # ── FA ──
    fa_items = {
        "Annual CapEx (₽M)": results.get("capex", []),
        "Intangibles Investment (₽M)": results.get("intangibles_investment", []),
        "Depreciation (₽M)": results.get("depreciation", []),
        "Amortization (₽M)": results.get("amortization", []),
        "Net Fixed Assets (₽M)": results.get("net_fixed_assets", []),
        "Net Intangibles (₽M)": results.get("net_intangibles", []),
    }
    fa_tab = tab_layout(tbl(fa_items, "tbl-fa"), fa_chart(results))

    # ── Working Capital ──
    wc_items = {
        "Accounts Receivable (₽M)": results.get("accounts_receivable", []),
        "Inventory (₽M)": results.get("inventory", []),
        "Accounts Payable (₽M)": results.get("accounts_payable", []),
        "Net Working Capital (₽M)": results.get("net_working_capital", []),
        "Change in NWC (₽M)": results.get("change_in_wc", []),
    }
    wc_tab = tab_layout(tbl(wc_items, "tbl-wc"), wc_chart(results))

    # ── Taxes ──
    tax_items = {
        "EBITDA (₽M)": results.get("ebitda", []),
        "Depreciation (₽M)": results.get("depreciation", []),
        "Amortization (₽M)": results.get("amortization", []),
        "EBIT (₽M)": results.get("ebit", []),
        "Interest Expense (₽M)": results.get("interest_expense", []),
        "EBT (₽M)": results.get("ebt", []),
        "Tax (₽M)": results.get("tax", []),
        "NOPAT (₽M)": results.get("nopat", []),
        "Net Income (₽M)": results.get("net_income", []),
    }
    tax_tab = tab_layout(tbl(tax_items, "tbl-tax"), tax_chart(results))

    # ── Debt ──
    debt_items = {
        "Debt Balance (₽M)": results.get("debt_balance", []),
        "Interest Expense (₽M)": results.get("interest_expense", []),
        "Principal Repayment (₽M)": results.get("principal_repayment", []),
        "New Debt Issuance (₽M)": results.get("new_debt_issuance", []),
    }
    debt_tab = tab_layout(tbl(debt_items, "tbl-debt"), debt_chart(results))

    # ── Equity ──
    equity_items = {
        "Paid-in Capital (₽M)": results.get("paid_in_capital", []),
        "Equity Injections (₽M)": results.get("equity_injections", []),
        "Retained Earnings (₽M)": results.get("retained_earnings", []),
        "Dividends (₽M)": results.get("dividends", []),
        "Cumulative Equity (₽M)": results.get("cumulative_equity", []),
    }
    equity_tab = tab_layout(tbl(equity_items, "tbl-equity"), equity_chart(results))

    # ── P&L ──
    pnl_items = {
        "Revenue (₽M)": results.get("revenue", []),
        "COGS (₽M)": results.get("cogs", []),
        "Gross Profit (₽M)": results.get("gross_profit", []),
        "OpEx (₽M)": results.get("opex", []),
        "EBITDA (₽M)": results.get("ebitda", []),
        "Depreciation (₽M)": results.get("depreciation", []),
        "Amortization (₽M)": results.get("amortization", []),
        "EBIT (₽M)": results.get("ebit", []),
        "Interest Expense (₽M)": results.get("interest_expense", []),
        "EBT (₽M)": results.get("ebt", []),
        "Tax (₽M)": results.get("tax", []),
        "Net Income (₽M)": results.get("net_income", []),
    }
    pnl_tab = tab_layout(tbl(pnl_items, "tbl-pnl"), pnl_chart(results))

    # ── Cash Flow ──
    cf_items = {
        "Operating CF (₽M)": results.get("operating_cf", []),
        "  incl. VAT CF (₽M)": results.get("vat_cf", []),
        "Investing CF (₽M)": results.get("investing_cf", []),
        "Financing CF (₽M)": results.get("financing_cf", []),
        "Free Cash Flow (₽M)": results.get("free_cash_flow", []),
        "Net Cash Flow (₽M)": results.get("net_cash_flow", []),
        "Cash Balance (₽M)": results.get("cash_balance", []),
    }
    cf_tab = tab_layout(tbl(cf_items, "tbl-cf"), cashflow_chart(results))

    # ── Balance Sheet ──
    balance_checks = results.get("bs_balance_check", [True] * (period + 1))
    balance_diffs = results.get("bs_balance_diff", [0.0] * (period + 1))
    all_balanced = all(balance_checks)
    balance_indicator = dbc.Alert(
        "✅ Balance Sheet balances for all years." if all_balanced
        else f"⚠️ Balance Sheet imbalance detected. Max diff: ₽{max(abs(d) for d in balance_diffs):,.4f}M",
        color="success" if all_balanced else "warning",
        className="mb-2 py-2",
    )
    bs_items = {
        "Cash (₽M)": results.get("cash_balance", []),
        "Accounts Receivable (₽M)": results.get("accounts_receivable", []),
        "Inventory (₽M)": results.get("inventory", []),
        "Net Fixed Assets (₽M)": results.get("net_fixed_assets", []),
        "Net Intangibles (₽M)": results.get("net_intangibles", []),
        "Total Assets (₽M)": results.get("bs_total_assets", []),
        "Accounts Payable (₽M)": results.get("accounts_payable", []),
        "Debt Balance (₽M)": results.get("debt_balance", []),
        "Total Liabilities (₽M)": results.get("bs_total_liabilities", []),
        "Paid-in Capital (₽M)": results.get("paid_in_capital", []),
        "Retained Earnings (₽M)": results.get("retained_earnings", []),
        "Total Equity (₽M)": results.get("bs_total_equity", []),
    }
    bs_tab = dbc.Container([
        balance_indicator,
        html.Div(tbl(bs_items, "tbl-bs"), className="mb-3"),
        dcc.Graph(figure=balance_sheet_chart(results)),
    ], fluid=True, className="py-3")

    # ── Evaluation ──
    npv = results.get("npv")
    irr = results.get("irr")
    pbp = results.get("pbp")
    dpbp = results.get("dpbp")
    wacc = float(results.get("wacc", 10))

    npv_color = "success" if (npv is not None and npv >= 0) else "danger"
    irr_color = "success" if (irr is not None and irr * 100 >= wacc) else "danger"

    kpi_row = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("📐 Net Present Value", className="text-muted small mb-1"),
                html.H3(fmt_currency(npv), className=f"fw-bold text-{npv_color} mb-0"),
            ])
        ], className="shadow-sm text-center h-100"), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("📈 Internal Rate of Return", className="text-muted small mb-1"),
                html.H3(fmt_pct(irr), className=f"fw-bold text-{irr_color} mb-0"),
                html.Small(f"WACC: {wacc:.1f}%", className="text-muted"),
            ])
        ], className="shadow-sm text-center h-100"), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("⏱️ Payback Period", className="text-muted small mb-1"),
                html.H3(fmt_years(pbp), className="fw-bold text-info mb-0"),
            ])
        ], className="shadow-sm text-center h-100"), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.P("⏳ Discounted Payback Period", className="text-muted small mb-1"),
                html.H3(fmt_years(dpbp), className="fw-bold text-secondary mb-0"),
            ])
        ], className="shadow-sm text-center h-100"), md=3),
    ], className="mb-4 g-3")

    eval_tab = dbc.Container([
        kpi_row,
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fcf_chart(results)), md=8),
            dbc.Col(dcc.Graph(figure=irr_gauge_chart(results)), md=4),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=npv_sensitivity_chart(results)), md=12),
        ]),
    ], fluid=True, className="py-3")

    return (
        rev_tab, opex_tab, fa_tab, wc_tab, tax_tab,
        debt_tab, equity_tab, pnl_tab, cf_tab, bs_tab, eval_tab,
    )


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
