import os
import pandas as pd
import numpy as np

from elbow_tracker import ElbowTracker

class SpikeDetector:
    def __init__(
        self,
        min_window=7,
        max_window=15,
        pip_size=0.01,
        pip_move_pips=500,
        volume_lookback=100,
        volume_sigma=2,
    ):
        self.min_window = min_window
        self.max_window = max_window
        self.pip_move = pip_move_pips * pip_size
        self.volume_lookback = volume_lookback
        self.volume_sigma = volume_sigma

    def detect_spikes(self, df: pd.DataFrame) -> pd.DataFrame:

        spikes = []

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        volumes = df["volume"].values
        times = df["time"].values
        h4pos = df["minute_in_h4"].values

        i = self.max_window
        while i < len(df):

            # Phase-1 time filter
            minute = h4pos[i]
            if not (180 <= minute <= 225):
                i += 1
                continue

            for window in range(self.min_window, self.max_window + 1):

                start_idx = i - window
                start_price = closes[start_idx]

                window_high = np.max(highs[start_idx:i+1])
                window_low  = np.min(lows[start_idx:i+1])

                bullish_move = window_high - start_price
                bearish_move = window_low - start_price

                spike_direction = None

                if bullish_move >= self.pip_move:
                    spike_direction = "BULLISH"
                    net_move = bullish_move
                    spike_extreme = window_high

                elif bearish_move <= -self.pip_move:
                    spike_direction = "BEARISH"
                    net_move = bearish_move
                    spike_extreme = window_low

                if spike_direction is None:
                    continue

                spikes.append(
                    {
                        "time": times[i],
                        "direction": spike_direction,
                        "start_price": start_price,
                        "end_price": closes[i],
                        "extreme": spike_extreme,
                        "window_size": window,
                        "net_move": net_move,
                    }
                )

                # Skip forward to avoid duplicates
                i += self.max_window
                break
            else:
                i += 1

        # ==========================================================
        # CUSTOM DATE FILTER (EDIT THESE)
        # ==========================================================

        START_DATE = "2023-01-10"
        END_DATE   = "2023-03-15"

        start_ts = pd.Timestamp(START_DATE)
        end_ts   = pd.Timestamp(END_DATE) + pd.Timedelta(days=1)

        df = df[(df["time"] >= start_ts) & (df["time"] < end_ts)]

        print(f"\nFiltered data from {START_DATE} to {END_DATE}")
        print("Rows remaining:", len(df))

        tracker = ElbowTracker()
        reversals = tracker.track_elbows(df, pd.DataFrame(spikes))

        print("Reversals detected:", len(reversals))
        print(reversals.head())

        return pd.DataFrame(spikes)

