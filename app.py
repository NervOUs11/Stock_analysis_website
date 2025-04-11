import pandas as pd
import streamlit as st
from getData import get_financial_data

st.set_page_config( page_title="Stock Financial Snapshot", layout="wide")

def display_financial_statement(title: str, df: pd.DataFrame) -> None:
    st.subheader(title)
    if isinstance(df, pd.DataFrame) and not df.empty: # Check if df is a DataFrame and not empty
        # Format the dates for display
        df = df.copy()  # avoid modifying original
        cols_to_convert = [col for col in df.index if col not in ["Basic EPS", "Diluted EPS"]]
        df.loc[cols_to_convert] = df.loc[cols_to_convert] / 1e6
        df = df.map(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
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
    st.title("💰 Stock Financial Snapshot")
    st.markdown("<p class='info-text'>Enter a stock symbol and country to get a quick financial overview.</p>", unsafe_allow_html=True)

    # image_url = "./image/image1.jpeg"
    # st.image(image_url, width=150)

    # User inputs
    input1, input2 = st.columns(2)
    with input1:
        stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL):").upper()
    with input2:
        country = st.text_input("Enter Country Where Stock Is Traded (e.g., US):").upper()

    if stock_symbol and country:
        if country == "US":
            full_symbol = stock_symbol
        else:
            full_symbol = f"{stock_symbol}.{country.upper()}"

        financial_data = get_financial_data(full_symbol, years=4)

        if financial_data:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Key Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Market Cap", f"{financial_data['market_cap']:,}")
                st.metric("Stock Price", f"{financial_data['currentPrice']:.2f}")
            with col2:
                st.metric("PE Ratio", f"{financial_data['currentPE']:.2f}")
                st.metric("Forward PE", f"{financial_data['forwardPE']:.2f}")

            st.subheader("Free Cash Flow")
            col3, col4 = st.columns(2)
            with col3:
                st.metric("FCF per Share", f"{financial_data['free_cash_flow_per_share']:.2f}")
                st.metric("FCF per Share (Adjusted)", f"{financial_data['free_cash_flow_per_share_adjusted']:.2f}")
            with col4:
                st.metric("FCF Yield", f"{financial_data['free_cash_flow_yield']}")
                st.metric("FCF Yield (Adjusted)", f"{financial_data['free_cash_flow_yield_adjusted']}")

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Financial Statements")
            display_financial_statement("Income Statement", financial_data['income_statement'])
            display_financial_statement("Cash Flow Statement", financial_data['cash_flow'])
            display_financial_statement("Balance Sheet", financial_data['balance_sheet'])
        else:
            st.error(
                f"Could not retrieve financial statements for {full_symbol}. Please check the symbol and country.")
    else:
        st.info("Enter a stock symbol and country to explore financial data.")


if __name__ == "__main__":
    main()