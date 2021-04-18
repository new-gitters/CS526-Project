import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import dash_bootstrap_components as dbc

#resource https://www.ncdc.noaa.gov/billions/time-series/US

df_freq=df.read_csv('./state-freq-data.csv', delimiter=",")
df_cost=df.read_csv('./state-freq-data.csv', delimiter=",")




app.layout=html.Div([
    # represents the URL bar, doesn't render anything
    html.H1("Wildfire Economic loss from 1980-2021 in the United States", style = {'text-align': 'center'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ecoloss_state', figure=getFig(), config={'scrollZoom': False, 'displayModeBar': False}), width=10),
        dbc.Col(dcc.Graph(id='price-time-series', config={'displayModeBar': False}), width=4)
    ], no_gutters=True),

    html.Div(id='output_container', children = []),

])

def getFig():  #create choropleth graph
    dff_freq = df_freq.copy()
    dff_cost = df_cost.copy()
    fig = go.Figure(data=go.Choropleth(
    locations=dff_freq['state'], # Spatial coordinates
    z = df['wildfire'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Millions USD",
))





    




