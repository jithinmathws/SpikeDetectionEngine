import pandas as pd

def load_data(path):

    # Read semicolon-separated file
    df = pd.read_csv(path, sep=";")

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename to engine format
    rename_map = {
        "date": "time",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    }

    df = df.rename(columns=rename_map)

    # Parse datetime
    df["time"] = pd.to_datetime(
        df["time"],
        format="%Y.%m.%d %H:%M",
        errors="coerce"
    )

    # Convert numeric columns
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Drop bad rows
    df = df.dropna().reset_index(drop=True)

    # Sort chronologically
    df = df.sort_values("time").reset_index(drop=True)

    # H4 positioning (same as before)
    df["h4_start"] = df["time"].dt.floor("4h")
    df["minute_in_h4"] = (
        (df["time"] - df["h4_start"]).dt.total_seconds() // 60
    ).astype(int)

    return df