from core.data_loader import load_data
from core.spike_detector import SpikeDetector
from core.elbow_tracker import ElbowTracker
from core.impulse_structure import ImpulseStructure
from core.internal_weakness import InternalWeaknessDetector
from core.metrics import print_stats
from core.fib_entry import FibonacciEntry
from core.trade_simulator import TradeSimulator
from core.performance import report
from core.visualizer import TradeVisualizer

import config
import pandas as pd

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = load_data("data/XAUUSD_M1.csv")

start = pd.Timestamp(config.START_DATE)
end   = pd.Timestamp(config.END_DATE) + pd.Timedelta(days=1)
df = df[(df.time >= start) & (df.time < end)]

print("\nRows loaded:", len(df))

# --------------------------------------------------
# PHASE 1: SPIKE DETECTION
# --------------------------------------------------
detector = SpikeDetector(
    config.PIP_SIZE,
    config.SPIKE_PIPS,
    config.MIN_WINDOW,
    config.MAX_WINDOW
)

spikes = detector.detect(df)

if len(spikes):
    spikes = spikes.copy()
    spikes = spikes[["time","direction","start","extreme"]]

print("\n--- Spikes ---")
print("Total spikes:", len(spikes))
print(spikes.head())

# --------------------------------------------------
# PHASE 2: EXHAUSTION DETECTION (ELBOW LOGIC)
# --------------------------------------------------
elbows = ElbowTracker()
reversals = elbows.track(df, spikes)

print("\n--- Exhaustion Events ---")
print("Reversal candidates:", len(reversals))
print(reversals.head())

# keep only spikes that exhausted
valid_spike_times = set(reversals["spike_time"])
filtered_spikes = spikes[spikes["time"].isin(valid_spike_times)]

print("\nSpikes after exhaustion filter:", len(filtered_spikes))

# --------------------------------------------------
# PHASE 3: STRUCTURE CONTEXT (only for exhausted spikes)
# --------------------------------------------------
structure = ImpulseStructure()
impulses = structure.classify(df, filtered_spikes)

print("\n--- Structural Context (Filtered) ---")
print("Impulses detected:", len(impulses))
print(impulses.head())

# --------------------------------------------------
# PHASE 4: LINK REVERSALS TO IMPULSES
# --------------------------------------------------
impulses = impulses.merge(
    reversals,
    left_on="time",
    right_on="spike_time",
    how="inner"
)

print("\nImpulses after linking with exhaustion:", len(impulses))

# --------------------------------------------------
# PHASE 5: STRUCTURE SHIFT CONFIRMATION
# --------------------------------------------------
weakness = InternalWeaknessDetector()
shifts = weakness.detect(df, impulses)

print("\n--- Confirmed Structure Shifts ---")
print("Detected shifts:", len(shifts))
print(shifts.head())

# --------------------------------------------------
# PHASE 6: FIBONACCI ENTRY PLANNING
# --------------------------------------------------
fib = FibonacciEntry()

# Pass parameters from config
trades = fib.generate(
    shifts, 
    deeper=config.DEEPER_ENTRY, 
    sl_buffer=config.SL_BUFFER
)

print(f"\n--- Planned Fibonacci Trades (Entry: {'55%' if config.DEEPER_ENTRY else '40%'}) ---")
print("Trades generated:", len(trades))
print(trades.head())

# --------------------------------------------------
# PHASE 7: TRADE SIMULATION
# --------------------------------------------------
sim = TradeSimulator()
results = sim.run(df, trades)

print("\n--- Trade Results ---")
print(results.head())

# --------------------------------------------------
# PHASE 8: PERFORMANCE REPORT
# --------------------------------------------------
report(results)

# --------------------------------------------------
# DEBUG: VIEW EVENT CHAIN
# --------------------------------------------------
if len(impulses):
    debug = impulses[["time","trend"]].merge(
        reversals[["spike_time","reversal_time"]],
        left_on="time",
        right_on="spike_time"
    )

    print("\n--- Event Chain Debug ---")
    print(debug.head())

# --------------------------------------------------
# STATS
# --------------------------------------------------
print_stats(filtered_spikes, shifts)

# --------------------------------------------------
# PHASE 9: VISUALIZE SAMPLE TRADES
# --------------------------------------------------
print("\n--- Generating Charts ---")
viz = TradeVisualizer()

# Grab the first 5 winners
winners = results[results["result"] == "WIN"].head(5)
if not winners.empty:
    print(f"Plotting {len(winners)} WIN trades...")
    for _, trade in winners.iterrows():
        viz.plot_trade(df, trade)
else:
    print("No WIN trades found to plot.")

# Grab the first 5 losers
losses = results[results["result"] == "LOSS"].head(5)
if not losses.empty:
    print(f"Plotting {len(losses)} LOSS trades...")
    for _, trade in losses.iterrows():
        viz.plot_trade(df, trade)
else:
    print("No LOSS trades found to plot.")

print("\nFinished generating charts! Check your project directory for the .png files.")