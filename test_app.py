"""Tests for the Soul Foods Dash visualiser."""

import unittest

from dash import dcc, html

from app import (
    PRICE_INCREASE_DATE,
    app,
    create_sales_figure,
    daily_sales,
    sales_comparison,
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
    def test_daily_sales_are_aggregated_and_sorted(self) -> None:
        self.assertTrue(daily_sales["date"].is_monotonic_increasing)
        self.assertFalse(daily_sales["date"].duplicated().any())
        self.assertEqual(len(daily_sales), 1_470)

    def test_figure_has_line_axes_and_price_change_marker(self) -> None:
        figure = create_sales_figure(daily_sales)

        self.assertEqual(figure.data[0].mode, "lines")
        self.assertEqual(len(figure.data[0].x), len(daily_sales))
        self.assertEqual(figure.layout.xaxis.title.text, "Date")
        self.assertEqual(figure.layout.yaxis.title.text, "Daily sales ($)")
        self.assertEqual(
            figure.layout.shapes[0].x0.to_pydatetime(),
            PRICE_INCREASE_DATE.to_pydatetime(),
        )

    def test_layout_contains_required_header_and_chart(self) -> None:
        title = find_component(app.layout, html.H1, "app-title")
        graph = find_component(app.layout, dcc.Graph, "sales-line-chart")

        self.assertIsNotNone(title)
        self.assertEqual(title.children, "Pink Morsel Sales Visualiser")
        self.assertIsNotNone(graph)

    def test_after_period_has_higher_average_daily_sales(self) -> None:
        before_average, after_average, percentage_change = sales_comparison(
            daily_sales
        )

        self.assertGreater(after_average, before_average)
        self.assertAlmostEqual(percentage_change, 35.8477, places=3)

    def test_dash_index_loads(self) -> None:
        response = app.server.test_client().get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pink Morsel Sales Visualiser", response.data)


if __name__ == "__main__":
    unittest.main()
