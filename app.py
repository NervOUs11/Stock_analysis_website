import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
from getData import get_financial_data


# def display_financial_statement(title: str, df: pd.DataFrame) -> None:
#     st.subheader(title + " (in millions)")
#     if isinstance(df, pd.DataFrame) and not df.empty:  # Check if df is a DataFrame and not empty
#         # Format the dates for display
#         df = df.copy()  # avoid modifying original
#         try:
#             df.columns = df.columns.strftime('%Y-%m-%d')
#         except AttributeError:
#             st.warning(f"Dataframe columns are not datetime objects for {title}.  Skipping date formatting.")
#         st.dataframe(df)
#     elif df is None:
#         st.write(f"No {title} available.")
#     else:
#         st.write(f"{title} is empty.")
def display_financial_statement(title: str, df: pd.DataFrame) -> None:
    """
    Displays a financial statement DataFrame in a Streamlit application.

    Args:
        title (str): The title of the financial statement.
        df (pd.DataFrame): The DataFrame containing the financial statement data.
    """
    st.subheader(title)
    if isinstance(df, pd.DataFrame) and not df.empty: # Check if df is a DataFrame and not empty
        # Format the dates for display
        df = df.copy()  # avoid modifying original
        cols_to_convert = [col for col in df.index if col not in ["Basic EPS", "Diluted EPS"]]
        df.loc[cols_to_convert] = df.loc[cols_to_convert] / 1e6
        df = df.applymap(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
        try:
            df.columns = df.columns.strftime('%Y-%m-%d')
        except AttributeError:
            st.warning(f"Dataframe columns are not datetime objects for {title}.  Skipping date formatting.")
        st.dataframe(df)
    elif df is None:
        st.write(f"No {title} available.")
    else:
        st.write(f"{title} is empty.")


def main():
    st.title("Stock Analysis")

    # User inputs
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):").upper()
    country = st.text_input("Enter Country Where Stock Is Traded (e.g., US):").upper()

    if stock_symbol and country:
        # Combine stock symbol and country for yfinance (if needed)
        if country == "US":
            full_symbol = stock_symbol
        else:
            full_symbol = f"{stock_symbol}.{country.upper()}"  # Example: AAPL.L for London

        financial_data = get_financial_data(full_symbol, years=4)

        if financial_data:
            st.write(f"Market Capitalization: {financial_data['market_cap']:,}")
            st.write(f"Stock Price: {financial_data['currentPrice']}")
            st.write(f"PE Ratio: {financial_data['currentPE']:.2f}")
            st.write(f"Forward PE Ratio: {financial_data['forwardPE']:.2f}")
            st.write(f"Free Cash Flow per Share: {financial_data['free_cash_flow_per_share']:.2f}")
            st.write(f"Free Cash Flow per Share (Adjusted Stock Stock Based Compensation): "
                     f"{financial_data['free_cash_flow_per_share_adjusted']:.2f}")
            st.write(f"Free Cash Flow Yield: {financial_data['free_cash_flow_yield']}")
            st.write(f"Free Cash Flow Yield (Adjusted Stock Stock Based Compensation): "
                     f"{financial_data['free_cash_flow_yield_adjusted']}")
            display_financial_statement("Income Statement", financial_data['income_statement'])
            display_financial_statement("Balance Sheet", financial_data['balance_sheet'])
            display_financial_statement("Cash Flow Statement", financial_data['cash_flow'])
        else:
            st.error(
                f"Could not retrieve financial statements for {full_symbol}.  Please check the symbol and country.")
    else:
        st.write("Please enter a stock symbol and country.")


if __name__ == "__main__":
    main()
