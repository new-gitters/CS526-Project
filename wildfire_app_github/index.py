import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app

from apps import economic_loss, usa

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Economic Impact", href="/economic_loss"),
        dbc.DropdownMenuItem("USA", href="/usa"),
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/fire.jpg", height="30px")),
                        dbc.Col(dbc.NavbarBrand("US Wildfires", className = "ml-2")),
                    ],
                    align = "center",
                    no_gutters = True,
                ),
                href = "/economic_loss",
            ),
            dbc.NavbarToggler(id = "navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar = True,
            ),
        ]
    ),
    color = "dark",
    dark = True,
    className = "mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/usa':
        return usa.layout
    else:
        return economic_loss.layout

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', debug=True)