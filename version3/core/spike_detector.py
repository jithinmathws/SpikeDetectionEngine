import numpy as np
import pandas as pd

class SpikeDetector:

    def __init__(self, pip_size, spike_pips, min_w, max_w):
        self.pip_move = pip_size * spike_pips
        self.min_w = min_w
        self.max_w = max_w

    def detect(self, df):

        spikes = []

        highs  = df["high"].values
        lows   = df["low"].values
        closes = df["close"].values
        opens  = df["open"].values
        times  = df["time"].values

        i = self.max_w

        while i < len(df):

            detected = False

            if "minute_in_h4" in df.columns:
                if not (180 <= df["minute_in_h4"].iloc[i] <= 225):
                    i += 1
                    continue

            for w in range(self.min_w, self.max_w+1):

                start = i - w

                # Use candle midpoint instead of close
                start_price = (highs[start] + lows[start]) / 2

                window_high = np.max(highs[start:i+1])
                window_low  = np.min(lows[start:i+1])

                # BULLISH displacement
                if window_high - start_price >= self.pip_move:
                    spikes.append((times[i], "BULLISH", start_price, window_high))
                    i += self.max_w
                    detected = True
                    break

                # BEARISH displacement
                if start_price - window_low >= self.pip_move:
                    spikes.append((times[i], "BEARISH", start_price, window_low))
                    i += self.max_w
                    detected = True
                    break

            if not detected:
                i += 1

        return pd.DataFrame(
            spikes,
            columns=["time","direction","start","extreme"]
        )