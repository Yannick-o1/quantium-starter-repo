"""Dash visualiser for Soul Foods Pink Morsel sales."""

from pathlib import Path
from typing import Tuple, Union

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html


REPOSITORY_ROOT = Path(__file__).resolve().parent
DATA_FILE = REPOSITORY_ROOT / "data" / "daily_sales_data.csv"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")
REQUIRED_COLUMNS = {"sales", "date", "region"}


def load_daily_sales(
    data_file: Union[str, Path] = DATA_FILE,
) -> pd.DataFrame:
    """Load the processed transactions and aggregate sales across regions."""
    sales = pd.read_csv(data_file)
    missing_columns = REQUIRED_COLUMNS.difference(sales.columns)
    if missing_columns:
        raise ValueError(
            f"{Path(data_file).name} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    sales = sales.copy()
    sales["date"] = pd.to_datetime(sales["date"], errors="raise")
    sales["sales"] = pd.to_numeric(sales["sales"], errors="raise")

    if sales[["sales", "date", "region"]].isna().any().any():
        raise ValueError("Sales data contains missing values.")

    return (
        sales.groupby("date", as_index=False, sort=True)["sales"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )


def create_sales_figure(daily_sales: pd.DataFrame) -> go.Figure:
    """Create the daily-sales line chart and mark the price increase."""
    start_date = daily_sales["date"].min().strftime("%d %b %Y").lstrip("0")
    end_date = daily_sales["date"].max().strftime("%d %b %Y").lstrip("0")

    figure = go.Figure(
        go.Scatter(
            x=daily_sales["date"],
            y=daily_sales["sales"],
            mode="lines",
            line={"color": "#2F6B8A", "width": 2},
            hovertemplate="%{x|%d %b %Y}<br>Sales: $%{y:,.0f}<extra></extra>",
            name="Daily sales",
        )
    )

    figure.add_shape(
        type="line",
        x0=PRICE_INCREASE_DATE,
        x1=PRICE_INCREASE_DATE,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line={"color": "#9A6700", "width": 2, "dash": "dash"},
    )
    figure.add_annotation(
        x=PRICE_INCREASE_DATE,
        y=1,
        xref="x",
        yref="paper",
        text="Price increase<br>15 Jan 2021",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        xshift=8,
        yshift=-8,
        font={"color": "#7A5200", "size": 12},
        bgcolor="rgba(255, 248, 225, 0.92)",
        borderpad=5,
    )

    figure.update_layout(
        title={
            "text": (
                "Daily Pink Morsel sales"
                f"<br><sup>All regions · {start_date}–{end_date}</sup>"
            ),
            "x": 0,
            "xanchor": "left",
        },
        template="plotly_white",
        showlegend=False,
        hovermode="x unified",
        margin={"l": 72, "r": 32, "t": 90, "b": 68},
        font={"family": "Arial, sans-serif", "color": "#24323D"},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    figure.update_xaxes(
        title_text="Date",
        showgrid=False,
        showline=True,
        linecolor="#9AA6AF",
    )
    figure.update_yaxes(
        title_text="Daily sales ($)",
        tickprefix="$",
        tickformat=",.0f",
        rangemode="tozero",
        gridcolor="#E7EBEE",
        showline=True,
        linecolor="#9AA6AF",
    )

    return figure


def sales_comparison(
    daily_sales: pd.DataFrame,
) -> Tuple[float, float, float]:
    """Return mean daily sales before, after and percentage change."""
    before = daily_sales.loc[
        daily_sales["date"] < PRICE_INCREASE_DATE, "sales"
    ]
    after = daily_sales.loc[
        daily_sales["date"] >= PRICE_INCREASE_DATE, "sales"
    ]

    if before.empty or after.empty:
        raise ValueError(
            "Sales data must cover dates before and after 15 January 2021."
        )

    before_average = float(before.mean())
    after_average = float(after.mean())
    percentage_change = (after_average / before_average - 1) * 100
    return before_average, after_average, percentage_change


daily_sales = load_daily_sales()
sales_figure = create_sales_figure(daily_sales)
before_average, after_average, percentage_change = sales_comparison(daily_sales)

app = Dash(__name__, title="Pink Morsel Sales Visualiser")
server = app.server

app.layout = html.Main(
    [
        html.Header(
            [
                html.H1(
                    "Pink Morsel Sales Visualiser",
                    id="app-title",
                    style={"margin": "0", "fontSize": "2rem"},
                ),
                html.P(
                    "Did sales increase after the price change on "
                    "15 January 2021?",
                    style={
                        "margin": "0.55rem 0 0",
                        "color": "#52616B",
                        "fontSize": "1.05rem",
                    },
                ),
            ]
        ),
        html.Section(
            [
                html.Strong(
                    f"Yes — average daily sales were "
                    f"{percentage_change:.1f}% higher after the increase.",
                    id="sales-conclusion",
                    style={"display": "block", "fontSize": "1.1rem"},
                ),
                html.Span(
                    f"Before: ${before_average:,.0f} per day · "
                    f"From 15 Jan 2021: ${after_average:,.0f} per day",
                    style={"color": "#52616B"},
                ),
            ],
            style={
                "margin": "1.5rem 0",
                "padding": "1rem 1.2rem",
                "backgroundColor": "#F3F7F9",
                "borderLeft": "4px solid #2F6B8A",
                "borderRadius": "4px",
            },
        ),
        dcc.Graph(
            id="sales-line-chart",
            figure=sales_figure,
            config={"displayModeBar": False, "responsive": True},
            style={"height": "68vh", "minHeight": "500px"},
        ),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "2rem clamp(1rem, 4vw, 3rem)",
        "fontFamily": "Arial, sans-serif",
        "color": "#24323D",
    },
)


if __name__ == "__main__":
    app.run(debug=True)
