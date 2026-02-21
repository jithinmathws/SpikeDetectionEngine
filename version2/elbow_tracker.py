import pandas as pd


class ElbowTracker:

    def track_elbows(self, df: pd.DataFrame, spikes: pd.DataFrame):

        events = []

        for _, spike in spikes.iterrows():

            spike_time = spike["time"]
            spike_dir = spike["direction"]

            # start tracking from next candle
            subset = df[df["time"] > spike_time].copy()

            elbow_double_occurred = False
            consecutive_opposing = 0
            reversal_starting = False

            for _, row in subset.iterrows():

                is_red = row["close"] < row["open"]
                is_green = row["close"] > row["open"]

                opposing = (
                    (spike_dir == "BULLISH" and is_red) or
                    (spike_dir == "BEARISH" and is_green)
                )

                if opposing:
                    consecutive_opposing += 1
                else:

                    # pause ended → check if we had a double
                    if consecutive_opposing == 2:

                        if not elbow_double_occurred:
                            elbow_double_occurred = True

                        else:
                            reversal_starting = True

                            events.append({
                                "spike_time": spike_time,
                                "reversal_time": row["time"],
                                "direction": spike_dir
                            })

                            break

                    consecutive_opposing = 0

        return pd.DataFrame(events)