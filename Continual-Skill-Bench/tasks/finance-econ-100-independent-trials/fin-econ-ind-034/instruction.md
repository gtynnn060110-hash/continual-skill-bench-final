## Task 034 [medium] [market] [InvestorBench]
You accumulate a lot of information about Johnson & Johnson (JNJ) in the following sectors so you are especially good at trading them: (1) Pharmaceuticals Sector: This is the largest segment of JNJ, involving research, development, and sale of pharmaceutical products across immunology, oncology, neurology, and infectious diseases. (2) Medical Devices Sector: JNJ is a significant player in medical devices, providing products used in orthopedics, surgery, cardiovascular care, and diabetes care. (3) Consumer Health Sector: This sector includes a broad array of OTC products, skin care products, and baby care products. Johnson & Johnson demonstrated robust financial performance in 2019, generating revenues of $82.1 billion. In 2020, JNJ faced challenges due to COVID-19, impacting its medical devices segment, but pharmaceuticals and consumer health divisions saw increased demand. By end of Q3 2020, JNJ's stock had recovered, driven by positive news regarding its COVID-19 vaccine candidate. At the beginning of Q4 2020, analysts were optimistic about JNJ, particularly about the potential approval and distribution of its COVID-19 vaccine.

You will receive daily market observations including:
- Current price of JNJ
- Recent news articles related to JNJ

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2020-03-12 to 2021-05-06 (291 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_034_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/jnj.json`. Test window: see trial_config in /root/data/jnj.json.
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
