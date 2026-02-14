# data_loader.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz


# =========================
# TIMEZONES
# =========================
UTC = pytz.UTC
UTC_PLUS_8 = pytz.timezone("Asia/Singapore")  # UTC+8 standard

print("LOADED data_loader.py FROM:", __file__)


# =========================
# MT5 CONNECTION HANDLING
# =========================
def initialize_mt5():
    """
    Initialize MetaTrader 5 connection.
    """
    if not mt5.initialize():
        raise RuntimeError("MetaTrader5 initialization failed")


def shutdown_mt5():
    """
    Shutdown MetaTrader 5 connection.
    """
    mt5.shutdown()


# =========================
# DATA LOADER
# =========================
def load_m1_data(
    symbol: str,
    start_time: datetime,
    end_time: datetime
) -> pd.DataFrame:
    """
    Load M1 OHLC data from MT5, convert time to UTC+8,
    annotate session gaps, and return a clean pandas DataFrame.

    Parameters
    ----------
    symbol : str
        Trading symbol (e.g. 'XAUUSD', 'USDJPY')
    start_time : datetime
        Start time (UTC timezone-aware)
    end_time : datetime
        End time (UTC timezone-aware)

    Returns
    -------
    pd.DataFrame
        Columns:
        time, open, high, low, close, volume, session_gap
    """

    # -------------------------
    # SAFETY CHECKS
    # -------------------------
    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise ValueError("start_time and end_time must be timezone-aware (UTC)")

    if end_time > datetime.now(tz=UTC):
        raise ValueError("end_time cannot be in the future")

    initialize_mt5()

    try:
        # Ensure symbol is available
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Failed to select symbol: {symbol}")

        # Pull M1 data
        rates = mt5.copy_rates_range(
            symbol,
            mt5.TIMEFRAME_M1,
            start_time,
            end_time
        )

        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No data returned for {symbol}")

        df = pd.DataFrame(rates)

    finally:
        shutdown_mt5()

    # -------------------------
    # DATA CLEANING
    # -------------------------
    # Convert timestamp to UTC+8
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["time"] = df["time"].dt.tz_convert(UTC_PLUS_8)

    # Rename volume column
    df.rename(columns={"tick_volume": "volume"}, inplace=True)

    # Keep required columns only
    df = df[
        ["time", "open", "high", "low", "close", "volume"]
    ]

    # Sort chronologically
    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # -------------------------
    # SESSION GAP ANNOTATION
    # -------------------------
    # True when gap > 1 minute (Gold daily breaks, weekends, etc.)
    df["session_gap"] = df["time"].diff() > pd.Timedelta(minutes=1)

    return df
