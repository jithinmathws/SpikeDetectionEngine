# spike_metrics.py
import pandas as pd


def spikes_to_dataframe(spikes: list, symbol: str) -> pd.DataFrame:
    """
    Convert detected spike objects into a structured DataFrame.

    Parameters
    ----------
    spikes : list of dict
        Output from spike_detector.detect_spikes()
    symbol : str
        Trading symbol

    Returns
    -------
    pd.DataFrame
        Client-ready spike report
    """

    rows = []

    for spike in spikes:
        rows.append({
            "symbol": symbol,
            "start_time_utc8": spike["start_time"],
            "end_time_utc8": spike["end_time"],
            "direction": spike["direction"],
            "spike_size_pips": spike["spike_pips"],
            "duration_minutes": spike["duration_minutes"],
            "candle_count": spike["candles"],
            "opposing_candles": spike["opposing_candles"],
            "elbow_type": spike["elbow_type"],
            "h4_final_hour": spike["h4_final_hour"]
        })


    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Ensure proper sorting
    df.sort_values("start_time_utc8", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

def compare_h4_context(df):
    """
    Compare spike quality with vs without H4 final-hour context.
    """

    summary = []

    for flag, label in [(False, "Outside H4 Final Hour"), (True, "Inside H4 Final Hour")]:
        subset = df[df["h4_final_hour"] == flag]

        if subset.empty:
            continue

        summary.append({
            "context": label,
            "spike_count": len(subset),
            "avg_spike_size_pips": round(subset["spike_size_pips"].mean(), 2),
            "avg_duration_min": round(subset["duration_minutes"].mean(), 2),
            "avg_candles": round(subset["candle_count"].mean(), 2),
            "pct_single_or_none_elbow": round(
                (subset["opposing_candles"] <= 1).mean() * 100, 2
            )
        })

    return pd.DataFrame(summary)
