import pandas as pd

class TradeSimulator:

    def run(self, df, trades, max_bars=500):

        highs = df["high"].values
        lows  = df["low"].values
        times = df["time"].values

        idx = {t:i for i,t in enumerate(times)}

        results = []

        for _, t in trades.iterrows():

            i = idx.get(t["time"])
            if i is None:
                continue

            entry = t["entry"]
            sl = t["sl"]
            tp = t["tp"]
            direction = t["direction"]

            outcome = "NO_FILL"
            exit_time = None
            filled = False

            for j in range(i+1, min(i+1+max_bars, len(df))):

                high = highs[j]
                low  = lows[j]

                # ---------------------------------
                # WAIT FOR ENTRY FILL FIRST
                # ---------------------------------
                if not filled:

                    if direction == "BUY" and low <= entry:
                        filled = True
                        entry_time = times[j]

                    elif direction == "SELL" and high >= entry:
                        filled = True
                        entry_time = times[j]

                    continue

                # ---------------------------------
                # AFTER FILL → CHECK SL/TP
                # ---------------------------------
                if direction == "BUY":

                    if low <= sl:
                        outcome = "LOSS"
                        exit_time = times[j]
                        break

                    if high >= tp:
                        outcome = "WIN"
                        exit_time = times[j]
                        break

                else:

                    if high >= sl:
                        outcome = "LOSS"
                        exit_time = times[j]
                        break

                    if low <= tp:
                        outcome = "WIN"
                        exit_time = times[j]
                        break

            results.append({
                "signal_time": t["time"],
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "direction": direction,
                "result": outcome,
                "exit_time": exit_time
            })

        return pd.DataFrame(results)