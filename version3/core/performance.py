def report(results):

    total = len(results)
    wins = (results["result"]=="WIN").sum()
    losses = (results["result"]=="LOSS").sum()

    winrate = wins/total*100 if total else 0

    print("\n--- TRADE PERFORMANCE ---")
    print("Total trades:", total)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win rate:", round(winrate,2), "%")