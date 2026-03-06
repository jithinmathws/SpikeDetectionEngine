from dotenv import load_dotenv
import os

load_dotenv()

class config:
    # MetaTrader 5 Settings
    MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")
    MT5_ACCOUNT = int(os.getenv("MT5_ACCOUNT", "12345678"))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "your_password")
    MT5_SERVER = os.getenv("MT5_SERVER", "DemoServer")

    # Strategy Parameters
    SYMBOL = os.getenv("SYMBOL", "XAUUSD")

    # Trading Settings
    START_DATE = "2025-01-01"
    END_DATE   = "2025-05-31"

    PIP_SIZE = 0.01
    SPIKE_PIPS = 800

    MIN_WINDOW = 7
    MAX_WINDOW = 25

    # Strategy Toggles
    LOOKAHEAD = 60
    MIN_ELBOW_BODY = 0.25

    # Fibonacci Settings
    # Use 0.40 for more fills, 0.55 for better risk/reward
    DEEPER_ENTRY = False  # Set to True for 55%, False for 40%

    # Gold SL Buffer (Price points, e.g., 1.00 = $1.00 move on Gold)
    SL_BUFFER = 0.50