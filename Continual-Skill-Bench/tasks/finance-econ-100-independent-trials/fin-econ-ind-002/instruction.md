## Task 002 [easy] [market] [InvestorBench]
You accumulate a lot of information about Honeywell International Inc. (HON) in the following sectors so you are especially good at trading them: (1) Industrial Sector: Honeywell provides a wide range of industrial products, including automation and control systems for manufacturing processes. (2) Aerospace Sector: A significant portion of Honeywell's business is in the aerospace industry, where it supplies engines, avionics, and other technologies for aircraft. (3) Building Technologies Sector: Honeywell also serves the building and construction market with technologies for HVAC and security systems. (4) Performance Materials and Technologies Sector: This sector includes the production of specialty chemicals, materials, and technologies used in a wide range of products and processes. (5) Safety and Productivity Solutions: Honeywell provides products that enhance safety and productivity for workers and workplaces. Honeywell International Inc. (HON) experienced a strong financial performance in 2019, reporting revenue of approximately $36.7 billion. The onset of the COVID-19 pandemic in early 2020 impacted various segments of Honeywell, particularly aerospace, due to a sharp decline in global travel. Despite these challenges, Honeywell's performance in health, safety, and automation products remained strong. At the beginning of Q4 2020, analysts were cautiously optimistic about Honeywell for the remainder of the year and into 2021.

You will receive daily market observations including:
- Current price of HON
- Recent news articles related to HON

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2020-03-12 to 2021-05-06 (291 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_002_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/hon.json`. Test window: 2020-03-12 to 2021-05-06 (see trial_config in /root/data/hon.json).
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
