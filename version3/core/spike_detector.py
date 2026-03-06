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

            # Time-of-day filter (H4 windowing)
            if "minute_in_h4" in df.columns:
                if not (180 <= df["minute_in_h4"].iloc[i] <= 225):
                    i += 1
                    continue

            for w in range(self.min_w, self.max_w + 1):

                start = i - w
                
                # FIXED: Use Open of start candle to avoid mid-candle bias
                start_price = opens[start] 

                # FIXED: Use current close to verify move completion at point-in-time
                current_close = closes[i]

                # BULLISH displacement
                if current_close - start_price >= self.pip_move:
                    # Record the highest high reached during the window
                    window_extreme = np.max(highs[start:i+1])
                    spikes.append((times[i], "BULLISH", start_price, window_extreme))
                    i += self.max_w # Skip forward to avoid overlapping detections
                    detected = True
                    break

                # BEARISH displacement
                if start_price - current_close >= self.pip_move:
                    # Record the lowest low reached during the window
                    window_extreme = np.min(lows[start:i+1])
                    spikes.append((times[i], "BEARISH", start_price, window_extreme))
                    i += self.max_w
                    detected = True
                    break

            if not detected:
                i += 1

        return pd.DataFrame(
            spikes,
            columns=["time","direction","start","extreme"]
        )