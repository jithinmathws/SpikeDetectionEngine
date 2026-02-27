import pandas as pd

class InternalWeaknessDetector:

    def detect(self, df, impulses, lookahead=100, min_delay=3):

        opens  = df["open"].values
        closes = df["close"].values
        highs  = df["high"].values
        lows   = df["low"].values
        times  = df["time"].values

        idx = {t:i for i,t in enumerate(times)}

        events = []

        for n, imp in impulses.iterrows():

            i = idx.get(imp["time"])
            if i is None:
                continue

            trend = imp["trend"]

            # skip invalid structure rows
            if trend == "UP" and pd.isna(imp["HL"]):
                continue
            if trend != "UP" and pd.isna(imp["LH"]):
                continue

            # boundary of next impulse
            if n < len(impulses)-1:
                next_imp = idx.get(impulses.iloc[n+1]["time"])
            else:
                next_imp = None

            end = min(i + lookahead, len(df))
            if next_imp:
                end = min(end, next_imp)

            for j in range(i + min_delay, end):

                body = abs(closes[j] - opens[j])

                # -----------------------------
                # SELL shift → body below HL
                # -----------------------------
                if trend == "UP":

                    body_high = max(opens[j], closes[j])

                    if body_high < imp["HL"] and body > 0.15:
                        events.append({
                            "shift_time": times[j],
                            "direction": "SELL",
                            "trend": imp["trend"],
                            "HL": imp["HL"],
                            "HH": imp["HH"]
                        })
                        break

                # -----------------------------
                # BUY shift → body above LH
                # -----------------------------
                else:

                    body_low = min(opens[j], closes[j])

                    if body_low > imp["LH"] and body > 0.15:
                        events.append({
                            "shift_time": times[j],
                            "direction": "BUY",
                            "trend": imp["trend"],
                            "LH": imp["LH"],
                            "LL": imp["LL"]
                        })
                        break

        return pd.DataFrame(events)