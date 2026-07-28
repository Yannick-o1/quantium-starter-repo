"""Interactive Dash visualiser for Soul Foods Pink Morsel sales."""

from pathlib import Path
from typing import Tuple, Union

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html


REPOSITORY_ROOT = Path(__file__).resolve().parent
DATA_FILE = REPOSITORY_ROOT / "data" / "daily_sales_data.csv"
PRICE_INCREASE_DATE = pd.Timestamp("2021-01-15")
REQUIRED_COLUMNS = {"sales", "date", "region"}
REGION_OPTIONS = ("north", "east", "south", "west", "all")
VALID_REGIONS = set(REGION_OPTIONS[:-1])


def load_sales_data(
    data_file: Union[str, Path] = DATA_FILE,
) -> pd.DataFrame:
    """Load processed sales at a daily, regional grain."""
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
    sales["region"] = (
        sales["region"].astype(str).str.strip().str.casefold()
    )

    if sales[["sales", "date", "region"]].isna().any().any():
        raise ValueError("Sales data contains missing values.")

    unexpected_regions = set(sales["region"].unique()).difference(
        VALID_REGIONS
    )
    if unexpected_regions:
        raise ValueError(
            f"Sales data contains unexpected regions: "
            f"{sorted(unexpected_regions)}"
        )

    return (
        sales.groupby(["date", "region"], as_index=False, sort=True)["sales"]
        .sum()
        .sort_values(["date", "region"])
        .reset_index(drop=True)
    )


def filter_daily_sales(
    sales: pd.DataFrame,
    selected_region: str,
) -> pd.DataFrame:
    """Filter a region and return one total-sales value per day."""
    if selected_region not in REGION_OPTIONS:
        raise ValueError(f"Unknown region: {selected_region!r}")

    filtered_sales = (
        sales
        if selected_region == "all"
        else sales.loc[sales["region"] == selected_region]
    )

    return (
        filtered_sales.groupby("date", as_index=False, sort=True)["sales"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )


def create_sales_figure(
    daily_sales: pd.DataFrame,
    selected_region: str = "all",
) -> go.Figure:
    """Create a regional daily-sales line chart."""
    start_date = daily_sales["date"].min().strftime("%d %b %Y").lstrip("0")
    end_date = daily_sales["date"].max().strftime("%d %b %Y").lstrip("0")
    region_label = (
        "All regions"
        if selected_region == "all"
        else f"{selected_region.title()} region"
    )

    figure = go.Figure(
        go.Scatter(
            x=daily_sales["date"],
            y=daily_sales["sales"],
            mode="lines",
            line={"color": "#C7496F", "width": 2.2},
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
        line={"color": "#A36A12", "width": 2, "dash": "dash"},
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
        font={"color": "#7C500C", "size": 12},
        bgcolor="rgba(255, 247, 224, 0.96)",
        bordercolor="#E9D7A8",
        borderwidth=1,
        borderpad=6,
    )

    figure.update_layout(
        title={
            "text": (
                "Daily Pink Morsel sales"
                f"<br><sup>{region_label} · {start_date}–{end_date}</sup>"
            ),
            "x": 0,
            "xanchor": "left",
        },
        template="plotly_white",
        showlegend=False,
        hovermode="x unified",
        margin={"l": 72, "r": 32, "t": 90, "b": 68},
        font={
            "family": "Inter, Arial, sans-serif",
            "color": "#31263A",
        },
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        transition={"duration": 300, "easing": "cubic-in-out"},
    )
    figure.update_xaxes(
        title_text="Date",
        showgrid=False,
        showline=True,
        linecolor="#A99EAA",
        tickfont={"color": "#665C68"},
    )
    figure.update_yaxes(
        title_text="Daily sales ($)",
        tickprefix="$",
        tickformat=",.0f",
        rangemode="tozero",
        gridcolor="#ECE7EC",
        showline=True,
        linecolor="#A99EAA",
        tickfont={"color": "#665C68"},
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


def comparison_copy(
    daily_sales: pd.DataFrame,
    selected_region: str,
) -> Tuple[str, str]:
    """Build the reader-facing summary for the selected region."""
    before_average, after_average, percentage_change = sales_comparison(
        daily_sales
    )
    region_label = (
        "Across all regions"
        if selected_region == "all"
        else f"In the {selected_region} region"
    )
    direction = "higher" if percentage_change >= 0 else "lower"

    headline = (
        f"{region_label}, average daily sales were "
        f"{abs(percentage_change):.1f}% {direction} after the increase."
    )
    details = (
        f"Before: ${before_average:,.0f} per day · "
        f"From 15 Jan 2021: ${after_average:,.0f} per day"
    )
    return headline, details


sales_data = load_sales_data()
daily_sales = filter_daily_sales(sales_data, "all")
sales_figure = create_sales_figure(daily_sales, "all")
initial_headline, initial_details = comparison_copy(daily_sales, "all")

app = Dash(__name__, title="Pink Morsel Sales Visualiser")
server = app.server

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Main(
            className="dashboard",
            children=[
                html.Header(
                    className="hero",
                    children=[
                        html.Div(
                            className="brand-row",
                            children=[
                                html.Span(
                                    "SOUL FOODS",
                                    className="eyebrow",
                                ),
                                html.Span(
                                    "SALES LAB",
                                    className="brand-badge",
                                ),
                            ],
                        ),
                        html.H1(
                            "Pink Morsel Sales Visualiser",
                            id="app-title",
                        ),
                        html.P(
                            "Explore daily sales around the 15 January 2021 "
                            "price increase, then focus the story by region.",
                            className="hero-copy",
                        ),
                    ],
                ),
                html.Section(
                    className="control-panel",
                    children=[
                        html.Div(
                            children=[
                                html.P(
                                    "REGION FILTER",
                                    className="section-kicker",
                                ),
                                html.H2(
                                    "Choose a sales view",
                                    className="control-title",
                                ),
                            ]
                        ),
                        dcc.RadioItems(
                            id="region-filter",
                            options=[
                                {
                                    "label": region,
                                    "value": region,
                                }
                                for region in REGION_OPTIONS
                            ],
                            value="all",
                            inline=True,
                            className="region-options",
                            inputClassName="region-radio",
                            labelClassName="region-label",
                        ),
                    ],
                ),
                html.Section(
                    className="insight-card",
                    children=[
                        html.Div("↗", className="insight-icon"),
                        html.Div(
                            children=[
                                html.P(
                                    "AT A GLANCE",
                                    className="section-kicker",
                                ),
                                html.Strong(
                                    initial_headline,
                                    id="sales-conclusion",
                                ),
                                html.Span(
                                    initial_details,
                                    id="sales-details",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Section(
                    className="chart-card",
                    children=[
                        dcc.Loading(
                            type="circle",
                            color="#C7496F",
                            className="chart-loading",
                            children=dcc.Graph(
                                id="sales-line-chart",
                                figure=sales_figure,
                                config={
                                    "displayModeBar": False,
                                    "responsive": True,
                                },
                                className="sales-chart",
                            ),
                        ),
                        html.P(
                            "Source: Soul Foods transaction data · "
                            "Daily sales = price × quantity",
                            className="source-note",
                        ),
                    ],
                ),
                html.Footer(
                    "Built for Soul Foods · Pink Morsel sales analysis",
                    className="footer",
                ),
            ],
        )
    ],
)


@app.callback(
    Output("sales-line-chart", "figure"),
    Output("sales-conclusion", "children"),
    Output("sales-details", "children"),
    Input("region-filter", "value"),
)
def update_visualiser(selected_region: str):
    """Update the chart and summary for the chosen region."""
    filtered_sales = filter_daily_sales(sales_data, selected_region)
    figure = create_sales_figure(filtered_sales, selected_region)
    headline, details = comparison_copy(filtered_sales, selected_region)
    return figure, headline, details


if __name__ == "__main__":
    app.run(debug=True)
