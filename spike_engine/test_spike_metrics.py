from datetime import datetime, timedelta
import pytz

from data_loader import load_m1_data
from candle_utils import calculate_candle_metrics
from spike_detector import detect_spikes
from spike_metrics import spikes_to_dataframe

utc = pytz.UTC
end = datetime.now(tz=utc)
start = end - timedelta(days=5)

df = load_m1_data("XAUUSD", start, end)
df = calculate_candle_metrics(df)

spikes = detect_spikes(df, symbol="XAUUSD", pip_size=0.01)

report = spikes_to_dataframe(spikes, symbol="XAUUSD")

print(report.head())
print("Total spikes:", len(report))
