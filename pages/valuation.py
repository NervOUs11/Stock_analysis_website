from dash import dcc, html
import dash_bootstrap_components as dbc
from dcf_valuation import calculate_pe_valuation, calculate_fcf_valuation
from components import make_card
from utils import safe_format


def build_valuation_page(data, g_rate, pe_multiple, fcf_multiple, val_method,
                         text_color, card_bg, border_color):
    """
    Builds and returns the complete Valuation tab layout, including
    the method toggle, assumption sliders, and results cards.

    :param data:         Dict returned by get_financial_data()
    :param g_rate:       Growth rate (integer, e.g. 15 means 15%)
    :param pe_multiple:  Target exit PE multiple
    :param fcf_multiple: Target exit P/FCF multiple
    :param val_method:   'pe' or 'fcf'
    :param text_color:   Current theme text colour
    :param card_bg:      Current theme card background colour
    :param border_color: Current theme border colour
    """

    # --- Calculations ---
    current_price = data['currentPrice']
    intrinsic_price = 0
    method_label = ""

    if val_method == "pe":
        eps = None
        if (data['income_statement'] is not None
                and 'Diluted EPS' in data['income_statement'].index):
            eps_series = data['income_statement'].loc['Diluted EPS'].dropna()
            if not eps_series.empty:
                eps = float(eps_series.iloc[0])
        if eps is not None and eps != 0:
            intrinsic_price = calculate_pe_valuation(
                eps, growth_rate=g_rate / 100, target_pe=pe_multiple
            )
        method_label = f"EPS grown at {g_rate}%/yr × {pe_multiple}x PE exit, discounted at 10%"

    else:  # fcf
        shares = data['sharesOutstanding']
        if (data['cash_flow'] is not None
                and 'Free Cash Flow' in data['cash_flow'].index and shares):
            fcf_ttm = float(data['cash_flow'].loc['Free Cash Flow'].iloc[0])
            intrinsic_price = calculate_fcf_valuation(
                fcf_ttm, shares, growth_rate=g_rate / 100, target_multiple=fcf_multiple
            )
        method_label = f"FCF grown at {g_rate}%/yr × {fcf_multiple}x P/FCF exit, discounted at 10%"

    upside = ((intrinsic_price - current_price) / current_price * 100) if current_price else 0
    is_undervalued = upside > 0

    card_kwargs = dict(text_color=text_color, card_bg=card_bg, border_color=border_color)

    slider_box_style = {
        "backgroundColor": card_bg,
        "border": f"1px solid {border_color}",
        "borderRadius": "8px",
        "padding": "20px",
        "marginBottom": "24px"
    }

    # --- Layout ---
    return html.Div([
        html.H4("Valuation Inputs", className="mt-4 mb-3"),

        html.Div([
            # Method selector
            dbc.Row([
                dbc.Col([
                    html.Label("Method", style={
                        "fontWeight": "600", "fontSize": "0.85rem",
                        "opacity": "0.7", "marginBottom": "6px"
                    }),
                    dbc.RadioItems(
                        id='valuation-method',
                        options=[
                            {"label": "  PE-Based",   "value": "pe"},
                            {"label": "  FCF-Based",  "value": "fcf"},
                        ],
                        value=val_method,
                        inline=True,
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "20px", "cursor": "pointer"}
                    )
                ], width=12)
            ], className="mb-4"),

            # Sliders
            dbc.Row([
                # Growth rate — always visible
                dbc.Col([
                    html.Label([
                        html.Span("Growth Rate", style={"fontWeight": "600"}),
                        html.Span(f"  {g_rate}%", style={
                            "color": "#2ECC71", "fontWeight": "700", "fontSize": "1.1rem"
                        })
                    ], className="d-flex align-items-center gap-2 mb-2"),
                    dcc.Slider(
                        min=0, max=30, step=1, value=g_rate, id='growth-slider',
                        marks={0: '0%', 10: '10%', 20: '20%', 30: '30%'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], width=6),

                # PE multiple — visible only when method == 'pe'
                dbc.Col([
                    html.Label([
                        html.Span("Target PE Multiple", style={"fontWeight": "600"}),
                        html.Span(f"  {pe_multiple}x", style={
                            "color": "#3D9DF2", "fontWeight": "700", "fontSize": "1.1rem"
                        })
                    ], className="d-flex align-items-center gap-2 mb-2"),
                    dcc.Slider(
                        min=5, max=60, step=1, value=pe_multiple, id='pe-slider',
                        marks={5: '5x', 20: '20x', 40: '40x', 60: '60x'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], width=6, style={"display": "block" if val_method == "pe" else "none"}),

                # FCF multiple — visible only when method == 'fcf'
                dbc.Col([
                    html.Label([
                        html.Span("Target P/FCF Multiple", style={"fontWeight": "600"}),
                        html.Span(f"  {fcf_multiple}x", style={
                            "color": "#3D9DF2", "fontWeight": "700", "fontSize": "1.1rem"
                        })
                    ], className="d-flex align-items-center gap-2 mb-2"),
                    dcc.Slider(
                        min=5, max=60, step=1, value=fcf_multiple, id='fcf-slider',
                        marks={5: '5x', 20: '20x', 40: '40x', 60: '60x'},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], width=6, style={"display": "block" if val_method == "fcf" else "none"}),
            ])
        ], style=slider_box_style),

        # Results
        html.H3("Intrinsic Value Results", className="mb-3"),
        dbc.Row([
            make_card("Intrinsic Price",   safe_format(intrinsic_price, "$"), highlight=True, **card_kwargs),
            make_card("Current Price",     safe_format(current_price, "$"),                   **card_kwargs),
            make_card("Upside / Downside", f"{upside:+.1f}%",                                 **card_kwargs),
            make_card("Status",
                      html.Span("● UNDERVALUED", style={"color": "#2ECC71"})
                      if is_undervalued else
                      html.Span("● OVERVALUED",  style={"color": "#E74C3C"}),
                      **card_kwargs),
        ], className="g-3 mb-3"),

        html.Small(
            f"★  Assumptions: {method_label}. Projection horizon: 5 years.",
            style={"opacity": "0.55", "fontSize": "0.78rem"}
        )
    ])
