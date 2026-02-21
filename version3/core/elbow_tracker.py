import pandas as pd

class ElbowTracker:

    def track(self, df, spikes, lookahead=60):

        opens = df["open"].values
        closes = df["close"].values
        times = df["time"].values
        idx = {t:i for i,t in enumerate(times)}

        events=[]

        for _,spike in spikes.iterrows():

            s = idx[spike.time]
            dir = spike.direction

            first=False
            count=0

            for j in range(s+1, min(s+lookahead,len(df))):

                red = closes[j] < opens[j]
                green = closes[j] > opens[j]

                opp = (dir=="BULLISH" and red) or (dir=="BEARISH" and green)

                if opp:
                    count+=1
                else:
                    if count==2:
                        if not first:
                            first=True
                        else:
                            events.append((spike.time,times[j],dir))
                            break
                    count=0

        return pd.DataFrame(events,
                            columns=["spike_time","reversal_time","direction"])