import pandas as pd

def load_data(path):

    # Try reading with header first
    df = pd.read_csv(path)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # If header not present, reload correctly
    if "date" not in df.columns:
        df = pd.read_csv(
            path,
            header=None,
            names=["date","time","open","high","low","close","volume"]
        )

    # Convert to string before combining
    df["date"] = df["date"].astype(str)
    df["time"] = df["time"].astype(str)

    # Merge date + time
    df["time"] = pd.to_datetime(
        df["date"] + " " + df["time"],
        errors="coerce"
    )

    df = df.drop(columns=["date"])
    df = df.dropna().reset_index(drop=True)

    # Convert numeric columns safely
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna().reset_index(drop=True)
    df = df.sort_values("time").reset_index(drop=True)

    # H4 positioning
    df["h4_start"] = df["time"].dt.floor("4h")
    df["minute_in_h4"] = ((df["time"] - df["h4_start"]).dt.total_seconds() // 60).astype(int)

    return df