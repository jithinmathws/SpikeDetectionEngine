from datetime import datetime, timedelta
import pytz
from data_loader import load_m1_data

utc = pytz.UTC

end_time = datetime.now(tz=utc)
start_time = end_time - timedelta(days=1)

df = load_m1_data(
    symbol="XAUUSD",
    start_time=start_time,
    end_time=end_time
)


print(df.head())
print(df.tail())
print("Rows:", len(df))
