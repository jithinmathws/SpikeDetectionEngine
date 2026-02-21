import numpy as np
import pandas as pd

class SpikeDetector:

    def __init__(self, pip_size, spike_pips, min_w, max_w):
        self.pip_move = pip_size * spike_pips
        self.min_w = min_w
        self.max_w = max_w

    def detect(self, df):

        spikes = []

        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        times = df["time"].values
        h4pos = df["minute_in_h4"].values

        i = self.max_w

        while i < len(df):

            if not (180 <= h4pos[i] <= 225):
                i += 1
                continue

            for w in range(self.min_w, self.max_w+1):

                start = i-w
                start_price = closes[start]

                high = np.max(highs[start:i+1])
                low  = np.min(lows[start:i+1])

                if high-start_price >= self.pip_move:
                    spikes.append((times[i],"BULLISH",start_price,high))
                    i += self.max_w
                    break

                if low-start_price <= -self.pip_move:
                    spikes.append((times[i],"BEARISH",start_price,low))
                    i += self.max_w
                    break
            else:
                i += 1

        return pd.DataFrame(spikes,
                            columns=["time","direction","start","extreme"])