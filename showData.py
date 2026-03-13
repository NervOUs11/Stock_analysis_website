import pandas as pd
import streamlit as st
import altair as alt


def display_financial_statement(title: str, df: pd.DataFrame) -> None:
    st.subheader(title)
    if df is not None and not df.empty:
        df = df.copy()  # Avoid modifying original

        # Convert values to numeric just in case, then divide by 1M (except EPS)
        for row in df.index:
            if row not in ["Basic EPS", "Diluted EPS"]:
                # Use pd.to_numeric to avoid errors if there are string 'NaN's
                df.loc[row] = pd.to_numeric(df.loc[row], errors='coerce') / 1e6

        # Format the numbers to strings with commas and 2 decimal places
        df = df.map(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")

        # Format the dates for display
        if isinstance(df.columns, pd.DatetimeIndex):
            df.columns = df.columns.strftime('%Y-%m-%d')
        else:
            try:
                df.columns = pd.to_datetime(df.columns).strftime('%Y-%m-%d')
            except Exception:
                pass

        st.dataframe(df, use_container_width=True)
    else:
        st.write(f"No {title} available.")


def display_financial_chart(title: str, df: pd.DataFrame, metrics: any, colors: list = None) -> None:
    st.subheader(title)

    if df is not None and not df.empty:
        # 1. Standardize input: Ensure 'metrics' is always a list
        if isinstance(metrics, str):
            metrics = [metrics]

        # Filter only existing rows to prevent errors
        existing_metrics = [m for m in metrics if m in df.index]
        if not existing_metrics:
            st.warning(f"Metrics {metrics} not found in the data.")
            return

        # 2. Prepare Data (Transpose and Reset)
        chart_data = df.loc[existing_metrics].T.reset_index()
        chart_data.columns = ['Date'] + existing_metrics

        # 3. Melt data for Altair (Long Format)
        chart_data = chart_data.melt(id_vars=['Date'], var_name='Metric', value_name='Value')

        # Clean Dates and Numeric Values
        chart_data['Date'] = pd.to_datetime(chart_data['Date']).dt.strftime('%Y')
        chart_data['Value'] = pd.to_numeric(chart_data['Value'], errors='coerce')

        # 4. Define the Chart Logic
        # If only one metric, we don't need a legend or grouping
        is_single = len(existing_metrics) == 1

        base_chart = alt.Chart(chart_data).mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        ).encode(
            y=alt.Y('Value:Q', title='Millions'),
            tooltip=['Date', 'Metric', alt.Tooltip('Value:Q', format=',.2f')]
        )

        # Determine the number of unique dates (years)
        num_years = len(chart_data['Date'].unique())

        # We set a consistent width for each "group" of bars
        # This ensures the bars don't look huge in single mode and tiny in grouped mode
        group_width = 120

        if is_single:
            # Simple Bar Chart
            chart = base_chart.encode(
                x=alt.X('Date:O', title='Fiscal Year', axis=alt.Axis(labelAngle=0)),
                color=alt.value(colors[0] if colors else "#0068c9")
            ).properties(
                width=group_width * num_years,  # Total width based on number of years
                height=400
            )
        else:
            # Grouped Bar Chart
            chart = base_chart.encode(
                x=alt.X('Metric:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
                color=alt.Color('Metric:N', scale=alt.Scale(range=colors) if colors else alt.Scheme('tableau10')),
                column=alt.Column('Date:O', title='Fiscal Year', spacing=15)
            ).properties(
                width=group_width,  # Each year group gets the same fixed width
                height=400
            )

        st.altair_chart(chart, use_container_width=False)
    else:
        st.info("No data available.")