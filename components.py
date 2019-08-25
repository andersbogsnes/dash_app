import statistics
from typing import List

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import controls

RED = "#e26855"

months = controls.available_months()
districts = controls.available_districts()

title = html.Div(html.H1("Hello Pydata Copenhagen!"), className="one-half column", id="title")

range_slider = html.Div([
    html.H4("Filter by year"),
    dcc.RangeSlider(
        id='crossfilter-range-slider',
        min=0,
        max=len(months) - 1,
        step=1,
        className="crossfilter"
    )])
district_dropdown = html.Div([
    html.H4("Filter by district"),
    dcc.Dropdown(
        id="crossfilter-district-dropdown",
        options=[{"value": district, "label": district} for district in districts],
        multi=True,
        value=districts,
        className="crossfilter"
    )])

selectors = html.Div([range_slider, district_dropdown])

num_offenses_graph = html.Div([dcc.Graph(id="num_offenses_graph")],
                              className="pretty_container",
                              id="NumOffensesContainer")

num_shootings_graph = html.Div([dcc.Graph(id="num_shootings_graph")],
                               className="pretty_container",
                               id="numShootingsContainer")

top10_graph = html.Div([dcc.Graph(id="top10_graph")],
                       className="pretty_container",
                       id="top10GraphContainer")

heatmap_graph = html.Div([dcc.Graph(id="heatmap_graph")],
                         className="pretty_container",
                         id="heatmapGraphContainer")


def draw_line(result, value_col, title):
    values = [r[value_col] for r in result]

    line_chart = go.Scatter(
        type="scatter",
        mode="lines+markers",
        x=[r["year_month"] for r in result],
        y=values,
        line_color=RED,
        marker_color="black",
        hovertemplate="%{y:0}<extra></extra>"
    )
    data = [line_chart]
    mean_line = go.layout.Shape(type="line",
                                xref="paper",
                                x0=0,
                                x1=1,
                                y0=statistics.mean(values),
                                y1=statistics.mean(values),
                                line_color=RED,
                                line_dash='dash')

    layout = go.Layout(shapes=[mean_line],
                       title=title,
                       showlegend=False,
                       )

    return dict(data=data, layout=layout)


def draw_bar(x: str, y: str, results: List, title: str):
    bar_chart = go.Bar(
        x=[r[x] for r in results],
        y=[r[y] for r in results],
        orientation='h',
        hovertemplate="Number of Offenses: %{x:.3s}<extra></extra>"
    )
    data = [bar_chart]
    layout = go.Layout(
        title=title
    )
    return dict(data=data, layout=layout)
