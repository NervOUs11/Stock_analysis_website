import plotly.express as px
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc


def make_card(label, val, highlight=False, text_color="#000000", card_bg="#FFFFFF", border_color="#CCCCCC"):
    """Styled Bootstrap card for KPIs. Optional green highlight border for the key result."""
    border = "2px solid #2ECC71" if highlight else f"1px solid {border_color}"
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Small(label, style={"opacity": "0.65", "fontSize": "0.78rem"}),
                html.H4(val, className="mb-0 mt-1", style={"color": text_color})
            ]),
            style={
                "backgroundColor": card_bg,
                "border": border,
                "color": text_color,
                "transition": "0.3s"
            }
        ),
        width=3
    )


def create_chart(title, df, metrics=None, colors=None, show_legend=True,
                 template="flatly", text_color="#000000"):
    """Reshapes a financial dataframe into long format and returns a grouped Plotly bar chart."""
    if df is None or df.empty:
        return html.Div()

    metrics = [metrics] if isinstance(metrics, str) else metrics
    existing = [m for m in metrics if m in df.index]
    if not existing:
        return html.Div()

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
