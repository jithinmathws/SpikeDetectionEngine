from datetime import datetime, timedelta
import pytz

from data_loader import load_m1_data
from candle_utils import calculate_candle_metrics
from spike_detector import detect_spikes
from spike_metrics import spikes_to_dataframe
from report_exporter import export_spike_report
from report_exporter_mt5 import export_spikes_for_mt5
from spike_assessment import assess_h4_filter_effectiveness, generate_assessment_verdict

utc = pytz.UTC
end = datetime.now(tz=utc)
start = end - timedelta(days=7)

symbol = "XAUUSD"
pip_size = 0.01

# Load data
df = load_m1_data(symbol, start, end)

# Candle metrics
df = calculate_candle_metrics(df)

# Detect spikes
spikes = detect_spikes(df, symbol=symbol, pip_size=pip_size)

# Convert to report
report_df = spikes_to_dataframe(spikes, symbol=symbol)

# Export
export_spike_report(report_df, symbol=symbol)

export_spikes_for_mt5(
    df=report_df,
    symbol="XAUUSD"
)

summary = assess_h4_filter_effectiveness(report_df)

print("\n=== H4 CONTEXT COMPARISON ===")
print(summary)

print("\n=== ASSESSMENT VERDICT ===")
print(generate_assessment_verdict(summary))