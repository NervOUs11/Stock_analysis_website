import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template(["flatly", "darkly"])

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
server = app.server
