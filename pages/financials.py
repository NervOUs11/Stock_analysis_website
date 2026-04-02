from dash import html
import dash_bootstrap_components as dbc
from components import make_card, create_chart
from utils import safe_format


def build_financials_page(data, text_color, card_bg, border_color, template):
    """
    Builds and returns the complete Financials tab layout.

    :param data:         Dict returned by get_financial_data()
    :param text_color:   Current theme text colour
    :param card_bg:      Current theme card background colour
    :param border_color: Current theme border colour
    :param template:     Plotly template name ('flatly' or 'darkly')
    """
    kwargs = dict(text_color=text_color, card_bg=card_bg, border_color=border_color)

    return html.Div([
        html.H3("Key Metrics", className="mt-4 mb-3"),
        dbc.Row([
            make_card("Market Cap",  safe_format(data['market_cap']),          **kwargs),
            make_card("Stock Price", safe_format(data['currentPrice'], "$"),   **kwargs),
            make_card("PE Ratio",    safe_format(data['currentPE']),            **kwargs),
            make_card("Forward PE",  safe_format(data['forwardPE']),            **kwargs),
        ], className="g-3 mb-3"),

        dbc.Row([
            make_card("FCF per Share",   safe_format(data['free_cash_flow_per_share'], "$"), **kwargs),
            make_card("FCF Yield",       data['free_cash_flow_yield'],                       **kwargs),
            make_card("Adj FCF / Share", safe_format(data['free_cash_flow_per_share_adjusted'], "$"), **kwargs),
            make_card("Adj FCF Yield",   data['free_cash_flow_yield_adjusted'],               **kwargs),
        ], className="g-3 mb-4"),

        html.Hr(style={"borderColor": border_color}),

        dbc.Row([
            dbc.Col(create_chart(
                "Income Statement", data['income_statement'],
                ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"],
                ["#97F23D", "#973DF2", "#F23D3D", "#3DF1F2"],
                template=template, text_color=text_color
            ), width=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart("Retained Earnings", data['balance_sheet'],
                                 "Retained Earnings", ["#3DF1F2"],
                                 template=template, text_color=text_color), width=6),
            dbc.Col(create_chart("EPS", data['income_statement'],
                                 "Diluted EPS", ["#97F23D"],
                                 template=template, text_color=text_color), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart("CAPEX", data['cash_flow'],
                                 "Capital Expenditure", ["#F23D3D"],
                                 template=template, text_color=text_color), width=6),
            dbc.Col(create_chart("Long Term Debt", data['balance_sheet'],
                                 "Long Term Debt", ["#973DF2"],
                                 template=template, text_color=text_color), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_chart(
                "FCF vs Stock Based Comp", data['cash_flow'],
                ["Stock Based Compensation", "Free Cash Flow"],
                ["#F23D3D", "#97F23D"],
                template=template, text_color=text_color
            ), width=12),
        ], className="mb-4"),
    ])
