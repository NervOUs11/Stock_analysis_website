import pandas as pd


def safe_format(value, prefix=""):
    """
    Converts large numerical values into readable formats (K, M, B, T).
    Returns 'N/A' for missing or null data.
    """
    if value is None or pd.isna(value):
        return "N/A"
    if isinstance(value, str):
        return value

    val = float(value)

    if abs(val) >= 1000:
        for unit in ['', 'K', 'M', 'B', 'T']:
            if abs(val) < 1000:
                return f"{prefix}{val:,.1f}{unit}"
            val /= 1000

    return f"{prefix}{val:,.2f}"
