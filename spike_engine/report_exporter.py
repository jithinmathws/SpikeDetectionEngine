# report_exporter.py
import os
from datetime import datetime
import pandas as pd

def export_spike_report(
    df: pd.DataFrame,
    symbol: str,
    output_dir: str = "reports"
):
    """
    Export spike report to CSV and Excel.

    Parameters
    ----------
    df : pd.DataFrame
        Output from spike_metrics.spikes_to_dataframe()
    symbol : str
        Trading symbol (e.g. 'XAUUSD', 'USDJPY')
    output_dir : str
        Directory to save reports
    """

    if df.empty:
        print(f"[INFO] No spikes to export for {symbol}")
        return

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{symbol}_M1_Spike_Report_{timestamp}"

    csv_path = os.path.join(output_dir, f"{base_name}.csv")
    xlsx_path = os.path.join(output_dir, f"{base_name}.xlsx")

    # Export CSV
    df.to_csv(csv_path, index=False)

    # Export Excel
    # Export Excel
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:

        df_excel = df.copy()

        # Strip timezone info for Excel compatibility
        for col in df_excel.columns:
            if pd.api.types.is_datetime64tz_dtype(df_excel[col]):
                df_excel[col] = df_excel[col].dt.tz_localize(None)

        df_excel.to_excel(writer, index=False, sheet_name="Spikes")

        worksheet = writer.sheets["Spikes"]

        # Auto-adjust column widths
        for col_idx, col in enumerate(df_excel.columns, start=1):
            max_length = max(
                df_excel[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet.column_dimensions[
                chr(64 + col_idx)
            ].width = max_length + 2

    print(f"[OK] Exported CSV  → {csv_path}")
    print(f"[OK] Exported Excel → {xlsx_path}")
