"""
viz.py
------
Plotting utilities using plotly for the dashboard.
"""

from typing import Optional
import pandas as pd
import plotly.express as px


def plot_country_timeseries(df: pd.DataFrame, country: str, window: int = 5) -> str:
    """
    Create a line chart with the actual CO2 values and a centered rolling mean.
    Returns an HTML string (Plotly full html bundle using CDN).
    """
    if country not in df["country"].unique():
        return "<p>No data available for the selected country.</p>"

    df_country = df[df["country"] == country].sort_values(by="year").copy()

    # If country has very few rows, fallback to window=1 (no smoothing)
    if len(df_country) < window:
        window = 1

    # rolling with center gives a nicer visual for missing years
    df_country["co2_smoothed"] = df_country["co2"].rolling(window=window, center=True).mean()

    chart = px.line(
        df_country,
        x="year",
        y=["co2", "co2_smoothed"],
        labels={"value": "CO₂ (million tonnes)", "year": "Year"},
        title=f"CO₂ Emissions — {country} (smoothed: {window} yr)",
    )

    def _rename_trace(trace):
        if trace.name == "co2":
            trace.update(name="Actual")
        else:
            trace.update(name=f"{window}-yr mean")

    chart.for_each_trace(_rename_trace)

    chart.update_layout(
        hovermode="x unified",
        legend_title_text="",
        plot_bgcolor="white",
        margin=dict(t=40)
    )

    # I kept Plotly CDN to keep Docker image size small during CI.
    return chart.to_html(include_plotlyjs="cdn")


def plot_world_map(df: pd.DataFrame, year: int) -> str:
    """
    Choropleth of CO2 by ISO code for a given year.
    Returns HTML string.
    """
    df_year = df[df["year"] == int(year)]
    if df_year.empty:
        return "<p>No data for selected year.</p>"

    # Plotly's choropleth expects ISO 3166 alpha-3 codes.
    choropleth = px.choropleth(
        df_year,
        locations="iso_code",
        color="co2",
        hover_name="country",
        hover_data={"iso_code": True, "co2": ":.3f"},
        color_continuous_scale="Reds",
        labels={"co2": "CO₂ [million t]"},
        title=f"CO₂ Emissions Worldwide — {year}"
    )

    choropleth.update_layout(
        margin=dict(t=40),
        coloraxis_colorbar_title_text="CO₂ [million t]"
    )

    return choropleth.to_html(include_plotlyjs="cdn")
