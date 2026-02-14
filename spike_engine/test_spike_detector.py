from datetime import datetime, timedelta
import pytz

from data_loader import load_m1_data
from candle_utils import calculate_candle_metrics
from spike_detector import detect_spikes

utc = pytz.UTC
end = datetime.now(tz=utc)
start = end - timedelta(days=3)

df = load_m1_data("XAUUSD", start, end)
df = calculate_candle_metrics(df)

spikes = detect_spikes(df, symbol="XAUUSD", pip_size=0.01)

print("Spikes found:", len(spikes))

for s in spikes[:3]:
    print(
        s["start_time"],
        s["direction"],
        s["spike_pips"],
        "pips",
        "| candles:",
        s["candles"],
        "| elbows:",
        s["elbow_type"]
    )
