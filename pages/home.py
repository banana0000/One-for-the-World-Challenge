import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home")

layout = html.Div(
    style={"textAlign": "center", "padding": "50px", "backgroundColor": "#111", "minHeight": "100vh"},
    children=[
        html.Br(),
        html.H1("Welcome to the One for the World Dashboard!", style={"color": "white", "fontSize": "40px"}),
        html.P("Use the navigation bar to explore various metrics and insights.",
               style={"color": "white", "fontSize": "25px", "marginBottom": "50px"}),

        # Card Section with 4 cards (one for each page)
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "30px",
                "flexWrap": "wrap",
                "padding": "20px"
            },
            children=[
                # Card 1: Home
                dbc.Card(
                    dbc.CardBody([  
                        html.H4("Home", style={"color": "white", "fontSize": "22px"}),
                        html.P("This is the homepage, where you can explore the general dashboard.", style={"color": "white"})
                    ]),
                    style={"width": "300px", "backgroundColor": "#333", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)"}
                ),
                # Card 2: Objectics
                dbc.Card(
                    dbc.CardBody([  
                        html.H4("Objectics", style={"color": "white", "fontSize": "22px"}),
                        html.P("Explore insights related to the Objectics data and its analysis.", style={"color": "white"})
                    ]),
                    style={"width": "300px", "backgroundColor": "#333", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)"}
                ),
                # Card 3: Money Moved
                dbc.Card(
                    dbc.CardBody([  
                        html.H4("Money Moved", style={"color": "white", "fontSize": "22px"}),
                        html.P("View detailed information about the movement of money and its status.", style={"color": "white"})
                    ]),
                    style={"width": "300px", "backgroundColor": "#333", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)"}
                ),
                # Card 4: Pledge
                dbc.Card(
                    dbc.CardBody([  
                        html.H4("Pledge", style={"color": "white", "fontSize": "22px"}),
                        html.P("Learn about the pledges and their progress over time.", style={"color": "white"})
                    ]),
                    style={"width": "300px", "backgroundColor": "#333", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)"}
                )
            ]
        )
    ]
)
