import pandas as pd
import streamlit as st
from getData import get_financial_data
from showData import display_financial_statement, display_financial_chart

st.set_page_config(page_title="Stock Financial Snapshot", layout="wide")


def safe_format(value, format_string="{:,.2f}"):
    """Enhanced helper to format metrics, including large number scaling."""
    if value is None or pd.isna(value):
        return "N/A"

    # If it's a large number and we want human-readable scaling (K, M, B, T)
    if isinstance(value, (int, float)) and value >= 1000:
        for unit in ['', 'K', 'M', 'B', 'T']:
            if abs(value) < 1000:
                return f"{value:,.1f}{unit}"
            value /= 1000
        return f"{value:,.1f}P"  # Peta for extreme cases

    if isinstance(value, str):
        return value

    return format_string.format(value)


def main():
    # st.title("Stock Financial Snapshot")
    left_co, cent_co, last_co = st.columns([1, 2, 1])

    with cent_co:
        image_url = "./image/Logo.png"
        st.image(image_url, use_container_width=True)

    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):").strip().upper()

    if stock_symbol:
        with st.spinner(f"Fetching data for {stock_symbol}..."):
            financial_data = get_financial_data(stock_symbol)

        if financial_data:
            st.markdown("<hr>", unsafe_allow_html=True)

            # --- Key Metrics ---
            st.subheader("Key Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Market Cap", safe_format(financial_data.get('market_cap'), "{:,}"))
                st.metric("Stock Price", safe_format(financial_data.get('currentPrice'), "${:,.2f}"))
            with col2:
                st.metric("PE Ratio", safe_format(financial_data.get('currentPE')))
                st.metric("Forward PE", safe_format(financial_data.get('forwardPE')))

            # --- Free Cash Flow ---
            st.subheader("Free Cash Flow")
            col3, col4 = st.columns(2)
            with col3:
                st.metric("FCF per Share", safe_format(financial_data.get('free_cash_flow_per_share'), "${:,.2f}"))
                st.metric("FCF per Share (Adjusted)",
                          safe_format(financial_data.get('free_cash_flow_per_share_adjusted'), "${:,.2f}"))
            with col4:
                st.metric("FCF Yield", safe_format(financial_data.get('free_cash_flow_yield')))
                st.metric("FCF Yield (Adjusted)", safe_format(financial_data.get('free_cash_flow_yield_adjusted')))

            st.markdown("<hr>", unsafe_allow_html=True)

            # --- Financial Statements ---
            # st.subheader("Financial Statements (in Millions)")
            # display_financial_statement("Income Statement", financial_data.get('income_statement'))
            # display_financial_statement("Cash Flow Statement", financial_data.get('cash_flow'))
            # display_financial_statement("Balance Sheet", financial_data.get('balance_sheet'))
            chart_col1, chart_col2 = st.columns(2)
            chart_col3, chart_col4 = st.columns(2)
            chart_col5, chart_col6 = st.columns(2)
            chart_col7, chart_col8 = st.columns(2)

            with chart_col1:
                display_financial_chart("Total Revenue", financial_data['income_statement'],
                                        "Total Revenue")
            with chart_col2:
                display_financial_chart("Net Income", financial_data['income_statement'],
                                        "Net Income", colors=["#28a745"])
            with chart_col3:
                display_financial_chart("EPS", financial_data['income_statement'],
                                        "Diluted EPS", ["#17a2b8"])
            with chart_col4:
                display_financial_chart("Long Term Debt", financial_data['balance_sheet'],
                                        "Long Term Debt", ["#ffc107"])
            with chart_col5:
                display_financial_chart("FCF vs stock base comp", financial_data['cash_flow'],
                                        ["Stock Based Compensation", "Free Cash Flow"],
                                        ["#0068c9", "#28a745"])
            with chart_col6:
                display_financial_chart("Dividend", financial_data['cash_flow'],
                                        "Common Stock Dividend Paid",
                                        ["#0068c9"])
        else:
            st.error(f"Could not retrieve financial statements for {stock_symbol}. Please check the symbol.")


if __name__ == "__main__":
    main()