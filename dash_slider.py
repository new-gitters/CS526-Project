import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import sqlite3
import numpy as np



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

con = sqlite3.connect("wildfire_data.sqlite")
cur = con.cursor()

df = pd.read_sql_query('SELECT STATE, FIRE_YEAR, STAT_CAUSE_DESCR, FIRE_SIZE_CLASS from Fires', con)

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))
#1992 - 2015
cfg = dict()
cfg['start_year'] = 1992
cfg['end_year']   = 2015
cfg['Years']      = list(range(cfg['start_year'], cfg['end_year']+1))
stateCount=df['STATE'].value_counts()
cfg['states']=stateCount.index.tolist()
cfg['timeout']          = 5*60     # Used in flask_caching
selections = set()

colors = {
    'background': '#1F2630',
    'text': '#7FDBFF'
}

def get_layout():
    return (html.Div([
    html.H1("Wildfires in the United States", style = {'text-align': 'center'}),
    dbc.Row([
        dbc.Col(dcc.RangeSlider(id="slct_year",
                    marks={
                        1992: '1992',
                        1995: '1995',
                        2000: '2000',
                        2005: '2005',
                        2010: '2010',
                        2015: {'label': '2015', 'style':{'color':'#f50', 'font-weight':'bold'}}
                    },
                    step=1,
                    min=1992,
                    max=2015,
                    value=[1992,2015],
                    dots=True,
                    allowCross=False,
                    disabled=False,
                    updatemode='mouseup',
                    included=True,
                    vertical=False,
                    verticalHeight=900,
                    tooltip={'always_visible':False, 'placement':'bottom'}
                    ), width=8),
        dbc.Col(dcc.Dropdown(id="slct_size",
                            options = [
                                {"label": "A = 0 to 0.25 Acres", "value": "A"},
                                {"label": "B = 0.26 to 9.9 Acres", "value": "B"},
                                {"label": "C = 10.0 to 99.9 Acres", "value": "C"},
                                {"label": "D = 100 to 299 Acres", "value": "D"},
                                {"label": "E = 300 to 999 Acres", "value": "E"},
                                {"label": "F = 1000 to 4999 Acres", "value": "F"},
                                {"label": "G = 5000+ Acres", "value": "G"},
                                {"label": "All", "value": "All"}],
                            multi = False,
                            value = "All",
                            style = {'width': "65%", 'color': '#212121'},
                            clearable=False
                            ))
    ]),

    html.Div(id='output_container', children = []),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='my_state_map', figure={}, config={'scrollZoom': False, 'displayModeBar': False}), width=8),
        dbc.Col(dcc.Graph(id='price-time-series', config={'displayModeBar': False}), width=4)
    ], no_gutters=True),
    dbc.Row([
        dbc.Col(dcc.Graph(id='state_bars', figure={}, config={'displayModeBar': False}), width=8),
        dbc.Col(dcc.Graph(id='cause_pie', figure={}, config={'displayModeBar': False}), width=4)
    ], no_gutters=True),
], style={'height':'100vh'}))

app.layout = get_layout()



@app.callback(
    [Output(component_id='output_container', component_property='children'),
    Output(component_id='my_state_map', component_property='figure'),
    Output(component_id='state_bars', component_property='figure'),
    Output(component_id='cause_pie', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')],
    [Input(component_id='slct_size', component_property='value')]
)

def update_graph(year_slctd, size_slctd):
    dff = df.copy()
    dff = dff[(dff["FIRE_YEAR"] >= year_slctd[0]) & (dff["FIRE_YEAR"] <= year_slctd[1])]
    if size_slctd == "All":
        pass
    else:
        dff = dff[dff["FIRE_SIZE_CLASS"] == size_slctd]
    container = "Wildfires from " + str(year_slctd[0]) + " to " + str(year_slctd[1])
    if year_slctd[0] == year_slctd[1]:
        container = "Wildfires in " + str(year_slctd[0])
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
    fig_map.update_layout(autosize=True,
                      font_color=colors['text'])
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    #########################################################

    fig_map.update_layout(clickmode='event')  #add the click event

    fig_bar_states = px.bar(dff_state, x='State', y='Counts', title='Fires by State', labels={'Counts':'Number of Fires'}, template='plotly_dark')
    fig_bar_states.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      autosize=True,
                      font_color=colors['text'])

    dff_cause = dff.STAT_CAUSE_DESCR.value_counts().rename_axis('Cause').reset_index(name='Counts')
    fig_pie_cause = px.pie(dff_cause, names='Cause', values='Counts', title='Cause of Fire', labels={'Cause': 'Cause of Fire', 'Counts':'Number of Fires'}, template='plotly_dark', hole=0.3)
    fig_pie_cause.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])

    return container, fig_map, fig_bar_states, fig_pie_cause


def fire_ts(df, title):
    fig = px.scatter(df,
                     title=title, labels={'FIRE_YEAR':'Year', 'value':'Number of Fires'})
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      autosize=True,
                      font_color=colors['text'])
    fig.update_layout(showlegend=False)
    return fig

def get_wildfire_by_year(state):
    wildfire_year_df=pd.DataFrame()
    data=df[df["STATE"] == state]
    
    year_data=data.groupby('FIRE_YEAR').size()
    wildfire_year_df[state] = year_data
    return wildfire_year_df

@app.callback(

    Output('price-time-series', 'figure'),
    Input('my_state_map', 'clickData')
     )

def update_price_timeseries(clickData):
    empty_series = pd.DataFrame(np.full(len(cfg['Years']), np.nan), index=cfg['Years'])
    empty_series.rename(columns={0: ''}, inplace=True)

    if clickData is None:
        States = "CA"
    else:
        States=clickData['points'][0]['location']

    wildfire_year_df = get_wildfire_by_year(States)

    title = f"Fires in {abbrev_us_state[States]} Over Time"
    return fire_ts(wildfire_year_df, title)

if __name__ == '__main__':
    app.run_server(debug=True)