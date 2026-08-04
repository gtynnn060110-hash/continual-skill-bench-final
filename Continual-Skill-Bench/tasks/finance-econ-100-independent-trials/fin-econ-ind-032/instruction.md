## Task 032 [medium] [market] [InvestorBench]
You accumulate a lot of information about Universal Corporation (UVV) in the following sectors so you are especially good at trading them: (1) Tobacco: This is the core sector for Universal Corporation, where they engage in the processing, procurement, and supply of leaf tobaccos. (2) Ingredients: Universal Corporation has expanded into the plant-based ingredients sector for food and beverage companies. Universal Corporation (UVV), a leading global leaf tobacco supplier, exhibited stable financial performance in 2019 with total revenues reaching $2.2 billion. The year 2020 brought challenges from COVID-19 which impacted the global supply chain and reduced demand in certain markets. Despite these hurdles, Universal Corporation maintained operational continuity. At the beginning of Q4 2020, analysts were cautiously optimistic about UVV, seeing potential growth opportunities in UVV's recent ventures into non-tobacco agricultural products.

You will receive daily market observations including:
- Current price of UVV
- Recent news articles related to UVV

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2020-03-12 to 2021-05-06 (291 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_032_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/uvv.json`. Test window: see trial_config in /root/data/uvv.json.
- Do **not** rely on a single `answer` or per-day `{"position": ...}` without `daily_positions`; the verifier will reject missing or incomplete arrays.
- Example:
```json
{
  "daily_positions": [
    {"date": "2020-03-12", "position": 0},
    {"date": "2020-03-13", "position": 1}
  ],
  "strategy": "brief summary optional"
}
```
