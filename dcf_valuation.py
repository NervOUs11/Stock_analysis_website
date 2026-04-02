def calculate_dcf(fcf, growth_rate=0.05, discount_rate=0.10, terminal_growth=0.02, years=5):
    """
    Calculates the Intrinsic Value of a company using a 2-stage DCF model.
    """
    try:
        projected_fcfs = []
        present_values = []

        current_fcf = fcf
        for i in range(1, years + 1):
            current_fcf = current_fcf * (1 + growth_rate)
            projected_fcfs.append(current_fcf)
            pv = current_fcf / ((1 + discount_rate) ** i)
            present_values.append(pv)

        final_fcf = projected_fcfs[-1]
        terminal_value = (final_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)
        enterprise_value = sum(present_values) + pv_terminal_value

        return enterprise_value

    except ZeroDivisionError:
        return 0


def calculate_pe_valuation(current_eps, growth_rate, target_pe, years=5, discount_rate=0.10):
    """
    Estimates intrinsic stock price using an earnings growth + exit PE model.

    Projects EPS forward by 'years' at 'growth_rate', applies 'target_pe' to get a
    future stock price, then discounts that back to today at 'discount_rate'.

    :param current_eps:   Most recent diluted EPS
    :param growth_rate:   Annual EPS growth rate (e.g., 0.15 for 15%)
    :param target_pe:     Exit P/E multiple applied at the end of the projection
    :param years:         Projection horizon (default 5)
    :param discount_rate: Rate used to discount future price back to present (default 10%)
    :return:              Intrinsic stock price today
    """
    try:
        future_eps = current_eps * (1 + growth_rate) ** years
        future_price = future_eps * target_pe
        intrinsic_price = future_price / ((1 + discount_rate) ** years)
        return intrinsic_price
    except (ZeroDivisionError, TypeError):
        return 0


def calculate_fcf_valuation(current_fcf, shares_outstanding, growth_rate, target_multiple, years=5, discount_rate=0.10):
    """
    Estimates intrinsic stock price using a FCF growth + exit P/FCF multiple model.

    Projects FCF forward by 'years' at 'growth_rate', applies 'target_multiple' to get a
    future market cap, divides by shares to get a future price, then discounts back to today.

    :param current_fcf:       Most recent Free Cash Flow (TTM)
    :param shares_outstanding: Total shares outstanding
    :param growth_rate:       Annual FCF growth rate (e.g., 0.15 for 15%)
    :param target_multiple:   Exit Price/FCF multiple applied at the end of the projection
    :param years:             Projection horizon (default 5)
    :param discount_rate:     Rate used to discount future price back to present (default 10%)
    :return:                  Intrinsic stock price today
    """
    try:
        future_fcf = current_fcf * (1 + growth_rate) ** years
        future_price_per_share = (future_fcf * target_multiple) / shares_outstanding
        intrinsic_price = future_price_per_share / ((1 + discount_rate) ** years)
        return intrinsic_price
    except (ZeroDivisionError, TypeError):
        return 0