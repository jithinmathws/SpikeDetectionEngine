import pandas as pd

class FibonacciEntry:

    def generate(self, shifts, deeper=True, sl_buffer=0.50):
        trades = []

        for _, imp in shifts.iterrows():
            trend = imp["trend"]

            # ----------------------------------
            # UP Impulse -> Shifted Down -> SELL Retracement
            # ----------------------------------
            if trend == "UP":
                hl = imp["HL"]
                hh = imp["HH"]

                if pd.isna(hl) or pd.isna(hh) or hh <= hl:
                    continue

                range_val = hh - hl
                
                # Fib drawn from Top (HH) down to Bottom (HL)
                fib40 = hh - (range_val * 0.40)
                fib55 = hh - (range_val * 0.55)

                entry = fib55 if deeper else fib40
                sl = hh + sl_buffer
                
                risk = abs(sl - entry)
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
            # DOWN Impulse -> Shifted Up -> BUY Retracement
            # ----------------------------------
            else:
                lh = imp["LH"]
                ll = imp["LL"]

                if pd.isna(lh) or pd.isna(ll) or lh <= ll:
                    continue

                range_val = lh - ll
                
                # Fib drawn from Bottom (LL) up to Top (LH)
                fib40 = ll + (range_val * 0.40)
                fib55 = ll + (range_val * 0.55)

                entry = fib55 if deeper else fib40
                sl = ll - sl_buffer

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