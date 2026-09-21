# Video Walkthrough Outline (3-5 minutes)

Target: management + technical audience. Backing figures: `data/processed/*.csv`, charts in `report/`.

## 1. Business problem (0:00 - 0:45)
- 6 hotel bars, 16 brands, 96 Bar x Brand product-lines, 6,575 transactions, ~365 days.
- Bar managers run out of stock and over-order in parallel; no standard par level.
- Story: "On some lines we saw a pattern you'd never want in a bar: `Opening 398 ml, Purchase 0, Consumed 398 ml, Closing 0 ml` -- sold the last bottle every single day."
- Question we answer: stock how much (par level), when to reorder (ROP), and how safe that policy really is.

## 2. Data & modeling (0:45 - 1:45)
- Conservation audit + proration of transactions to daily Bar x Brand consumption (34,294 daily rows).
- Demand is highly intermittent: average active-day share 9-24%; most lines are Occasional/Low.
- Six candidate methods (Mean, MA-7/14/30, Croston, SBA) backtested with 4 rolling 30-day windows.
- Model selection: MA-14, MA-30, Intermittent Mean, SBA dominate; Croston was never best.
- Honest caveat: WAPE ~2 -- flat forecasts cannot time zero days; we forecast the *level*, not the timing.

## 3. Inventory logic (1:45 - 3:00)
- Policy = periodic review (every 7 days), order up to Par, lead time 7 days.
- Safety Stock from forecast-error sigma (not average error): `SS = z * sigma_error * sqrt(LT)`.
- `ROP = lead_time_demand + SS`, `Par = (LT + review_cycle) * daily_forecast + SS`.
- Zero-forecast trap: 3 lines (incl. Anderson's Budweiser) had MA-7 = 0 ml -> conservatively floored to an active-day-level estimate; flagged, not silently changed.
- Simulation is lead-time aware: orders arrive 7 days later, inventory position = on-hand + on-order, 500 scenarios per line, same random scenarios across policies.

## 4. Business impact (3:00 - 4:00)
- Recommended policy (95% target): mean simulated service 92.5%, median 98.5%.
- Average stockout days 1.4 / month; lost demand ~118 ml per line; 2 orders/month.
- 25 of 96 lines below 90%, 34 below 95% (top offenders: Anderson's Miller 53.7%, Johnson's Miller 56.7%, Anderson's Budweiser 64.0%, Grey Goose 64.6%).
- Overstock side: Taylor's Barefoot/Heineken/Coors carry 7-10 litres of on-hand stock at 100% service but turnover below 0.4 -- money sitting on shelves; can trim.
- Trade-off: longer lead time buys service (LT-7 ~92.5% vs LT-2 ~87.6% at 95% target) but raises average inventory ~10% and cuts turnover 1.45 -> 1.05.

## 5. Production considerations & next steps (4:00 - 4:30+)
- Recompute par levels monthly from trailing demand + forecast-error statistics.
- Track realized stockouts versus censored demand (closing = 0 hides true demand).
- Watch slow movers: economic-hold-to-maturity / scrap vs. restock.
- Do NOT chase a 99% target globally (26 lines already at 100% service but hold excess stock); rebalance toward the 90-95% band.