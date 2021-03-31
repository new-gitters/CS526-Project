import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import sqlite3

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

con = sqlite3.connect("wildfire_data.sqlite")
cur = con.cursor()

df = pd.read_sql_query('SELECT STATE, FIRE_YEAR, STAT_CAUSE_DESCR from Fires', con)
#1992 - 2015

app.layout = html.Div([

    html.H1("Wildfires in the United States", style = {'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                options = [
                    {"label": "1992", "value": 1992},
                    {"label": "1993", "value": 1993},
                    {"label": "1994", "value": 1994},
                    {"label": "1995", "value": 1995},
                    {"label": "1996", "value": 1996},
                    {"label": "1997", "value": 1997},
                    {"label": "1998", "value": 1998},
                    {"label": "1999", "value": 1999},
                    {"label": "2000", "value": 2000},
                    {"label": "2001", "value": 2001},
                    {"label": "2002", "value": 2002},
                    {"label": "2003", "value": 2003},
                    {"label": "2004", "value": 2004},
                    {"label": "2005", "value": 2005},
                    {"label": "2006", "value": 2006},
                    {"label": "2007", "value": 2007},
                    {"label": "2008", "value": 2008},
                    {"label": "2009", "value": 2009},
                    {"label": "2010", "value": 2010},
                    {"label": "2011", "value": 2011}, 
                    {"label": "2012", "value": 2012},
                    {"label": "2013", "value": 2013},
                    {"label": "2014", "value": 2014},
                    {"label": "2015", "value": 2015},
                    {"label": "All Time", "value": 0}],
                multi = False,
                value = 0,
                style = {'width': "40%",
                        'color': '#212121'}
                ),
    html.Div(id='output_container', children = []),
    html.Br(),

    dcc.Graph(id='my_state_map', figure={}, config={'scrollZoom': False, 'displayModeBar': False}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='state_bars', figure={}, config={'displayModeBar': False})),
        dbc.Col(dcc.Graph(id='cause_bars', figure={}, config={'displayModeBar': False}))
    ])
])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
    Output(component_id='my_state_map', component_property='figure'),
    Output(component_id='state_bars', component_property='figure'),
    Output(component_id='cause_bars', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    container = "Wildfires from 1992-2015"
    dff = df.copy()
    if option_slctd != 0:
        dff = dff[dff["FIRE_YEAR"] == option_slctd]
        container = "Wildfires in {}".format(option_slctd)
    dff_state = dff.STATE.value_counts().rename_axis('State').reset_index(name='Counts')

    #Plotly Express
    fig_map = px.choropleth(
        data_frame = dff_state,
        locationmode = 'USA-states',
        locations='State',
        scope="usa",
        color = "Counts",
        hover_data = ['State', 'Counts'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Counts': 'Number of fires'},
        template='plotly_dark'
    )
    fig_map.layout.update(dragmode=False)

    fig_bar_states = px.bar(dff_state, x='State', y='Counts', title='Fires by State', labels={'Counts':'Number of Fires'}, template='plotly_dark')

    dff_cause = dff.STAT_CAUSE_DESCR.value_counts().rename_axis('Cause').reset_index(name='Counts')
    fig_bar_cause = px.bar(dff_cause, x='Cause', y='Counts', title='Causes of Fires', labels={'Cause': 'Cause of Fire', 'Counts':'Number of Fires'}, template='plotly_dark')
    return container, fig_map, fig_bar_states, fig_bar_cause

if __name__ == '__main__':
    app.run_server(debug=True)