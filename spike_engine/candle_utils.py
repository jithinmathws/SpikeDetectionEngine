# candle_utils.py
import pandas as pd


# =========================
# CONFIGURABLE PARAMETERS
# =========================
NEUTRAL_BODY_RATIO = 0.10
# A candle is neutral if body <= 10% of total range


# =========================
# CORE CALCULATIONS
# =========================
def calculate_candle_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the DataFrame with candle metrics and direction classification.

    Adds columns:
    - body
    - range
    - upper_wick
    - lower_wick
    - direction  (bull / bear / neutral)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: open, high, low, close

    Returns
    -------
    pd.DataFrame
        Same DataFrame with added columns
    """

    # -------------------------
    # PRICE METRICS
    # -------------------------
    df["body"] = (df["close"] - df["open"]).abs()
    df["range"] = df["high"] - df["low"]

    # Avoid division issues
    df["range"].replace(0, 1e-9, inplace=True)

    df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]

    # -------------------------
    # DIRECTION CLASSIFICATION
    # -------------------------
    df["direction"] = "neutral"

    bull_mask = (df["close"] > df["open"]) & (
        df["body"] / df["range"] > NEUTRAL_BODY_RATIO
    )

    bear_mask = (df["close"] < df["open"]) & (
        df["body"] / df["range"] > NEUTRAL_BODY_RATIO
    )

    df.loc[bull_mask, "direction"] = "bull"
    df.loc[bear_mask, "direction"] = "bear"

    return df
