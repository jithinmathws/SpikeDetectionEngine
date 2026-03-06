import os
import glob
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import MetaTrader5 as mt5

# Import your core strategy modules
from core.data_loader import fetch_live_data 
from core.spike_detector import SpikeDetector
from core.elbow_tracker import ElbowTracker
from core.impulse_structure import ImpulseStructure
from core.internal_weakness import InternalWeaknessDetector
from core.fib_entry import FibonacciEntry
from core.visualizer import TradeVisualizer
from settings.config import config

# --------------------------------------------------
# 0. LOGGING SETUP
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# 1. UTILITY FUNCTIONS
# --------------------------------------------------

def cleanup_old_charts(directory=".", max_age_hours=48):
    """Deletes .png chart files older than max_age_hours to save disk space."""
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)
    
    search_pattern = os.path.join(directory, "trade_debug_*.png")
    chart_files = glob.glob(search_pattern)
    
    deleted_count = 0
    for file_path in chart_files:
        try:
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < cutoff_time:
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            logger.error(f"Could not delete {file_path}: {e}")
            
    if deleted_count > 0:
        logger.info(f"Cleanup: Deleted {deleted_count} old chart(s).")

def get_filling_mode(symbol):
    """Automatically detects the correct filling mode for your broker."""
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return mt5.ORDER_FILLING_IOC
    
    filling_mode = symbol_info.filling_mode
    if filling_mode & mt5.SYMBOL_FILLING_FOK:
        return mt5.ORDER_FILLING_FOK
    elif filling_mode & mt5.SYMBOL_FILLING_IOC:
        return mt5.ORDER_FILLING_IOC
    else:
        return mt5.ORDER_FILLING_RETURN

# --------------------------------------------------
# 2. ORDER EXECUTION FUNCTION
# --------------------------------------------------

def send_order_to_broker(trade, symbol="XAUUSD", lot_size=0.01):
    logger.info(f"PREPARING ORDER: {trade['direction']} LIMIT @ {trade['entry']:.2f}")
    
    order_type = mt5.ORDER_TYPE_BUY_LIMIT if trade['direction'] == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT
    filling = get_filling_mode(symbol)

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": round(float(trade['entry']), 2),
        "sl": round(float(trade['sl']), 2),
        "tp": round(float(trade['tp']), 2),
        "deviation": 20,
        "magic": 777111,
        "comment": "Spike_Fib_Strategy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Order failed: {result.comment} (Code: {result.retcode})")
    else:
        logger.info(f"SUCCESS! {trade['direction']} Limit placed at {trade['entry']:.2f}")

# --------------------------------------------------
# 3. MAIN LIVE LOOP
# --------------------------------------------------

def run_live_bot():
    load_dotenv()
    
    MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")
    
    try:
        account = int(os.getenv("MT5_ACCOUNT"))
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")
    except (TypeError, ValueError):
        logger.error("Check .env for MT5_ACCOUNT (must be numeric).")
        return

    # Initialize connection
    if not mt5.initialize(path=MT5_PATH, login=account, password=password, server=server, timeout=15000):
        logger.error(f"MT5 Connection Failed: {mt5.last_error()}")
        return

    # Verify Session
    acc_info = mt5.account_info()
    if acc_info is None:
        logger.error("Login failed. Verify server name in .env")
        mt5.shutdown()
        return
        
    logger.info(f"SESSION VERIFIED: {server} | Account: {account} | Balance: {acc_info.balance}")
    logger.info("Strategy: Spike & Fib Bot is LIVE.")

    # Initialize Strategy Components
    detector = SpikeDetector(config.PIP_SIZE, config.SPIKE_PIPS, config.MIN_WINDOW, config.MAX_WINDOW)
    elbows = ElbowTracker()
    structure = ImpulseStructure()
    weakness = InternalWeaknessDetector()
    fib = FibonacciEntry()
    viz = TradeVisualizer() 

    last_processed_time = None

    try:
        while True:
            now = datetime.now()
            
            if now.second == 2:
                if now.minute == 0:
                    cleanup_old_charts(max_age_hours=48)

                logger.info(f"Scanning XAUUSD M1...")
                df = fetch_live_data(symbol="XAUUSD", timeframe=mt5.TIMEFRAME_M1, bars=300)
                
                if df is not None and not df.empty:
                    spikes = detector.detect(df)
                    if not spikes.empty:
                        logger.info(f"Spike detected at {spikes.iloc[-1]['time']}")
                        reversals = elbows.track(df, spikes)
                        if not reversals.empty:
                            impulses = structure.classify(df, spikes[spikes["time"].isin(reversals["spike_time"])])
                            if not impulses.empty:
                                shifts = weakness.detect(df, impulses.merge(reversals, left_on="time", right_on="spike_time"))
                                
                                if not shifts.empty:
                                    trades = fib.generate(shifts, deeper=config.DEEPER_ENTRY, sl_buffer=config.SL_BUFFER)
                                    
                                    if not trades.empty:
                                        latest = trades.iloc[-1].copy()
                                        if latest['time'] == df.iloc[-2]['time'] and latest['time'] != last_processed_time:
                                            send_order_to_broker(latest)
                                            last_processed_time = latest['time']
                                            viz.plot_trade(df, latest)
                
                time.sleep(55) 
            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    run_live_bot()