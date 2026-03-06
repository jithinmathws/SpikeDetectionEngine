# import pandas as pd

# def load_data(path):

#     # Read semicolon-separated file
#     df = pd.read_csv(path, sep=";")

#     # Normalize column names
#     df.columns = [c.strip().lower() for c in df.columns]

#     # Rename to engine format
#     rename_map = {
#         "date": "time",
#         "open": "open",
#         "high": "high",
#         "low": "low",
#         "close": "close",
#         "volume": "volume"
#     }

#     df = df.rename(columns=rename_map)

#     # Parse datetime
#     df["time"] = pd.to_datetime(
#         df["time"],
#         format="%Y.%m.%d %H:%M",
#         errors="coerce"
#     )

#     # Convert numeric columns
#     for c in ["open","high","low","close","volume"]:
#         df[c] = pd.to_numeric(df[c], errors="coerce")

#     # Drop bad rows
#     df = df.dropna().reset_index(drop=True)

#     # Sort chronologically
#     df = df.sort_values("time").reset_index(drop=True)

#     # H4 positioning (same as before)
#     df["h4_start"] = df["time"].dt.floor("4h")
#     df["minute_in_h4"] = (
#         (df["time"] - df["h4_start"]).dt.total_seconds() // 60
#     ).astype(int)

#     return df

import MetaTrader5 as mt5
import pandas as pd
import time

def fetch_live_data(symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M1, bars=300):
    # 1. Pull the latest bars
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    
    # 2. Safety Check: Did MT5 actually return data?
    if rates is None or len(rates) == 0:
        print(f"[!] Failed to pull data for {symbol}. Check MT5 connection and symbol name.")
        return None
    
    # 3. Convert to pandas DataFrame
    df = pd.DataFrame(rates)
    
    # 4. Convert MT5 Unix timestamp to pandas datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # 5. Rename columns to match your engine
    df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    
    # 6. RE-ADD THE H4 WINDOWING LOGIC (Crucial for your SpikeDetector)
    df["h4_start"] = df["time"].dt.floor("4h")
    df["minute_in_h4"] = (
        (df["time"] - df["h4_start"]).dt.total_seconds() // 60
    ).astype(int)
    
    return df