# Hotel Bar Inventory Forecasting & Par Level Recommendation System

Predicts 30-day consumption for 96 Bar x Brand product-lines and recommends a periodic-review
inventory policy (Safety Stock, Reorder Point, Par Level) with a lead-time-aware simulation.

## Quick start

```powershell
# PowerShell, Windows
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter notebook notebooks\inventory_forecasting_solution.ipynb
```

Run the notebook **in order** (`Kernel -> Restart & Run All`). All cells are
directory-independent: they locate the project root by walking up from the working
directory until `data\raw\bar_inventory_data.csv` is found, so it does not matter whether
the kernel is started from the project root or from `notebooks\`.

## Pipeline

raw transactions -> conservation audit -> prorated daily Bar x Brand consumption ->
intermittent-demand classification -> baseline + Croston/SBA + moving-average forecasts ->
rolling-origin backtest (4 x 30-day windows) -> per-series model selection -> 30-day forecast ->
forecast sanity floor for zero-forecast series -> forecast-error uncertainty -> Safety Stock ->
ROP -> Par Level -> order quantity -> lead-time-aware inventory simulation -> sensitivity matrix.

## Results (single sentence)

At a 95% service target, 7-day lead time and 7-day review cycle the corrected policy achieves a
**mean simulated service of 92.5%** (median 98.5%) with an average of **1.4 stockout days** and
**2.0 orders per month** per product-line; 34 of 96 lines fall below the target and are listed in
`data/processed/high_risk_series.csv`.

## Key outputs

`data/processed/` contains `daily_bar_consumption.csv` (34,294 x 13),
`intermittent_demand_analysis.csv`, `forecast_summary.csv`, `inventory_planning.csv`,
`inventory_simulation.csv`, `zero_forecast_diagnostics.csv`,
`inventory_policy_sensitivity.csv`, `high_risk_series.csv`, and others.
`report/` holds the business report and management charts.

## Environment

Python 3.10+ recommended. See `requirements.txt`.