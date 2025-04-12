import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output

# Inicializáljuk az alkalmazást
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], use_pages=True)

# Alapértelmezett elrendezés
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # URL figyelő

    # Navigációs sáv
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand('One for the World Dashboard', className='ms-2',
                            style={"color": "white", "font-size": "24px"}),

            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", id="link-home",
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Objectics", href="/Objectics", id="link-1",
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Money Moved", href="/Money_Moved", id="link-2",
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
                dbc.NavItem(dbc.NavLink("Pledge", href="/Pledge", id="link-3",
                                        style={"color": "white", "font-size": "25px", "margin-left": "50px"})),
            ], className="ms-auto", navbar=True, style={"margin-left": "auto", "padding-right": "50px"})
        ], fluid=True),
        className="navbar-custom mb-4",
        style={"background": "linear-gradient(90deg, blue, magenta, black)"}
    ),

    # Az aktív oldal tartalma
    dash.page_container,  # Az aktuális oldal tartalma fog megjelenni itt
])

# 🔥 Callback a linkek aláhúzásához (aktív oldal kiemelése)
@app.callback(
    [
        Output("link-home", "style"),
        Output("link-1", "style"),
        Output("link-2", "style"),
        Output("link-3", "style"),
    ],
    Input("url", "pathname")
)
def update_link_style(pathname):
    default_style = {"color": "white", "font-size": "25px", "textDecoration": "none"}
    selected_style = {"color": "white", "border-bottom": "2px solid white",
                      "padding-bottom": "5px", "font-size": "25px"}

    return (
        selected_style if pathname == "/" else default_style,
        selected_style if pathname == "/Objectics" else default_style,
        selected_style if pathname == "/Money_Moved" else default_style,
        selected_style if pathname == "/Pledge" else default_style,
    )

# Futtatjuk az alkalmazást
if __name__ == "__main__":
    app.run(debug=True)
