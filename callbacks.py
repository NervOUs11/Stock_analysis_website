import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from getData import get_financial_data
from pages.financials import build_financials_page
from pages.valuation import build_valuation_page


# ── Persist active tab ────────────────────────────────────────────────────────

@app.callback(
    Output("active-tab-store", "data"),
    Input("main-tabs", "active_tab"),
    prevent_initial_call=True
)
def save_active_tab(active_tab):
    """Writes the selected tab ID to the store so re-renders can restore it."""
    return active_tab


# ── Dark mode CSS injection (clientside — no server round-trip) ───────────────

app.clientside_callback(
    """
    function(themeValue) {
        const isDark = themeValue && themeValue.length > 0;

        let styleEl = document.getElementById('_dash-dark-overrides');
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = '_dash-dark-overrides';
            document.head.appendChild(styleEl);
        }

        styleEl.textContent = isDark ? `
            .rc-slider-mark-text        { color: #FFFFFF !important; }
            .rc-slider-tooltip-inner    { background-color: #1E1E1E !important; color: #FFFFFF !important; }
            .rc-slider-rail             { background-color: #444444 !important; }
            .form-check-label           { color: #FFFFFF !important; }
            .dash-input, input.form-control {
                background-color: #2A2A2A !important;
                color: #FFFFFF !important;
            }
        ` : '';

        return window.dash_clientside.no_update;
    }
    """,
    Output("theme-switch", "className"),  # harmless dummy output
    Input("theme-switch", "value"),
)


# ── Main dashboard ────────────────────────────────────────────────────────────

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
        Input("pe-slider", "value"),
        Input("fcf-slider", "value"),
        Input("valuation-method", "value")
    ],
    [
        State("ticker-input", "value"),
        State("active-tab-store", "data")
    ],
    prevent_initial_call=True
)
def update_dashboard(n_clicks, theme_value, g_rate, pe_multiple, fcf_multiple,
                     val_method, symbol, active_tab):
    # --- Theme ---
    is_dark = len(theme_value) > 0
    template = "darkly" if is_dark else "flatly"
    bg_color = "#121212" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#000000"
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    input_bg = "#2A2A2A" if is_dark else "#FFFFFF"
    border_color = "#444444" if is_dark else "#CCCCCC"

    logo_src = app.get_asset_url("Logo_white.png" if is_dark else "Logo_black.png")

    container_style = {
        "backgroundColor": bg_color, "color": text_color,
        "minHeight": "100vh", "transition": "0.3s"
    }
    input_style = {
        "backgroundColor": input_bg, "color": text_color,
        "border": f"1px solid {border_color}", "transition": "0.3s"
    }

    # Slider/toggle defaults
    g_rate = g_rate if g_rate is not None else 15
    pe_multiple = pe_multiple if pe_multiple is not None else 25
    fcf_multiple = fcf_multiple if fcf_multiple is not None else 25
    val_method = val_method if val_method is not None else "pe"

    # Stay on the current tab; only reset to Financials on a fresh search
    triggered = dash.ctx.triggered_id
    default_tab = "tab-financials" if triggered == "search-btn" else (active_tab or "tab-financials")

    if not symbol:
        return "", container_style, logo_src, input_style

    # --- Data ---
    data = get_financial_data(symbol.upper())
    if not data:
        error = dbc.Alert(f"No data found for '{symbol}'.", color="danger")
        return error, container_style, logo_src, input_style

    # --- Pages ---
    theme_kwargs = dict(text_color=text_color, card_bg=card_bg, border_color=border_color)

    financials_page = build_financials_page(data, template=template, **theme_kwargs)
    valuation_page = build_valuation_page(
        data, g_rate, pe_multiple, fcf_multiple, val_method, **theme_kwargs
    )

    tabs = dbc.Tabs([
        dbc.Tab(financials_page, label="Financials",      tab_id="tab-financials"),
        dbc.Tab(valuation_page,  label="Valuation Model", tab_id="tab-valuation"),
    ], id="main-tabs", active_tab=default_tab)

    return tabs, container_style, logo_src, input_style
