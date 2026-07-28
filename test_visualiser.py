"""End-to-end tests for the Pink Morsel Dash visualiser."""

from app import app


def test_header_is_present(dash_duo):
    """The page should display the visualiser heading."""
    dash_duo.start_server(app)

    header = dash_duo.wait_for_element("#app-title", timeout=5)

    assert header.is_displayed()
    assert header.text == "Pink Morsel Sales Visualiser"


def test_visualisation_is_present(dash_duo):
    """The Plotly sales chart should render on the page."""
    dash_duo.start_server(app)

    dash_duo.wait_for_element(
        "#sales-line-chart .scatterlayer path",
        timeout=5,
    )
    chart = dash_duo.find_element("#sales-line-chart")

    assert chart.is_displayed()


def test_region_picker_is_present(dash_duo):
    """The picker should display all five required region options."""
    dash_duo.start_server(app)

    picker = dash_duo.wait_for_element("#region-filter", timeout=5)
    radio_buttons = dash_duo.find_elements(
        "#region-filter input[type='radio']"
    )

    assert picker.is_displayed()
    assert [button.get_attribute("value") for button in radio_buttons] == [
        "north",
        "east",
        "south",
        "west",
        "all",
    ]
