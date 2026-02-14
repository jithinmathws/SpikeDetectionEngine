# report_exporter_mt5.py
import os
import pandas as pd


def export_spikes_for_mt5(
    df: pd.DataFrame,
    symbol: str,
    output_dir: str = "mt5_report"
):
    """
    Export spike data in MT5-compatible CSV format.

    The CSV is intended to be read by an MT5 indicator.
    Datetime format: YYYY.MM.DD HH:MM (timezone-naive, UTC+8 local)

    Required columns in df:
    - start_time_utc8
    - end_time_utc8
    - direction
    - spike_size_pips
    - elbow_type
    """

    if df.empty:
        print(f"[INFO] No spikes to export for {symbol}")
        return

    # -------------------------
    # COPY & PREPARE
    # -------------------------
    mt5_df = df.copy()

    # Convert datetimes to MT5 string format
    mt5_df["start_time"] = mt5_df["start_time_utc8"].dt.strftime("%Y.%m.%d %H:%M")
    mt5_df["end_time"] = mt5_df["end_time_utc8"].dt.strftime("%Y.%m.%d %H:%M")

    # Select & order columns EXACTLY as MT5 expects
    mt5_df = mt5_df[
        [
            "start_time",
            "end_time",
            "direction",
            "spike_size_pips",
            "elbow_type",
        ]
    ]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct output path
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_MT5_Spikes_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)

    # Write CSV
    mt5_df.to_csv(output_path, index=False)

    print(f"[OK] MT5 spike CSV exported → {output_path}")
