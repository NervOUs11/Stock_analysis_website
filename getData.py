import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
import streamlit as st


def get_financial_data(symbol: str, years: int = 4) -> Optional[dict]:
    try:
        stock = yf.Ticker(symbol)

        # Fetch financial statements
        income_statement = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        market_cap = stock.info.get('marketCap')
        sharesOutstanding = stock.info.get('sharesOutstanding')
        currentPrice = stock.info.get('currentPrice')
        forwardPE = stock.info.get('forwardPE')

        # Handle cases where data is not available
        if income_statement is None or balance_sheet is None or cash_flow is None:
            return None

        # Limit the data to the specified number of years
        income_statement = income_statement.iloc[:, :years] if income_statement.shape[1] > years else income_statement
        balance_sheet = balance_sheet.iloc[:, :years] if balance_sheet.shape[1] > years else balance_sheet
        cash_flow = cash_flow.iloc[:, :years] if cash_flow.shape[1] > years else cash_flow

        # Filter income statement rows
        if income_statement is not None and not income_statement.empty:
            income_statement = income_statement.loc[
                               ["Total Revenue", "Gross Profit", "Operating Income",
                                "Pretax Income", "Tax Provision", "Net Income", "Basic EPS", "Diluted EPS"], :
                               ].dropna(how='all')
            # Convert to millions, but keep EPS as is
            # cols_to_convert = [col for col in income_statement.index if col not in ["Basic EPS", "Diluted EPS"]]
            # income_statement.loc[cols_to_convert] = income_statement.loc[cols_to_convert] / 1e6 # Convert to millions

        # Filter balance sheet rows
        if balance_sheet is not None and not balance_sheet.empty:
            balance_sheet = balance_sheet.loc[
                               ["Current Assets", "Total Assets", "Current Liabilities",
                                "Total Liabilities Net Minority Interest", "Long Term Debt", "Retained Earnings",
                                "Stockholders Equity"], :
                               ].dropna(how='all')
            # balance_sheet = balance_sheet / 1e6  # Convert to millions
            # SUM Stockholders Equity and Total Liabilities
            if ('Total Liabilities Net Minority Interest' in balance_sheet.index
                    and 'Stockholders Equity' in balance_sheet.index):
                balance_sheet.loc['Total Liabilities and Equity'] = balance_sheet.loc[
                                                                    'Total Liabilities Net Minority Interest'] + \
                                                                    balance_sheet.loc['Stockholders Equity']
            else:
                st.error(f"Could not calculate Free Cash Flow adjusted for stock-based compensation for {symbol}")

        # Filter cash flow rows
        if cash_flow is not None and not cash_flow.empty:
            cash_flow = cash_flow.loc[
                           ["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
                            "Common Stock Dividend Paid", "Repurchase Of Capital Stock",
                            "Capital Expenditure", "Stock Based Compensation", "Free Cash Flow"], :
                           ].dropna(how='all')

            # Calculate Free Cash Flow adjusted for stock-based compensation
            if 'Free Cash Flow' in cash_flow.index and 'Stock Based Compensation' in cash_flow.index:
                cash_flow.loc['Free Cash Flow Adjusted Stock Based Compensation'] = cash_flow.loc['Free Cash Flow'] - \
                                                            cash_flow.loc['Stock Based Compensation']
            else:
                st.error(f"Could not calculate Free Cash Flow adjusted for stock-based compensation for {symbol}")

        # Calculate current PE ratio
        # get newest eps in income_statement if newest eps is none get the second newest
        eps = income_statement.loc['Diluted EPS'].iloc[0]
        if np.isnan(eps):
            eps = income_statement.loc['Diluted EPS'].iloc[1]
        current_pe = currentPrice / eps

        # Calculate free cash flow per share and free cash flow per share adjusted for stock-based compensation
        free_cash_flow_per_share = cash_flow.loc['Free Cash Flow'].iloc[0] / sharesOutstanding
        free_cash_flow_per_share_adjusted = (cash_flow.loc['Free Cash Flow Adjusted Stock Based Compensation'].iloc[0]
                                             / sharesOutstanding)

        # Calculate free cash flow yield and free cash flow yield adjusted for stock-based compensation
        free_cash_flow_yield = cash_flow.loc['Free Cash Flow'].iloc[0] / market_cap
        free_cash_flow_yield_adjusted = (cash_flow.loc['Free Cash Flow Adjusted Stock Based Compensation'].iloc[0]
                                          / market_cap)

        # Change to format percent
        free_cash_flow_yield = f"{free_cash_flow_yield:.2%}"
        free_cash_flow_yield_adjusted = f"{free_cash_flow_yield_adjusted:.2%}"

        return {
            'income_statement': income_statement,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'market_cap': market_cap,
            'sharesOutstanding': sharesOutstanding,
            'currentPrice': currentPrice,
            'currentPE': current_pe,
            'forwardPE': forwardPE,
            'free_cash_flow_per_share': free_cash_flow_per_share,
            'free_cash_flow_per_share_adjusted': free_cash_flow_per_share_adjusted,
            'free_cash_flow_yield': free_cash_flow_yield,
            'free_cash_flow_yield_adjusted': free_cash_flow_yield_adjusted
        }
    except Exception as e:
        st.error(f"Error fetching financial data for {symbol}: {e}")
        return None