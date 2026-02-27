import pandas as pd

class FibonacciEntry:

    def generate(self, shifts, deeper=True):

        trades = []

        for _, imp in shifts.iterrows():

            trend = imp["trend"]

            # ----------------------------------
            # UP impulse → SELL retracement
            # ----------------------------------
            if trend == "UP":

                hl = imp["HL"]
                hh = imp["HH"]

                if pd.isna(hl) or pd.isna(hh) or hh <= hl:
                    continue

                fib40 = hl + (hh-hl)*0.40
                fib55 = hl + (hh-hl)*0.55

                entry = fib55 if deeper else fib40
                sl = hh + 0.01

                risk = abs(entry - sl)
                tp = entry - risk

                trades.append({
                    "time": imp["shift_time"],
                    "direction": "SELL",
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "fib40": fib40,
                    "fib55": fib55
                })

            # ----------------------------------
            # DOWN impulse → BUY retracement
            # ----------------------------------
            else:

                lh = imp["LH"]
                ll = imp["LL"]

                if pd.isna(lh) or pd.isna(ll) or lh <= ll:
                    continue

                fib40 = ll + (lh-ll)*0.40
                fib55 = ll + (lh-ll)*0.55

                entry = fib55 if deeper else fib40
                sl = ll - 0.01

                risk = abs(entry - sl)
                tp = entry + risk

                trades.append({
                    "time": imp["shift_time"],
                    "direction": "BUY",
                    "entry": entry,
                    "sl": sl,
                    "tp": tp,
                    "fib40": fib40,
                    "fib55": fib55
                })

        return pd.DataFrame(trades)