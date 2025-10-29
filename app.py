"""
app.py
------
Main Shiny application entrypoint for the CO₂ Dashboard.

This app loads prepared data at import time (simple approach for a student demo),
exposes a small UI with two tabs, and demonstrates reactive plotting.
"""

from shiny import App, ui, render
from data import load_prepared_data
from viz import plot_country_timeseries, plot_world_map
from utils import safe_html, get_country_list

#data loading
# Load data once when the app starts. This keeps the UI simple.
# NOTE: for production you'd want background loading and error pages.
print("[app.py] Loading dataset...")
df = load_prepared_data()
countries = get_country_list(df)
print(f"[app.py] {len(countries)} countries available. Default country: Austria (if present).")

# CSS
custom_css = """
body { background-color: #fafafa; font-family: 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; }
h1, h2, h3 { color: #333; font-weight: 600; }
.sidebar { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; padding: 15px; }
.plot-container { padding: 15px; }
.footer { text-align: center; color: #777; font-size: 0.9em; margin-top: 40px; }
"""

# UI Layout
ui_elements = ui.page_fluid(
    ui.head_content(ui.tags.style(custom_css)),
    ui.panel_title("🌍 CO₂ Dashboard", window_title="🌍CO₂ Dashboard"),
    ui.h2("🌿Global CO₂ Emissions Dashboard", class_="text-center mt-3"),
    ui.h5(
        "Explore country-level emissions and world map visualizations.",
        class_="text-center mb-4 text-muted"
    ),
    ui.navset_pill(
        ui.nav_panel(
            "📈 Country Time Series",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_select(
                        id="country",
                        label="Select Country",
                        choices=countries,
                        selected="Austria" if "Austria" in countries else (countries[0] if countries else None)
                    ),
                    ui.input_slider(
                        id="smooth",
                        label="Rolling mean (years)",
                        min=1,
                        max=20,
                        value=5
                    ),
                    width=300,
                    class_="sidebar"
                ),
                ui.div(ui.output_ui("country_plot"), class_="plot-container")
            )
        ),
        ui.nav_panel(
            "🗺️ World Map",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_slider(
                        id="year",
                        label="Select Year",
                        min=int(df["year"].min()),
                        max=int(df["year"].max()),
                        value=2020
                    ),
                    width=300,
                    class_="sidebar"
                ),
                ui.div(ui.output_ui("world_plot"), class_="plot-container")
            )
        )
    ),
    ui.div(
        "my mini project — Data from Our World in Data | Built with Shiny for Python & Plotly",
        class_="footer"
    )
)


# Server logic
def server(input, output, session):
    @output
    @render.ui
    def country_plot():
        # Small debug print
        print(f"[app.py] Rendering country plot: {input.country()} (smooth={input.smooth()})")
        html = plot_country_timeseries(df, input.country(), input.smooth())
        return safe_html(html)

    @output
    @render.ui
    def world_plot():
        print(f"[app.py] Rendering world plot for year: {input.year()}")
        html = plot_world_map(df, input.year())
        return safe_html(html)


app = App(ui_elements, server)

# TODO: Add a loading spinner and a graceful error page if data download fails.
# TODO: Convert data loading to a background task so UI starts quickly.
