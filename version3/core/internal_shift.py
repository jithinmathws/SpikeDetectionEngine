import pandas as pd

def detect_bearish_shift(df, swings):

    events = []

    closes = df["close"].values
    opens  = df["open"].values
    lows   = df["low"].values
    times  = df["time"].values

    swing_lows = swings[swings["type"]=="LOW"]

    for _, sw in swing_lows.iterrows():

        idx = df.index[df["time"] == sw["time"]]
        if len(idx)==0:
            continue

        i = idx[0]

        # scan forward few candles
        for j in range(i+1, min(i+5, len(df))):

            # bearish candle
            if closes[j] < opens[j]:

                # structure break
                if closes[j] < sw["price"]:

                    events.append({
                        "shift_time": times[j],
                        "broken_low": sw["price"]
                    })
                    break

    return pd.DataFrame(events)