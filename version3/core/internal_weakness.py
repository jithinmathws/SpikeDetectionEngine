import pandas as pd

class InternalWeaknessDetector:

    def detect(self, df, impulses, lookahead=100, min_delay=3):
        opens  = df["open"].values
        closes = df["close"].values
        times  = df["time"].values

        idx = {t:i for i,t in enumerate(times)}
        events = []

        for n, imp in impulses.iterrows():
            i = idx.get(imp["time"])
            if i is None:
                continue

            trend = imp["trend"]

            if trend == "UP" and pd.isna(imp["HL"]):
                continue
            if trend != "UP" and pd.isna(imp["LH"]):
                continue

            if n < len(impulses)-1:
                next_imp = idx.get(impulses.iloc[n+1]["time"])
            else:
                next_imp = None

            end = min(i + lookahead, len(df))
            if next_imp:
                end = min(end, next_imp)

            for j in range(i + min_delay, end):
                
                is_green = closes[j] > opens[j]
                is_red = closes[j] < opens[j]

                # -----------------------------
                # BULLISH SPIKE -> SELL SHIFT
                # Wait for RED candle close to break below HL body
                # -----------------------------
                if trend == "UP":
                    if is_red and closes[j] < imp["HL_body"]:
                        events.append({
                            "shift_time": times[j],
                            "direction": "SELL",
                            "trend": imp["trend"],
                            "HL": imp["HL"],
                            "HH": imp["HH"]
                        })
                        break

                # -----------------------------
                # BEARISH SPIKE -> BUY SHIFT
                # Wait for GREEN candle close to break above LH body
                # -----------------------------
                else:
                    if is_green and closes[j] > imp["LH_body"]:
                        events.append({
                            "shift_time": times[j],
                            "direction": "BUY",
                            "trend": imp["trend"],
                            "LH": imp["LH"],
                            "LL": imp["LL"]
                        })
                        break

        return pd.DataFrame(events)