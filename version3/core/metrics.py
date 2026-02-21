def print_stats(spikes, reversals):

    print("\n--- SPIKE STATS ---")
    print("Total spikes:",len(spikes))

    if len(spikes):
        days = spikes["time"].dt.date.nunique()
        print("Spikes/day:", round(len(spikes)/days,2))

    print("\n--- REVERSAL STATS ---")
    print("Total reversals:",len(reversals))

    if len(spikes):
        rate = len(reversals)/len(spikes)*100
        print("Reversal rate:", round(rate,2),"%")