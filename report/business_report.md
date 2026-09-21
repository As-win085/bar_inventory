# Hotel Bar Inventory: Forecast-based Par Levels -- Business Report

**Scope: 6 bars, 16 brands, 96 Bar x Brand product-lines, 6,575 transactions, ~365 days.**
**Recommended policy: 7-day review, 7-day lead time, 95% service target.**

---

## 1. Business problem
Bars keep too little of fast-moving stock (stockouts sell out every day) and too much of slow
movers (shelf stock that never turns). Inventory data is recorded per transaction, not per day,
so daily demand must be reconstructed before any par level can be set.

| Demo of the problem | Occurrence |
|---|---|
| `Opening 398ml / Purchase 0 / Consumed 398ml / Closing 0` | 264 records 4.0% are stockout-censored; 999 records end at zero stock |

## 2. Assumptions
- Transactions are prorated evenly to the day when a consumption line has no matching purchase line;
  purchases are assigned to their entry date; consumed quantity is capped at opening+purchase.
- Demand scale is millilitres; 1 bottle ~ 750 ml for display (preferred-order size per line can be changed).
- Stockouts are lost sales (no backorder). Lead time is constant at 7 days.
- Forecast uncertainty is estimated from rolling-origin forecast errors per line.

## 3. Models and trade-offs
Six methods were compared on 4 rolling 30-day windows: Mean, MA-7/MA-14/MA-30, Croston, SBA.
Selection (96 lines): MA-7 34, Intermittent Mean 20, MA-30 19, MA-14 13, SBA 7, Mean 3. Croston
was never recommended. Rolling mean WAPE is ~2 across models: demand is lumpy, so timing cannot be
predicted; the forecast captures each line's **level**, and safety stock absorbs the timing risk.
Three lines (Anderson's Budweiser, Absolut; Smith's Yellow Tail) produced an MA-7 of 0 ml over
trailing zero-demand days; they were conservatively floored to an active-day-level estimate and
flagged (`forecast_adjustment_flag`), not silently changed.

## 4. Performance and business answer
**Recalculate Par = (LT + review) x daily forecast + z x sigma_error x sqrt(LT); ROP = LT x forecast + SS.**

| KPI (Policy B, 500 scenarios/line) | Value |
|---|---|
| Mean simulated service | 92.5% (median 98.5%) |
| Lines below 90% / 95% / 99% | 25 / 34 / 51 of 96 |
| Avg stockout days / month | 1.4 |
| Avg lost demand / month | ~118 ml per line |
| Avg orders / month | 2.0 |
| Mean on-hand inventory | ~2,247 ml per line; turnover 1.05 |

Highest-risk lines need intervention: **Anderson's Miller 53.7%, Johnson's Miller 56.7%,
Anderson's Budweiser 64.0%, Grey Goose 64.6%** (all below 75% service; add stock/raise target).
Inventory-heavy lines carry 7-10 L at 100% service but turnover < 0.4 (Taylor's Barefoot, Heineken,
Coors; Anderson's Captain Morgan) -- over-stocked; trim toward 90-95% target.

**Sensitivity (service by lead time x target):**

| Lead time | 90% target | 95% target | 99% target |
|---|---|---|---|
| 2 days | 86.6% | 87.6% | 89.3% |
| 3 days | 88.1% | 89.1% | 90.8% |
| 5 days | 90.2% | 91.2% | 92.6% |
| 7 days | 91.6% | 92.5% | 93.7% |

A longer lead time raises service but inflates par level and cuts turnover (1.45 -> 1.05 at LT7).
We recommend the **7-day review / 7-day LT / 95% target** policy as the operational baseline, then
per-line rebalancing using `high_risk_series.csv` and `inventory_heavy_series.csv`.

## 5. Production considerations and future work
- Re-run monthly; recompute SS from rolling forecast-error sigma, not the mean error.
- Replace censored days empirically (closing = 0 understates demand) once true sales data is joined.
- Do not apply one target everywhere; set 95% band for fast movers, lower for slow movers.
- Future: multi-location pooling and seasonality windows would help a small fraction of lines;
  do not add exogenous forecasting for the majority of near-constant-mix lines.