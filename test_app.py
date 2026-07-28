"""Tests for the Soul Foods Dash visualiser."""

import unittest

from dash import dcc, html

from app import (
    PRICE_INCREASE_DATE,
    REGION_OPTIONS,
    app,
    comparison_copy,
    create_sales_figure,
    daily_sales,
    filter_daily_sales,
    sales_data,
    sales_comparison,
    update_visualiser,
)


def find_component(component, component_type, component_id):
    """Recursively find a Dash component by type and ID."""
    if isinstance(component, component_type) and component.id == component_id:
        return component

    children = getattr(component, "children", None)
    if children is None:
        return None
    if not isinstance(children, (list, tuple)):
        children = [children]

    for child in children:
        found = find_component(child, component_type, component_id)
        if found is not None:
            return found
    return None


class DashAppTests(unittest.TestCase):
    def test_sales_data_preserves_daily_region_grain(self) -> None:
        self.assertEqual(len(sales_data), 5_880)
        self.assertEqual(
            set(sales_data["region"]),
            {"north", "east", "south", "west"},
        )
        self.assertFalse(sales_data.duplicated(["date", "region"]).any())

    def test_all_region_sales_are_aggregated_and_sorted(self) -> None:
        self.assertTrue(daily_sales["date"].is_monotonic_increasing)
        self.assertFalse(daily_sales["date"].duplicated().any())
        self.assertEqual(len(daily_sales), 1_470)
        self.assertAlmostEqual(
            daily_sales["sales"].sum(),
            sales_data["sales"].sum(),
        )

    def test_region_filter_returns_one_value_per_day(self) -> None:
        north_sales = filter_daily_sales(sales_data, "north")

        self.assertEqual(len(north_sales), 1_470)
        self.assertFalse(north_sales["date"].duplicated().any())
        self.assertLess(
            north_sales["sales"].sum(),
            daily_sales["sales"].sum(),
        )

        with self.assertRaises(ValueError):
            filter_daily_sales(sales_data, "central")

    def test_figure_has_line_axes_and_price_change_marker(self) -> None:
        north_sales = filter_daily_sales(sales_data, "north")
        figure = create_sales_figure(north_sales, "north")

        self.assertEqual(figure.data[0].mode, "lines")
        self.assertEqual(len(figure.data[0].x), len(north_sales))
        self.assertEqual(figure.layout.xaxis.title.text, "Date")
        self.assertEqual(figure.layout.yaxis.title.text, "Daily sales ($)")
        self.assertIn("North region", figure.layout.title.text)
        self.assertEqual(
            figure.layout.shapes[0].x0.to_pydatetime(),
            PRICE_INCREASE_DATE.to_pydatetime(),
        )

    def test_layout_contains_required_header_and_chart(self) -> None:
        title = find_component(app.layout, html.H1, "app-title")
        graph = find_component(app.layout, dcc.Graph, "sales-line-chart")
        radio = find_component(app.layout, dcc.RadioItems, "region-filter")

        self.assertIsNotNone(title)
        self.assertEqual(title.children, "Pink Morsel Sales Visualiser")
        self.assertIsNotNone(graph)
        self.assertIsNotNone(radio)
        self.assertEqual(
            [option["value"] for option in radio.options],
            list(REGION_OPTIONS),
        )
        self.assertEqual(
            [option["label"] for option in radio.options],
            list(REGION_OPTIONS),
        )
        self.assertEqual(radio.value, "all")

    def test_callback_updates_chart_and_summary_for_region(self) -> None:
        figure, headline, details = update_visualiser("east")

        self.assertIn("East region", figure.layout.title.text)
        self.assertIn("east region", headline)
        self.assertIn("Before:", details)
        self.assertIn("From 15 Jan 2021:", details)

    def test_after_period_has_higher_average_daily_sales(self) -> None:
        before_average, after_average, percentage_change = sales_comparison(
            daily_sales
        )
        headline, details = comparison_copy(daily_sales, "all")

        self.assertGreater(after_average, before_average)
        self.assertAlmostEqual(percentage_change, 35.8477, places=3)
        self.assertIn("35.8% higher", headline)
        self.assertIn("$6,604", details)

    def test_dash_index_loads(self) -> None:
        response = app.server.test_client().get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pink Morsel Sales Visualiser", response.data)


if __name__ == "__main__":
    unittest.main()
