import pandas as pd


class WicklessFinder:

    def find_entries(self, df, spikes, tolerance=0.00, lookahead=60):

        opens = df["open"].values
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        times = df["time"].values

        idx = {t:i for i,t in enumerate(times)}

        entries = []

        for i in range(len(spikes)):

            spike_time = spikes.iloc[i]["time"]
            direction = spikes.iloc[i]["direction"]

            s = idx.get(spike_time)
            if s is None:
                continue

            opposing_count = 0

            for j in range(s+1, min(s+1+lookahead, len(df))):

                o = opens[j]
                c = closes[j]
                h = highs[j]
                l = lows[j]

                red = c < o
                green = c > o

                if direction == "BULLISH":
                    opposing = red
                    wickless = (h - max(o,c)) <= tolerance
                    entry_type = "SELL"
                else:
                    opposing = green
                    wickless = (min(o,c) - l) <= tolerance
                    entry_type = "BUY"

                if opposing:
                    opposing_count += 1

                    if wickless:
                        entries.append({
                            "entry_time": times[j],
                            "direction": entry_type,
                            "spike_time": spike_time
                        })
                        break

                    if opposing_count >= 3:
                        break
                else:
                    opposing_count = 0

        return pd.DataFrame(entries)