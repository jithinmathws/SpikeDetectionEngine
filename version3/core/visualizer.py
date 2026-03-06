import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np

class TradeVisualizer:

    def plot_trade(self, df, trade, window_bars=200):
        """
        Plots a specific trade along with its spike, exhaustion, and fib levels.
        """
        # 1. Force signal_time to be a pandas Timestamp
        signal_time = pd.to_datetime(trade["signal_time"])
        
        # FIXED: Get the absolute POSITIONAL index (0 to len-1) instead of the label index
        pos_matches = np.where(df["time"] == signal_time)[0]
        if len(pos_matches) == 0:
            print(f"Error: Could not find signal time {signal_time} in DataFrame.")
            return
        idx = pos_matches[0]

        # Calculate plotting boundaries using integer positions
        start_idx = max(0, idx - window_bars // 2)
        end_idx = min(len(df), idx + window_bars)
        
        plot_df = df.iloc[start_idx:end_idx].copy()
        plot_df = plot_df.reset_index(drop=True) 

        fig, ax = plt.subplots(figsize=(15, 8))

        # 2. Draw Candlesticks
        for i, row in plot_df.iterrows():
            color = '#26a69a' if row['close'] >= row['open'] else '#ef5350' # TradingView colors
            
            # Wick
            ax.vlines(i, row['low'], row['high'], color=color, linewidth=1.5)
            
            # Body
            height = abs(row['close'] - row['open'])
            bottom = min(row['open'], row['close'])
            # Body width is 0.8 of the bar space for a thicker look
            rect = patches.Rectangle((i - 0.4, bottom), 0.8, height, color=color, alpha=0.9)
            ax.add_patch(rect)

        # 3. Overlay Fibonacci Levels & Trade Entry/SL/TP
        ax.axhline(trade['fib40'], color='gray', linestyle='--', alpha=0.5, label='Fib 40%')
        ax.axhline(trade['fib55'], color='gray', linestyle='-', alpha=0.5, label='Fib 55%')
        
        ax.axhline(trade['entry'], color='blue', linestyle='-', linewidth=2, label=f"Entry ({trade['direction']})")
        ax.axhline(trade['sl'], color='red', linestyle='--', linewidth=1.5, label="Stop Loss")
        ax.axhline(trade['tp'], color='green', linestyle='--', linewidth=1.5, label="Take Profit")

        # 4. Annotate Signal Time
        signal_plot_idx = idx - start_idx
        
        ax.annotate('Signal/Shift', xy=(signal_plot_idx, trade['entry']), 
                    xytext=(signal_plot_idx, trade['entry'] + 1),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    fontsize=10)

        # 5. Highlight the Result
        result_color = 'forestgreen' if trade['result'] == 'WIN' else 'firebrick' if trade['result'] == 'LOSS' else 'goldenrod'
        safe_time_str = signal_time.strftime('%Y%m%d_%H%M')
        
        plt.title(f"Trade Result: {trade['result']} | {trade['direction']} | {signal_time}", 
                  fontsize=14, fontweight='bold', color=result_color)

        ax.set_ylabel("Price (XAUUSD)")
        ax.set_xlabel("Bars (Minutes)")
        
        # FIXED: Force the x-axis to scale properly to the number of bars we drew
        ax.set_xlim(-1, len(plot_df) + 1)
        
        ax.legend(loc='best')
        ax.grid(True, alpha=0.2)
        
        plt.tight_layout()
        filename = f"trade_debug_{safe_time_str}.png"
        plt.savefig(filename, dpi=150) # Added higher resolution
        print(f"Saved visualization: {filename}")
        plt.close()