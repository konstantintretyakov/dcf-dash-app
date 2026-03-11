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


def build_table(line_items: dict, period: int, table_id: str = "table") -> dash_table.DataTable:
    """Build a DataTable with rows=line items, columns=Year 0..N.

    Args:
        line_items: {human_readable_label: [val_year0, val_year1, ...]}
        period: number of projection years
        table_id: HTML id for the DataTable
    """
    col_ids = ["Line Item"] + [f"Year {t}" for t in range(period + 1)]

    rows = []
    for label, values in line_items.items():
        row = {"Line Item": label}
        for t in range(period + 1):
            row[f"Year {t}"] = values[t] if t < len(values) else 0.0
        rows.append(row)

    df = pd.DataFrame(rows, columns=col_ids)

    columns = [{"name": "Line Item", "id": "Line Item", "type": "text"}]
    for t in range(period + 1):
        columns.append(
            {
                "name": f"Year {t}",
                "id": f"Year {t}",
                "type": "numeric",
                "format": {"specifier": ",.2f"},
            }
        )

    return dash_table.DataTable(
        id=table_id,
        data=df.to_dict("records"),
        columns=columns,
        style_table={"overflowX": "auto", "minWidth": "100%"},
        style_header=HEADER_STYLE,
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
            {
                "if": {
                    "filter_query": "{Line Item} contains 'Total' or {Line Item} contains 'EBITDA' or {Line Item} contains 'Net Income' or {Line Item} contains 'Free Cash'",
                },
                "fontWeight": "bold",
                "borderTop": "2px solid #2c3e50",
            },
        ],
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
