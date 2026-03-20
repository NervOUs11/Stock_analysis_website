import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from getData import get_financial_data
from valuation import calculate_dcf

# ==========================================
# 1. APP INITIALIZATION & THEME SETUP
# ==========================================

# Register Plotly templates for light/dark theme toggling
load_figure_template(["flatly", "darkly"])

# Initialize Dash app with Bootstrap Flatly theme
# suppress_callback_exceptions=True allows us to use slider IDs that are generated dynamically
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY],
                suppress_callback_exceptions=True)


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def safe_format(value, prefix=""):
    """
    Converts large numerical values into readable formats (K, M, B, T).
    Returns 'N/A' for missing or null data.
    """
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, str):
        return value

    val = float(value)

    # Logic to scale numbers and append the appropriate unit suffix
    if abs(val) >= 1000:
        for unit in ['', 'K', 'M', 'B', 'T']:
            if abs(val) < 1000:
                return f"{prefix}{val:,.1f}{unit}"
            val /= 1000

    return f"{prefix}{val:,.2f}"


# ==========================================
# 3. APP LAYOUT
# ==========================================

app.layout = dbc.Container([
    # Hidden container for sliders to prevent Dash from throwing "Nonexistent ID" errors on startup
    html.Div(id='hidden-slider-container', style={'display': 'none'}, children=[
        dcc.Slider(id='growth-slider', value=15),
        dcc.Slider(id='discount-slider', value=10),
        dcc.Slider(id='terminal-slider', value=1)
    ]),

    # Top Row: Contains the dark mode switch and the application logo
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
                style={"width": "200px"}
            ),
            width=6,
            className="text-end"
        )
    ], justify="between", className="mb-2"),

    # Search section: User input for stock ticker and search execution button
    dbc.Row([
        dbc.Col([
            dbc.Input(id="ticker-input", placeholder="Enter Ticker (e.g., AAPL)", type="text"),
            dbc.Button("Search", id="search-btn", color="primary", className="mt-2 w-100")
        ], width={"size": 4, "offset": 4}, className="mt-3")
    ]),

    html.Hr(),

    # Dynamic loading area: Shows a spinner while the data-fetching callback executes
    dcc.Loading(id="loading-content", children=[
        html.Div(id="dashboard-body")
    ])

], id="main-container", fluid=True)


# ==========================================
# 4. CALLBACKS (THE BRAIN / LOGIC)
# ==========================================

@app.callback(
    [
        Output("dashboard-body", "children"),
        Output("main-container", "style"),
        Output("app-logo", "src"),
        Output("ticker-input", "style")
    ],
    [
        Input("search-btn", "n_clicks"),
        Input("theme-switch", "value"),
        Input("growth-slider", "value"),
        Input("discount-slider", "value"),
        Input("terminal-slider", "value")
    ],
    [State("ticker-input", "value")],
    prevent_initial_call=True  # Prevents the callback from firing until user interaction occurs
)
def update_dashboard(n_clicks, theme_value, g_rate, d_rate, t_growth, symbol):
    """
    Primary logic function: Handles theme switching, data fetching,
    financial chart creation, and DCF valuation calculations.
    """

    # --- A. Theme Management ---
    is_dark = len(theme_value) > 0
    template = "darkly" if is_dark else "flatly"

    # Default logic for sliders to ensure calculations work if IDs are temporarily missing
    g_rate = g_rate if g_rate is not None else 15
    d_rate = d_rate if d_rate is not None else 10
    t_growth = t_growth if t_growth is not None else 1

    # Dynamic color palette based on dark/light mode selection
    bg_color = "#121212" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#000000"
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    input_bg = "#2A2A2A" if is_dark else "#FFFFFF"
    border_color = "#444444" if is_dark else "#CCCCCC"

    logo_file = "Logo_white.png" if is_dark else "Logo_black.png"
    logo_src = app.get_asset_url(logo_file)

    container_style = {
        "backgroundColor": bg_color,
        "color": text_color,
        "minHeight": "100vh",
        "transition": "0.3s"
    }

    input_style = {
        "backgroundColor": input_bg,
        "color": text_color,
        "border": f"1px solid {border_color}",
        "transition": "0.3s"
    }

    if not symbol:
        return "", container_style, logo_src, input_style

    # --- B. Data Fetching ---
    data = get_financial_data(symbol.upper())

    if not data:
        error_alert = dbc.Alert(f"No data for {symbol}", color="danger")
        return error_alert, container_style, logo_src, input_style

    # --- C. Component Factories ---
    def make_card(label, val):
        """Generates a styled Bootstrap card for financial KPIs."""
        return dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Small(label, style={"opacity": "0.7"}),
                    html.H4(val, className="mb-0", style={"color": text_color})
                ]),
                style={
                    "backgroundColor": card_bg,
                    "border": f"1px solid {border_color}",
                    "color": text_color,
                    "transition": "0.3s"
                }
            ),
            width=3
        )

    def create_chart(title, df, metrics=None, colors=None, show_legend=True):
        """Processes dataframe into Long-format and returns a Plotly bar chart."""
        if df is None or df.empty: return html.Div()

        metrics = [metrics] if isinstance(metrics, str) else metrics
        existing = [m for m in metrics if m in df.index]
        if not existing: return html.Div()

        # Reshape data for Plotly Express
        plot_df = df.loc[existing].T.sort_index().reset_index()
        plot_df['Year'] = pd.to_datetime(plot_df['index']).dt.year.astype(str)
        plot_df = plot_df.melt(id_vars='Year', value_vars=existing, var_name='Metric', value_name='Value')

        fig = px.bar(
            plot_df, x='Year', y='Value', color='Metric',
            barmode='group', title=title, template=template,
            color_discrete_sequence=colors if colors else px.colors.qualitative.Plotly
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=show_legend,
            xaxis={'type': 'category'},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
        )

        return dcc.Graph(figure=fig, config={'displayModeBar': False})

    # --- D. Final UI Assembly ---

    # View 1: Financials - Focuses on historical performance and key statements
    financials_page = html.Div([
        html.H3("Key Metrics", className="mt-4 mb-3"),
        dbc.Row([
            make_card("Market Cap", safe_format(data['market_cap'])),
            make_card("Stock Price", safe_format(data['currentPrice'], "$")),
            make_card("PE Ratio", safe_format(data['currentPE'])),
            make_card("Forward PE", safe_format(data['forwardPE'])),
        ], className="g-3 mb-3"),

        dbc.Row([
            make_card("FCF per Share", safe_format(data['free_cash_flow_per_share'], "$")),
            make_card("FCF Yield", data['free_cash_flow_yield']),
            make_card("Adj FCF / Share", safe_format(data['free_cash_flow_per_share_adjusted'], "$")),
            make_card("Adj FCF Yield", data['free_cash_flow_yield_adjusted']),
        ], className="g-3 mb-4"),

        html.Hr(style={"borderColor": border_color}),

        dbc.Row([
            dbc.Col(create_chart("Income statement", data['income_statement'],
                                 ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
                                 ["#97F23D", "#973DF2", "#F23D3D", "#3DF1F2"]), width=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart("Retained Earnings", data['balance_sheet'], "Retained Earnings", ["#3DF1F2"]),
                    width=6),
            dbc.Col(create_chart("EPS", data['income_statement'], "Diluted EPS", ["#97F23D"]), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart("CAPEX", data['cash_flow'], "Capital Expenditure", ["#F23D3D"]), width=6),
            dbc.Col(create_chart("Long Term Debt", data['balance_sheet'], "Long Term Debt", ["#973DF2"]), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart("FCF vs Stock Based Comp", data['cash_flow'],
                                 ["Stock Based Compensation", "Free Cash Flow"], ["#F23D3D", "#97F23D"]), width=12),
        ], className="mb-4")
    ])

    # View 2: Valuation - Interactive DCF model based on user-defined growth assumptions
    fcf_ttm = data['cash_flow'].loc['Free Cash Flow'].iloc[0]
    intrinsic_value = calculate_dcf(fcf_ttm, growth_rate=(g_rate / 100), discount_rate=(d_rate / 100),
                                    terminal_growth=(t_growth / 100))
    market_cap = data['market_cap']
    upside = ((intrinsic_value - market_cap) / market_cap) * 100

    valuation_page = html.Div([
        html.H4("DCF Assumption Sliders", className="mt-4 mb-3"),
        dbc.Row([
            dbc.Col([
                html.Label(f"Growth Rate: {g_rate}%"),
                dcc.Slider(0, 30, 1, value=g_rate, id='growth-slider'),
            ], width=4),
            dbc.Col([
                html.Label(f"Discount Rate: {d_rate}%"),
                dcc.Slider(5, 20, 0.5, value=d_rate, id='discount-slider'),
            ], width=4),
            dbc.Col([
                html.Label(f"Terminal Growth: {t_growth}%"),
                dcc.Slider(0, 5, 0.1, value=t_growth, id='terminal-slider'),
            ], width=4),
        ], className="mb-5 p-3 rounded", style={"backgroundColor": card_bg, "border": f"1px solid {border_color}"}),

        html.H3("Intrinsic Value Results", className="mb-3"),
        dbc.Row([
            make_card("Intrinsic Value (DCF)", safe_format(intrinsic_value, "$")),
            make_card("Current Market Cap", safe_format(market_cap, "$")),
            make_card("Margin of Safety", f"{upside:.1f}%"),
            make_card("Status", "UNDERVALUED" if upside > 0 else "OVERVALUED"),
        ], className="g-3 mb-4"),
    ])

    # Combine Financials and Valuation into a Tabbed interface
    tabs = dbc.Tabs([
        dbc.Tab(financials_page, label="Financials", tab_id="tab-financials"),
        dbc.Tab(valuation_page, label="Valuation Model", tab_id="tab-valuation"),
    ], active_tab="tab-financials")

    return tabs, container_style, logo_src, input_style


# ==========================================
# 5. SERVER EXECUTION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)