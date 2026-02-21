from core.data_loader import load_data
from core.spike_detector import SpikeDetector
from core.elbow_tracker import ElbowTracker
from core.metrics import print_stats
from core.wickless_finder import WicklessFinder
import config

df = load_data("data/XAUUSD_M1.csv")

# filter dates
df = df[(df.time>=config.START_DATE) & (df.time<=config.END_DATE)]

detector = SpikeDetector(
    config.PIP_SIZE,
    config.SPIKE_PIPS,
    config.MIN_WINDOW,
    config.MAX_WINDOW
)

spikes = detector.detect(df)

tracker = ElbowTracker()
reversals = tracker.track(df,spikes,config.LOOKAHEAD)

finder = WicklessFinder()
entries = finder.find_entries(df, reversals)

print("\n--- Wickless Entry Stats ---")
print("Entries found:", len(entries))
print(entries.head())

print_stats(spikes,reversals)