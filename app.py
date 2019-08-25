import datetime

import dash
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.figure_factory as ff
import controls
import components

app = dash.Dash(__name__)
server = app.server

logo = html.Div(html.Img(
    src=app.get_asset_url("pydata-logo-final.png"),
    id="pydata-logo",
    className="one-third column"))

title_row = html.Div([logo, components.title],
                     className="banner row flex-display",
                     id="banner")
controller_row = html.Div(
    [html.Div([components.selectors], className="eight columns offset-by-two")],
    id="selectors",
    className="row flex-display")

first_row = html.Div([html.Div([components.top10_graph], className="one-half column"),
                      html.Div([components.num_offenses_graph], className="one-half column")],
                     className="row flex-display")
second_row = html.Div([html.Div([components.heatmap_graph], className="one-half column"),
                       html.Div([components.num_shootings_graph], className="one-half column")],
                      className="row flex-display")

app.layout = html.Div([title_row, controller_row, first_row, second_row], id="app-container")


@app.callback(Output("crossfilter-range-slider", 'value'),
              [Input('num_offenses_graph', 'relayoutData'),
               Input('num_shootings_graph', 'relayoutData')])
def test_slider(offenses_data, shootings_data):
    ctx = dash.callback_context

    default_values = 0, len(components.months) - 1
    if not ctx.triggered:
        return default_values

    data = offenses_data if ctx.triggered[0][
                                "prop_id"] == "num_offenses_graph.relayoutData" else shootings_data
    if data is None:
        return default_values

    if "xaxis.range[0]" not in data:
        return default_values

    dates = sorted([datetime.datetime.strptime(date.split(" ")[0], "%Y-%m-%d")
                   .replace(day=1)
                    for date in data.values()])
    indexes = [i for i, date in enumerate(components.months) if date in dates]
    return indexes


@app.callback(Output("num_shootings_graph", "figure"),
              [Input("crossfilter-range-slider", "value"),
               Input("crossfilter-district-dropdown", "value")])
def make_num_shootings_graph(input_index, districts_selected):
    start_date, end_date = components.months[input_index[0]], components.months[input_index[1]]
    result = controls.get_num_shootings_by_year_and_district(start_date, end_date,
                                                             districts_selected)

    return components.draw_line(result,
                                "num_shootings",
                                title=f"Number of Shootings per Month "
                                      f"between {start_date.strftime('%Y-%m')} "
                                      f"and {end_date.strftime('%Y-%m')}")


@app.callback(Output("num_offenses_graph", "figure"),
              [Input("crossfilter-range-slider", "value"),
               Input("crossfilter-district-dropdown", "value")])
def make_num_offenses_graph(input_index, districts_selected):
    start_date = components.months[input_index[0]]
    end_date = components.months[input_index[1]]
    result = controls.get_num_offenses_by_year_and_district(start_date,
                                                            end_date,
                                                            districts_selected)
    return components.draw_line(result,
                                "num_offenses",
                                title=f"Number of Offenses per Month between "
                                      f"{start_date.strftime('%Y-%m')} and "
                                      f"{end_date.strftime('%Y-%m')}")


@app.callback(Output('top10_graph', 'figure'),
              [Input('crossfilter-range-slider', 'value'),
               Input('crossfilter-district-dropdown', 'value')])
def make_top10_group(months_selected, districts_selected):
    start_date = components.months[months_selected[0]]
    end_date = components.months[months_selected[1]]
    results = controls.get_top10_offense_groups(start_date,
                                                end_date,
                                                districts_selected)

    return components.draw_bar(x="num_offenses",
                               y="OFFENSE_CODE_GROUP",
                               results=results[::-1],
                               title="Top 10 Offense Code Groups")


@app.callback(Output('heatmap_graph', 'figure'),
              [Input('crossfilter-range-slider', 'value'),
               Input('crossfilter-district-dropdown', 'value')])
def make_heatmap(selected_months, selected_districts):
    start_date = components.months[selected_months[0]]
    end_date = components.months[selected_months[1]]

    data = controls.get_heatmap_data(start_date, end_date, selected_districts)
    figure = ff.create_annotated_heatmap(data.values,
                                         y=data.index.to_list(),
                                         x=data.columns.to_list(),
                                         annotation_text=data.values,
                                         colorscale='viridis'
                                         )
    for i in range(len(figure.layout.annotations)):
        figure.layout.annotations[i].font.size = 8
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
