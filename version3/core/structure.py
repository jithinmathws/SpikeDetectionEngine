import pandas as pd
import numpy as np

def find_swings(df, lookback=3):

    highs = df["high"].values
    lows  = df["low"].values
    times = df["time"].values

    swings = []

    for i in range(lookback, len(df)-lookback):

        window_high = highs[i-lookback:i+lookback+1]
        window_low  = lows[i-lookback:i+lookback+1]

        if highs[i] == np.max(window_high):
            swings.append((times[i], "HIGH", highs[i]))

        elif lows[i] == np.min(window_low):
            swings.append((times[i], "LOW", lows[i]))

    return pd.DataFrame(swings, columns=["time","type","price"])