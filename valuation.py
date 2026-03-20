def calculate_dcf(fcf, growth_rate=0.05, discount_rate=0.10, terminal_growth=0.02, years=5):
    """
    Calculates the Intrinsic Value of a company using a 2-stage DCF model.

    :param fcf: The most recent Free Cash Flow (Ttm)
    :param growth_rate: Expected annual growth for the next 'years' (e.g., 0.05 for 5%)
    :param discount_rate: The WACC or required rate of return (e.g., 0.10 for 10%)
    :param terminal_growth: Perpetual growth rate after the projection period (usually 2-3%)
    :param years: Number of years to project forward
    :return: Total Enterprise Value (Present Value of all future cash flows)
    """
    try:
        projected_fcfs = []
        present_values = []

        # --- Stage 1: Projection Period ---
        current_fcf = fcf
        for i in range(1, years + 1):
            # Grow the FCF
            current_fcf = current_fcf * (1 + growth_rate)
            projected_fcfs.append(current_fcf)

            # Discount to Present Value: PV = FCF / (1 + r)^n
            pv = current_fcf / ((1 + discount_rate) ** i)
            present_values.append(pv)

        # --- Stage 2: Terminal Value (Gordon Growth Model) ---
        # TV = [FCF_final * (1 + terminal_growth)] / (discount_rate - terminal_growth)
        final_fcf = projected_fcfs[-1]
        terminal_value = (final_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)

        # Discount Terminal Value to Present Day
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)

        # Total Value = Sum of PV of Projections + PV of Terminal Value
        enterprise_value = sum(present_values) + pv_terminal_value

        return enterprise_value

    except ZeroDivisionError:
        return 0