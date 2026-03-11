from dash import dash_table
import pandas as pd


HEADER_STYLE = {
    "backgroundColor": "#2c3e50",
    "color": "white",
    "fontWeight": "bold",
}

CELL_STYLE = {
    "fontFamily": "'Courier New', monospace",
    "fontSize": "13px",
    "padding": "6px 12px",
    "textAlign": "right",
}

# Colours for investment-phase vs operating-phase columns
INV_HEADER_BG = "#e67e22"   # orange
INV_DATA_BG   = "#fef9f0"   # light amber
OP_HEADER_BG  = "#27ae60"   # green
OP_DATA_BG    = "#f0faf4"   # light mint


def _col_display_name(t: int, investment_years: int) -> str:
    """Return a human-readable column header that indicates the phase."""
    if t == 0:
        return "Base"
    elif t <= investment_years:
        return f"Inv {t}"
    else:
        return f"Op {t - investment_years}"


def build_table(
    line_items: dict,
    period: int,
    table_id: str = "table",
    investment_years: int = 0,
) -> dash_table.DataTable:
    """Build a DataTable with rows=line items, columns=Base / Inv N / Op N.

    Args:
        line_items:       {human_readable_label: [val_year0, val_year1, ...]}
        period:           total number of years (investment + operating)
        table_id:         HTML id for the DataTable
        investment_years: number of investment-phase columns (highlighted orange)
    """
    # Internal column IDs stay as "Year 0", "Year 1", … for row-data keys
    rows = []
    for label, values in line_items.items():
        row = {"Line Item": label}
        for t in range(period + 1):
            row[f"Year {t}"] = values[t] if t < len(values) else 0.0
        rows.append(row)

    col_ids = ["Line Item"] + [f"Year {t}" for t in range(period + 1)]
    df = pd.DataFrame(rows, columns=col_ids)

    columns = [{"name": "Line Item", "id": "Line Item", "type": "text"}]
    for t in range(period + 1):
        columns.append(
            {
                "name": _col_display_name(t, investment_years),
                "id": f"Year {t}",
                "type": "numeric",
                "format": {"specifier": ",.2f"},
            }
        )

    # Phase-specific header colours
    style_header_conditional = [
        {
            "if": {"column_id": f"Year {t}"},
            "backgroundColor": INV_HEADER_BG,
            "color": "white",
        }
        for t in range(1, investment_years + 1)
    ] + [
        {
            "if": {"column_id": f"Year {t}"},
            "backgroundColor": OP_HEADER_BG,
            "color": "white",
        }
        for t in range(investment_years + 1, period + 1)
    ]

    # Phase-specific data cell tint
    style_data_conditional = [
        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
        {
            "if": {
                "filter_query": (
                    "{Line Item} contains 'Total' or "
                    "{Line Item} contains 'EBITDA' or "
                    "{Line Item} contains 'Net Income' or "
                    "{Line Item} contains 'Free Cash'"
                ),
            },
            "fontWeight": "bold",
            "borderTop": "2px solid #2c3e50",
        },
    ] + [
        {
            "if": {"column_id": f"Year {t}"},
            "backgroundColor": INV_DATA_BG,
        }
        for t in range(1, investment_years + 1)
    ] + [
        {
            "if": {"column_id": f"Year {t}"},
            "backgroundColor": OP_DATA_BG,
        }
        for t in range(investment_years + 1, period + 1)
    ]

    return dash_table.DataTable(
        id=table_id,
        data=df.to_dict("records"),
        columns=columns,
        style_table={"overflowX": "auto", "minWidth": "100%"},
        style_header=HEADER_STYLE,
        style_header_conditional=style_header_conditional,
        style_data_conditional=style_data_conditional,
        style_cell=CELL_STYLE,
        style_cell_conditional=[
            {
                "if": {"column_id": "Line Item"},
                "textAlign": "left",
                "fontWeight": "600",
                "width": "220px",
                "minWidth": "220px",
            }
        ],
        page_action="none",
        fixed_rows={"headers": True},
    )
