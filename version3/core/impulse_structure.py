import pandas as pd
import bisect

class ImpulseStructure:

    def find_swings(self, df, window=2):
        highs = df["high"].values
        lows  = df["low"].values

        swing_highs = []
        swing_lows  = []

        for i in range(window, len(df)-window):
            if highs[i] == max(highs[i-window:i+window+1]):
                swing_highs.append(i)
            if lows[i] == min(lows[i-window:i+window+1]):
                swing_lows.append(i)

        return swing_highs, swing_lows

    def classify(self, df, spikes):
        times = df["time"].values
        highs = df["high"].values
        lows  = df["low"].values
        opens = df["open"].values
        closes = df["close"].values

        idx = {t:i for i,t in enumerate(times)}
        swing_highs, swing_lows = self.find_swings(df)
        events = []

        for _, sp in spikes.iterrows():
            i = idx.get(sp["time"])
            if i is None:
                continue

            extreme = sp["extreme"]

            # find last swing high BEFORE spike
            k_h = bisect.bisect_left(swing_highs, i)
            prev_sh = swing_highs[k_h-1] if k_h > 0 else None

            # find last swing low BEFORE spike
            k_l = bisect.bisect_left(swing_lows, i)
            prev_sl = swing_lows[k_l-1] if k_l > 0 else None

            if prev_sh is None or prev_sl is None:
                continue

            # Get Wick Extremes
            last_high = highs[prev_sh]
            last_low  = lows[prev_sl]
            
            # GET BODY EXTREMES (For your Shift logic)
            last_high_body = max(opens[prev_sh], closes[prev_sh])
            last_low_body  = min(opens[prev_sl], closes[prev_sl])

            # BULLISH IMPULSE = break last swing high
            if sp["direction"] == "BULLISH" and extreme > last_high:
                events.append({
                    "time": sp["time"],
                    "trend": "UP",
                    "HL": last_low,
                    "HL_body": last_low_body,
                    "HH": extreme
                })

            # BEARISH IMPULSE = break last swing low
            elif sp["direction"] == "BEARISH" and extreme < last_low:
                events.append({
                    "time": sp["time"],
                    "trend": "DOWN",
                    "LH": last_high,
                    "LH_body": last_high_body,
                    "LL": extreme
                })

        return pd.DataFrame(events)