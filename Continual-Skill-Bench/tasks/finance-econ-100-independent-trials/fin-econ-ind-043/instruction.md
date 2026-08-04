## Task 043 [medium] [market] [InvestorBench]
You accumulate a lot of information of MSFT on the following sectors so you are especially good at trading them: (1) Technology Sector: This is the primary sector for Microsoft, encompassing software development, cloud computing services (like Azure), and various technology solutions. (2) Consumer Discretionary Sector: Microsoft also plays a role through its gaming and entertainment divisions, including Xbox gaming consoles. (3) Communication Services Sector: Microsoft is involved through LinkedIn and communication tools like Microsoft Teams. From 2019 to end of Q3 2020, Microsoft demonstrated robust financial performance and positive stock trends. In 2019, revenue increased to $125.8 billion, a 14% rise, driven by cloud, Office, and LinkedIn segments. In 2020, despite COVID-19, Microsoft's revenue grew 13% in Q3, bolstered by surging demand for cloud services and Teams. The stock price rose from about $100 in early 2019 to nearly $210 by end of September 2020. At the start of Q4 2020, analysts were optimistic about Microsoft's continued growth driven by Azure and sustained demand for remote work tools.

You will receive daily market observations including:
- Current price of MSFT
- Recent news articles related to MSFT

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2020-03-12 to 2021-05-06 (291 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_043_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/msft.json`. Test window: see trial_config in /root/data/msft.json.
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
