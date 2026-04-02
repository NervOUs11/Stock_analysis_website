from dash import dcc, html
import dash_bootstrap_components as dbc
from server import app


app.layout = dbc.Container([
    # Persists the active tab across re-renders caused by slider/theme changes
    dcc.Store(id='active-tab-store', data='tab-financials'),

    # Hidden stubs keep all dynamic IDs registered on page load,
    # preventing Dash's "Nonexistent ID" errors before a search runs.
    html.Div(id='hidden-slider-container', style={'display': 'none'}, children=[
        dcc.Slider(id='growth-slider', value=15),
        dcc.Slider(id='pe-slider', value=25),
        dcc.Slider(id='fcf-slider', value=25),
        dcc.RadioItems(id='valuation-method', value='pe'),
        dbc.Tabs(id='main-tabs', active_tab='tab-financials')
    ]),

    # Header: dark mode toggle + logo
    dbc.Row([
        dbc.Col(
            dbc.Checklist(
                options=[{"label": "🌙 Dark Mode", "value": 1}],
                value=[],
                id="theme-switch",
                switch=True,
                className="mt-3"
            ),
            width=6,
            className="d-flex align-items-top"
        ),
        dbc.Col(
            html.Img(
                id="app-logo",
                src=app.get_asset_url("Logo_black.png"),
                style={"width": "200px"}
            ),
            width=6,
            className="text-end"
        )
    ], justify="between", className="mb-2"),

    # Search bar
    dbc.Row([
        dbc.Col([
            dbc.Input(id="ticker-input", placeholder="Enter Ticker (e.g., AAPL)", type="text"),
            dbc.Button("Search", id="search-btn", color="primary", className="mt-2 w-100")
        ], width={"size": 4, "offset": 4}, className="mt-3")
    ]),

    html.Hr(),

    # Main content area with loading spinner
    dcc.Loading(id="loading-content", children=[
        html.Div(id="dashboard-body")
    ])

], id="main-container", fluid=True)
