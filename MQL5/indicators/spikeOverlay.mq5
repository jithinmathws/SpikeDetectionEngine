#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots   0

// =========================
// INPUTS
// =========================
input string SpikeCSVFile = "spikes_mt5.csv";   // CSV must be in MQL5/Files
input bool   ShowLabels   = true;

// =========================
// INIT
// =========================
int OnInit()
{
   DrawSpikesFromCSV();
   return(INIT_SUCCEEDED);
}

// =========================
// DEINIT
// =========================
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, "SPIKE_");
}

// =========================
// ON CALCULATE (unused)
// =========================
int OnCalculate(
   const int rates_total,
   const int prev_calculated,
   const datetime &time[],
   const double &open[],
   const double &high[],
   const double &low[],
   const double &close[],
   const long &tick_volume[],
   const long &volume[],
   const int &spread[]
)
{
   return(rates_total);
}

// =========================
// CORE LOGIC
// =========================
void DrawSpikesFromCSV()
{
   int handle = FileOpen(SpikeCSVFile, FILE_READ | FILE_CSV);

   if(handle == INVALID_HANDLE)
   {
      Print("❌ Failed to open CSV file: ", SpikeCSVFile);
      return;
   }

   // Skip header line
   FileReadString(handle);

   while(!FileIsEnding(handle))
   {
      string startStr  = FileReadString(handle);
      string endStr    = FileReadString(handle);
      string direction = FileReadString(handle);
      string sizeStr   = FileReadString(handle);
      string elbowType = FileReadString(handle);

      datetime t1 = StringToTime(startStr);
      datetime t2 = StringToTime(endStr);

      if(t1 == 0 || t2 == 0)
         continue;

      bool isBull = (StringCompare(direction, "bull") == 0);

      color spikeColor = isBull ? clrLime : clrRed;
      color fillColor  = isBull
                         ? (color)ColorToARGB(clrLime, 80)
                         : (color)ColorToARGB(clrRed, 80);

      string rectName = "SPIKE_" + startStr;

      // Find bar index
      int shift = iBarShift(_Symbol, PERIOD_M1, t1, true);
      if(shift < 0)
         continue;

      double highPrice = iHigh(_Symbol, PERIOD_M1, shift);
      double lowPrice  = iLow(_Symbol, PERIOD_M1, shift);

      // -------------------------
      // DRAW RECTANGLE
      // -------------------------
      ObjectCreate(0, rectName, OBJ_RECTANGLE, 0, t1, highPrice, t2, lowPrice);
      ObjectSetInteger(0, rectName, OBJPROP_COLOR, fillColor);
      ObjectSetInteger(0, rectName, OBJPROP_BACK, true);
      ObjectSetInteger(0, rectName, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, rectName, OBJPROP_WIDTH, 1);

      // -------------------------
      // OPTIONAL LABEL
      // -------------------------
      if(ShowLabels)
      {
         string labelName = rectName + "_LBL";
         string labelText = direction + " | " + sizeStr + " pips | " + elbowType;

         ObjectCreate(0, labelName, OBJ_TEXT, 0, t1, highPrice);
         ObjectSetString(0, labelName, OBJPROP_TEXT, labelText);
         ObjectSetInteger(0, labelName, OBJPROP_FONTSIZE, 8);
         ObjectSetString(0, labelName, OBJPROP_FONT, "Arial");
         ObjectSetInteger(0, labelName, OBJPROP_COLOR, spikeColor);
      }
   }

   FileClose(handle);
}
