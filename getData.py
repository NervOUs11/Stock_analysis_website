import yfinance as yf
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
        if income_statement is None:
            st.error(f"⚠️ No income statement data for {symbol}.")
        if balance_sheet is None:
            st.error(f"⚠️ No balance sheet data for {symbol}.")
        if cash_flow is None:
            st.error(f"⚠️ No cash flow data for {symbol}.")

        # Limit the data to the specified number of years
        if income_statement is not None and not income_statement.empty:
            income_statement = income_statement.iloc[:, :years] if income_statement.shape[1] > years else income_statement
            income_statement = income_statement.reindex(
                ["Total Revenue", "Gross Profit", "Operating Income",
                 "Pretax Income", "Tax Provision", "Net Income", "Basic EPS", "Diluted EPS"]
            ).dropna(how='all')

        if balance_sheet is not None and not balance_sheet.empty:
            balance_sheet = balance_sheet.iloc[:, :years] if balance_sheet.shape[1] > years else balance_sheet
            balance_sheet = balance_sheet.reindex(
                ["Current Assets", "Total Assets", "Current Liabilities",
                 "Total Liabilities Net Minority Interest", "Long Term Debt", "Retained Earnings",
                 "Stockholders Equity"]
            ).dropna(how='all')

            # SUM Stockholders Equity and Total Liabilities
            if ('Total Liabilities Net Minority Interest' in balance_sheet.index
                    and 'Stockholders Equity' in balance_sheet.index):
                balance_sheet.loc['Total Liabilities and Equity'] = balance_sheet.loc[
                                                                    'Total Liabilities Net Minority Interest'] + \
                                                                    balance_sheet.loc['Stockholders Equity']
            # No else here, as the calculation is skipped if indices are missing

        if cash_flow is not None and not cash_flow.empty:
            cash_flow = cash_flow.iloc[:, :years] if cash_flow.shape[1] > years else cash_flow
            cash_flow = cash_flow.reindex(["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
                                           "Common Stock Dividend Paid", "Repurchase Of Capital Stock",
                                           "Capital Expenditure", "Stock Based Compensation",
                                           "Free Cash Flow"]).dropna(how='all')

            # Calculate Free Cash Flow adjusted for stock-based compensation
            if 'Free Cash Flow' in cash_flow.index and 'Stock Based Compensation' in cash_flow.index:
                cash_flow.loc['FCF Adjusted Stock Based Compensation'] = cash_flow.loc['Free Cash Flow'] - \
                                                            cash_flow.loc['Stock Based Compensation']
            # No else here, as the calculation is skipped if indices are missing

        current_pe = None
        if income_statement is not None and 'Diluted EPS' in income_statement.index and currentPrice is not None:
            eps_series = income_statement.loc['Diluted EPS'].dropna()
            if not eps_series.empty:
                eps = eps_series.iloc[0]
                if not np.isnan(eps) and eps != 0:
                    current_pe = currentPrice / eps

        free_cash_flow_per_share = None
        free_cash_flow_per_share_adjusted = None
        free_cash_flow_yield = None
        free_cash_flow_yield_adjusted = None

        if cash_flow is not None and sharesOutstanding is not None and market_cap is not None:
            if 'Free Cash Flow' in cash_flow.index:
                fcf = cash_flow.loc['Free Cash Flow'].iloc[0]
                if not np.isnan(fcf) and sharesOutstanding != 0 and market_cap != 0:
                    free_cash_flow_per_share = fcf / sharesOutstanding
                    free_cash_flow_yield = f"{fcf / market_cap:.2%}"

            if 'FCF Adjusted Stock Based Compensation' in cash_flow.index:
                fcf_adjusted = cash_flow.loc['FCF Adjusted Stock Based Compensation'].iloc[0]
                if not np.isnan(fcf_adjusted) and sharesOutstanding != 0 and market_cap != 0:
                    free_cash_flow_per_share_adjusted = fcf_adjusted / sharesOutstanding
                    free_cash_flow_yield_adjusted = f"{fcf_adjusted / market_cap:.2%}"

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
        st.error(f"Oops! Something went wrong fetching data for {symbol}: {e}")
        return None