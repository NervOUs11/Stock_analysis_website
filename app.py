import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from getData import get_financial_data

# ==========================================
# 1. APP INITIALIZATION & THEME SETUP
# ==========================================

# Loads both light (flatly) and dark (darkly) templates into Plotly's memory.
# This ensures charts automatically match the CSS theme of the app.
load_figure_template(["flatly", "darkly"])

# Initialize the Dash app with the default light theme (FLATLY)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def safe_format(value, prefix=""):
    """
    Formats raw numbers into human-readable strings (e.g., 1,500,000 -> 1.5M).
    Handles missing data gracefully by returning 'N/A'.
    """
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, str):
        return value

    val = float(value)

    # Scale down large numbers and append the correct suffix
    if abs(val) >= 1000:
        for unit in ['', 'K', 'M', 'B', 'T']:
            if abs(val) < 1000:
                return f"{prefix}{val:,.1f}{unit}"
            val /= 1000

    # Fallback for smaller numbers (e.g., standard stock prices)
    return f"{prefix}{val:,.2f}"


# ==========================================
# 3. APP LAYOUT (THE VISUAL SKELETON)
# ==========================================

app.layout = dbc.Container([

    # --- Header Row: Theme Switch & Logo ---
    dbc.Row([
        # Left side: Dark Mode Toggle
        dbc.Col(
            dbc.Checklist(
                options=[{"label": "🌙 Dark Mode", "value": 1}],
                value=[],
                id="theme-switch",
                switch=True,
                className="mt-3"
            ),
            width=6,
            className="d-flex align-items-top"  # Aligns the switch to the top edge
        ),

        # Right side: Dynamic Logo
        dbc.Col(
            html.Img(
                id="app-logo",
                style={"width": "200px"}
            ),
            width=6,
            className="text-end"  # Pushes the logo to the far right of its column
        )
    ], justify="between", className="mb-2"),

    # --- Search Input Row ---
    dbc.Row([
        dbc.Col([
            # User types the ticker here
            dbc.Input(id="ticker-input", placeholder="Enter Ticker (e.g., AAPL)", type="text"),
            # Clicking this button triggers the main callback
            dbc.Button("Search", id="search-btn", color="primary", className="mt-2 w-100")
        ], width={"size": 4, "offset": 4}, className="mt-3")  # Centered column (4 cols wide, offset by 4)
    ]),

    html.Hr(),  # Horizontal divider line

    # --- Content Area ---
    # dcc.Loading wraps the content area so a spinner appears while the callback runs
    dcc.Loading(id="loading-content", children=[
        # This empty Div will be populated by the update_dashboard callback
        html.Div(id="dashboard-body")
    ])

], id="main-container", fluid=True)  # fluid=True makes the container span the whole screen width


# ==========================================
# 4. CALLBACKS (THE BRAIN / LOGIC)
# ==========================================

@app.callback(
    [
        Output("dashboard-body", "children"),  # The actual data UI (cards/charts)
        Output("main-container", "style"),  # Injects background colors for theme
        Output("app-logo", "src"),  # Swaps the logo image file
        Output("ticker-input", "style")  # Adjusts input box colors for dark mode
    ],
    [
        Input("search-btn", "n_clicks"),  # Trigger 1: Clicking the search button
        Input("theme-switch", "value")  # Trigger 2: Flipping the dark mode switch
    ],
    [State("ticker-input", "value")]  # State: Grabs the text in the input box without triggering on keystrokes
)
def update_dashboard(n_clicks, theme_value, symbol):
    """
    Main controller function. Fires whenever the user searches or toggles the theme.
    It fetches data, builds the UI components, and returns them to the layout.
    """

    # --- A. Evaluate Theme Settings ---
    is_dark = len(theme_value) > 0  # Returns True if the switch is toggled on
    template = "darkly" if is_dark else "flatly"  # Tells Plotly which chart template to use

    # Define dynamic CSS hex colors based on the theme
    bg_color = "#121212" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#000000"
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    input_bg = "#2A2A2A" if is_dark else "#FFFFFF"
    border_color = "#444444" if is_dark else "#CCCCCC"

    # Select the correct logo file from the assets folder
    logo_file = "Logo_white.png" if is_dark else "Logo_black.png"
    logo_src = app.get_asset_url(logo_file)

    # Package the CSS styles to inject into the HTML layout
    container_style = {
        "backgroundColor": bg_color,
        "color": text_color,
        "minHeight": "100vh",  # Ensures the background stretches to the bottom of the screen
        "transition": "0.3s"  # Smooth fade effect when swapping themes
    }

    input_style = {
        "backgroundColor": input_bg,
        "color": text_color,
        "border": f"1px solid {border_color}",
        "transition": "0.3s"
    }

    # Early Exit: If the app just loaded and the user hasn't typed anything yet
    if not symbol:
        return "", container_style, logo_src, input_style

    # --- B. Fetch Data ---
    data = get_financial_data(symbol.upper())

    # Handle bad tickers or API failures
    if not data:
        error_alert = dbc.Alert(f"No data for {symbol}", color="danger")
        return error_alert, container_style, logo_src, input_style

    # --- C. UI Component Builders ---

    def make_card(label, val):
        """Builds a responsive Bootstrap card for a single metric."""
        return dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Small(label, style={"opacity": "0.7"}),  # The subtitle
                    html.H4(val, className="mb-0", style={"color": text_color})  # The main number
                ]),
                style={
                    "backgroundColor": card_bg,
                    "border": f"1px solid {border_color}",
                    "color": text_color,
                    "transition": "0.3s"
                }
            ),
            width=3  # Takes up 1/4th of the row
        )

    def create_chart(title, df, metrics=None, colors=None, show_legend=True):
        """Builds an interactive Plotly bar chart from a financial dataframe."""
        if df is None or df.empty: return html.Div()

        # Ensure metrics is a list for iteration
        metrics = [metrics] if isinstance(metrics, str) else metrics

        # Filter dataframe to only include the requested metrics
        existing = [m for m in metrics if m in df.index]
        if not existing: return html.Div()

        # Data Transformation for Plotly (Wide to Long format)
        plot_df = df.loc[existing].T.sort_index()  # Transpose (dates become rows) and sort oldest to newest
        plot_df = plot_df.reset_index()

        # Extract just the Year from the Date index (e.g., '2023-12-31' -> '2023')
        plot_df['Year'] = pd.to_datetime(plot_df['index']).dt.year.astype(str)

        # Melt converts multiple metric columns into a single 'Value' column mapped to a 'Metric' category
        plot_df = plot_df.melt(id_vars='Year', value_vars=existing, var_name='Metric', value_name='Value')

        # Generate the Plotly Bar Figure
        fig = px.bar(
            plot_df,
            x='Year',
            y='Value',
            color='Metric',
            barmode='group',  # Puts bars side-by-side instead of stacking them
            title=title,
            template=template,  # Applies Dark/Light mode template
            color_discrete_sequence=colors if colors else px.colors.qualitative.Plotly
        )

        # Fine-tune the chart appearance
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent outer background
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent inner grid background
            font=dict(color=text_color),
            showlegend=show_legend,
            xaxis={'type': 'category'},  # Prevents Plotly from interpolating missing years as decimals
            legend=dict(
                orientation="h",  # Horizontal legend at the top
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=None  # Removes the word "Metric:" from the legend
            )
        )

        # Return the chart wrapped in Dash's Graph component
        return dcc.Graph(figure=fig, config={'displayModeBar': False})

    # --- D. Assemble the Final Layout ---

    content = html.Div([
        html.H3("Key Metrics", className="mt-4 mb-3"),

        # Top Row: Basic Metrics
        dbc.Row([
            make_card("Market Cap", safe_format(data['market_cap'])),
            make_card("Stock Price", safe_format(data['currentPrice'], "$")),
            make_card("PE Ratio", safe_format(data['currentPE'])),
            make_card("Forward PE", safe_format(data['forwardPE'])),
        ], className="g-3 mb-3"),  # 'g-3' adds consistent gap spacing between cards

        # Second Row: Free Cash Flow Metrics
        dbc.Row([
            make_card("FCF per Share", safe_format(data['free_cash_flow_per_share'], "$")),
            make_card("FCF Yield", data['free_cash_flow_yield']),
            make_card("Adj FCF / Share", safe_format(data['free_cash_flow_per_share_adjusted'], "$")),
            make_card("Adj FCF Yield", data['free_cash_flow_yield_adjusted']),
        ], className="g-3 mb-4"),

        html.Hr(style={"borderColor": border_color}),

        # Third Row: Revenue & Net Income Charts
        dbc.Row([
            dbc.Col(create_chart("Total Revenue", data['income_statement'], "Total Revenue"), width=6),
            dbc.Col(create_chart("Net Income", data['income_statement'], "Net Income", ["#28a745"]), width=6),
        ], className="mb-4"),

        # Fourth Row: EPS & Debt Charts
        dbc.Row([
            dbc.Col(create_chart("EPS", data['income_statement'], "Diluted EPS", ["#17a2b8"]), width=6),
            dbc.Col(create_chart("Long Term Debt", data['balance_sheet'], "Long Term Debt", ["#ffc107"]), width=6),
        ], className="mb-4"),

        # Fifth Row: FCF Comparison Chart (Full Width)
        dbc.Row([
            dbc.Col(create_chart("FCF vs Stock Based Comp", data['cash_flow'],
                                 ["Stock Based Compensation", "Free Cash Flow"], ["#0068c9", "#28a745"]), width=12),
        ], className="mb-4")
    ])

    # Return the 4 variables matching the 4 Outputs in the callback decorator
    return content, container_style, logo_src, input_style


# ==========================================
# 5. SERVER EXECUTION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)