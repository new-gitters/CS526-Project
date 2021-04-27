import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import dash_bootstrap_components as dbc
import sqlite3
from predictor import machine_learning
import io
import base64

#resource https://www.ncdc.noaa.gov/billions/time-series/US
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
con = sqlite3.connect("wildfire_data.sqlite")
cur = con.cursor()

df_count = pd.read_sql_query('SELECT STATE, FIRE_YEAR, STAT_CAUSE_DESCR, FIRE_SIZE_CLASS from Fires', con)

df_freq=pd.read_csv('./state-freq-data.csv', delimiter=",")
df_cost=pd.read_csv('./state-cost-data.csv', delimiter=",")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# 1992-2015 wildfire count
# 1980-2021 billion dollar event count

cfg = dict()
cfg['start_year'] = 1980
cfg['end_year']   = 2021
cfg['Years']      = list(range(cfg['start_year'], cfg['end_year']+1))

colors = {
    'background': '#1F2630',
    'text': '#7FDBFF'
}

def getFig():  #create choropleth graph
    dff_cost= df_cost.copy()
    dff_freq = df_freq.copy()

    mydict={}
    mydict['state']=dff_freq.state.unique()
    mydict['count']=[]
    for state in mydict['state']:
        data=dff_freq[dff_freq["state"] == state]
        mydict['count'].append((data['wildfire']==1).sum())

    df = pd.DataFrame(mydict)
    df['loss'] = dff_cost['wildfire']

    fig_map = px.choropleth(
        data_frame = df,
        locationmode = 'USA-states',
        locations='state',
        scope="usa",
        color = "count",
        hover_data = ['state', 'count','loss'],
        color_continuous_scale=px.colors.sequential.Turbo,
        labels={'count': '"Billion-Dollar wildfire number',
        'loss':'1980-2021 Billion-Dollar Disasters Cost'},
  
    )

    fig_map.update_layout(clickmode='event+select')  #add the click event


    return fig_map

def getStateOption():
    res=[]
    states=list(us_state_abbrev.items())
    states.sort(key=lambda x:x[1])
    res.append({"label":"All","value":"All"})
    for state in states:
        tmp={}
        tmp["label"]=state[0]
        tmp["value"]=state[1]
        res.append(tmp)
    return res
def get_loss_pie():
    dff_cause=df_cost[['state','wildfire']]
    dff_cause=dff_cause.sort_values(by=['wildfire'],ascending=False).head(10)
    fig_pie_cause = px.pie(dff_cause, names='state', values='wildfire', title='loss of Fire', labels={'state': 'state code', 'wildfire':'Loss of fires in million'}, template='plotly_dark', hole=0.3)
    fig_pie_cause.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    return fig_pie_cause



app.layout=html.Div([
    # represents the URL bar, doesn't render anything
    html.H1("Wildfire Economic loss in the United States", style = {'text-align': 'center'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ecoloss_state', figure=getFig(), config={'scrollZoom': False, 'displayModeBar': False}), width=8),
        dbc.Col(dcc.Graph(id='price-time-series', config={'displayModeBar': False}), width=4)
    ], no_gutters=True),


    dbc.Row([
        dbc.Col(dcc.RangeSlider(id="slct_year",
                    marks={
                        1980: '1980',
                        1985: '1985',
                        1990: '1990',
                        1995: '1995',
                        2000: '2000',
                        2005: '2005',
                        2010: '2010',
                        2015: '2015',
                        2021: {'label': '2021', 'style':{'color':'#f50', 'font-weight':'bold'}}
                    },
                    step=1,
                    min=1980,
                    max=2021,
                    value=[1980,2021],
                    dots=True,
                    allowCross=False,
                    disabled=False,
                    updatemode='mouseup',
                    included=True,
                    vertical=False,
                    verticalHeight=900,
                    tooltip={'always_visible':False, 'placement':'bottom'}
                    ), width=8),
        dbc.Col(dcc.Dropdown(id="slct_state",
                            options = getStateOption(),
                            multi = False,
                            value = "All",
                            style = {'width': "65%", 'color': '#212121'},
                            clearable=False
                            ))
    ]),
    dbc.Row([
    dbc.Col(dcc.Graph(id='freq_pie', figure={}, config={'displayModeBar': False}), width=4),
    dbc.Col(dcc.Graph(id='loss_pie', figure=get_loss_pie(), config={'displayModeBar': False}), width=4),
    html.Img(id='prediction',src=machine_learning(),width="400", height="400")
    ],no_gutters=True),

    # img element

    #dbc.Col(dcc.Graph(id='machine', figure=machine_learning(), config={'displayModeBar': False}), width=4),

    



])

@app.callback(
    Output('price-time-series', 'figure'),
    Input('ecoloss_state', 'clickData')
     )
def update_price_timeseries(clickData):
    #print(clickData)
    #can try to set he click data as geojson
    empty_series = pd.DataFrame(np.full(len(cfg['Years']), np.nan), index=cfg['Years'])
    empty_series.rename(columns={0: ''}, inplace=True)

    if clickData is None:
        States = "CA"
    else:
        States=clickData['points'][0]['location']

    wildfire_year_df = get_wildfire_by_year(States)

    title = f"Fires in {abbrev_us_state[States]} Over Time"
    return fire_ts(wildfire_year_df, title)

def fire_ts(df, title):
    #print(df.head())
    fig = px.bar(df,title=title, labels={'year':'Year', 'value':'Number of Fires'})
    
    fig.update_xaxes(showgrid=False)
    fig.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                 
                      font_color=colors['text'])
    fig.update_layout(showlegend=False)
    return fig

def get_wildfire_by_year(state):
    wildfire_year_df=pd.DataFrame()
    data=df_freq[df_freq["state"] == state]
    data=data[['year','wildfire']]
    #print(data)
    year_data=data.groupby('year').sum()
    #print(year_data.head())
    return year_data

@app.callback(
    Output(component_id='freq_pie', component_property='figure'),
    [Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_state', component_property='value')]
)
def update_pie(slct_year,slct_state):
    dff=df_freq.copy()
    dff = dff[(dff["year"] >= slct_year[0]) & (dff["year"] <= slct_year[1])]
    if slct_state == "All":
        pass
    else:
        dff = dff[dff["state"] == slct_state]
    container = "Wildfires from " + str(slct_year[0]) + " to " + str(slct_year[1])
    causes=["drought","flooding","freeze","severe storm","tropical cyclone","wildfire","winter storm"]
    mydict={}
    mydict['cause']=[]
    mydict['freq']=[]
    for cause in causes:
        mydict['cause'].append(cause)
        mydict['freq'].append(dff[cause].sum())
    data=pd.DataFrame(mydict)

    freq_pie = px.pie(data, names='cause', values='freq', title='loss of Fire', labels={'state': 'state code', 'wildfire':'Loss of fires in million'}, template='plotly_dark', hole=0.3)
    freq_pie.update_layout(
                      plot_bgcolor=colors['background'],
                      paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    
    return freq_pie




 

if __name__ == '__main__':
    app.run_server(debug=True)




    




