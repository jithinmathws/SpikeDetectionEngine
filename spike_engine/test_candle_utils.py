from datetime import datetime, timedelta
import pytz

from data_loader import load_m1_data
from candle_utils import calculate_candle_metrics

utc = pytz.UTC
UTC_PLUS_8 = pytz.timezone("Asia/Singapore")  # UTC+8 standard

end = datetime.now(tz=UTC_PLUS_8)
start = end - timedelta(hours=3)

df = load_m1_data("XAUUSD", start, end)
df = calculate_candle_metrics(df)

print(df[[
    "time",
    "open",
    "high",
    "low",
    "close",
    "body",
    "range",
    "direction"
]].head(10))

print(df["direction"].value_counts())
