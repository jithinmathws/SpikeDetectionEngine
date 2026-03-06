import pandas as pd

class ElbowTracker:

    def track(self, df, spikes, lookahead=60):

        opens = df["open"].values
        closes = df["close"].values
        times = df["time"].values
        # Create a mapping for quick index lookup based on timestamp
        idx = {t:i for i,t in enumerate(times)}

        events=[]

        for _, spike in spikes.iterrows():

            s = idx.get(spike.time)
            if s is None:
                continue

            direction = spike.direction
            first_wave_confirmed = False
            count = 0

            # Scan forward from the spike to find two distinct waves of opposite candles
            for j in range(s + 1, min(s + lookahead, len(df))):

                body = abs(closes[j] - opens[j])

                # Candle definitions based on body size threshold
                is_red = closes[j] < opens[j] and body > 0.15
                is_green = closes[j] > opens[j] and body > 0.15

                # Ignore the immediate candle following the spike to allow for spread/noise
                if j == s + 1:
                    continue

                # Identify if current candle opposes the spike direction
                is_opposite = (direction == "BULLISH" and is_red) or \
                              (direction == "BEARISH" and is_green)

                if is_opposite:
                    count += 1
                else:
                    # UPDATED: If we have at least 2 opposite candles, a wave is identified
                    if count >= 2:
                        if not first_wave_confirmed:
                            # First exhaustion attempt found, reset to look for the second
                            first_wave_confirmed = True
                        else:
                            # Second exhaustion attempt found; this confirms the 'Elbow'
                            events.append((spike.time, times[j], direction))
                            break
                    
                    # Reset counter if the streak of opposite candles is broken
                    count = 0

        return pd.DataFrame(events,
                            columns=["spike_time", "reversal_time", "direction"])