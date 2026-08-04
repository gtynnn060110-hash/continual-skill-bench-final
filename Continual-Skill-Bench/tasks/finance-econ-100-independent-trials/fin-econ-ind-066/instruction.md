## Task 066 [hard] [market] [InvestorBench]
You are an investment expert of NFLX. You accumulate a lot of information of NFLX on the following sectors so you are especially good at trading them: (1) Communication Services, which includes companies that facilitate communication and offer related content and information through various media. (2) Entertainment, which includes companies involved in providing entertainment content and services, such as movies, TV shows, and streaming services. (3) Media, which encompasses a broader range of services including content production and distribution. (4) Internet Content & Information, which covers companies that produce content to be distributed through online platforms. From 2019 to end of Q3 2020, Netflix showcased notable financial growth, largely influenced by COVID-19, which spiked demand for streaming services. Throughout 2019, revenue growth was robust driven by increasing global streaming memberships. The year 2020 saw further acceleration in subscriber numbers, particularly in the first half. Stock performance remained strong with resilience during the March 2020 market downturn. As of end of Q3 2020, analysts anticipated a mixed picture for Netflix going forward, with continued revenue and earnings growth but at a decelerating pace.

You will receive daily market observations including:
- Current price of NFLX
- Recent news articles related to NFLX

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2020-03-12 to 2021-05-06 (234 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_066_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/nflx.json`. Test window: see trial_config in /root/data/nflx.json.
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
