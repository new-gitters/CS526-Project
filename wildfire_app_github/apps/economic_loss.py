import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import dash_bootstrap_components as dbc

'''SINGLE PAGE CHANGE: comment out next line if running as single page'''
from app import app

#resource https://www.ncdc.noaa.gov/billions/time-series/US

df_freq=pd.read_csv('./state-freq-data.csv', delimiter=",")
df_cost=pd.read_csv('./state-cost-data.csv', delimiter=",")

'''SINGLE PAGE CHANGE: uncomment next line if running as single page'''
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

def getFig():  #create choropleth graph
    dff_cost = df_cost.copy()
    # print(dff_cost.head())
    fig = go.Figure(data=go.Choropleth(
    locations=dff_cost['state'], # Spatial coordinates

    z = dff_cost['wildfire'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Billions USD",
    ))
    return fig

"""SINGLE PAGE CHANGE: change layout = ... to app.layout = ... if running as single page"""
layout=html.Div([
    # represents the URL bar, doesn't render anything
    html.H1("Wildfire Economic loss from 1980-2021 in the United States", style = {'text-align': 'center'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ecoloss_state', figure=getFig(), config={'scrollZoom': False, 'displayModeBar': False}), width=10),
        dbc.Col(dcc.Graph(id='price-time-series', config={'displayModeBar': False}), width=4)
    ], no_gutters=True),

    html.Div(id='output_container', children = []),

])




'''SINGLE PAGE CHANGE: uncomment next line if running as single page'''
# if __name__ == '__main__':
#     app.run_server(debug=True)