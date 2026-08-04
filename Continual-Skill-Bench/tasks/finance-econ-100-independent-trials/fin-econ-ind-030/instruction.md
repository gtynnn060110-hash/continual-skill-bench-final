## Task 030 [medium] [market] [InvestorBench]
You are an experienced trading manager in cryptocurrency trading at a mainstream investment firm. You accumulate a lot of information about Bitcoin USD (BTC-USD) in the following sectors, so you are especially good at trading them: 1) Trading: This involves the buying and selling of Bitcoin and other cryptocurrencies on various exchanges and platforms. It's a highly active area with significant price volatility. 2) Investment: Bitcoin is often treated as a digital asset by investors looking for portfolio diversification. It's increasingly included in investment strategies alongside traditional assets. 3) Payment Solutions: Bitcoin serves as a digital currency, facilitating transactions without the need for traditional banking systems. It's used in cross-border transactions due to its decentralized nature. 4) Blockchain Technology: The underlying technology of Bitcoin is blockchain, a decentralized ledger that records all transactions securely and transparently. This technology is pivotal in many fintech innovations beyond just cryptocurrencies. From December 2022 to April 2023, Bitcoin (BTC-USD) experienced significant volatility in its price. In December 2022, Bitcoin had been trading around $16,800 but saw a gradual decline through the month, touching lows near $16,500. The cryptocurrency began to recover in January 2023, surpassing $21,000 by the end of the month, spurred by renewed investor interest and a favorable macroeconomic outlook. February saw a slight retreat, with prices oscillating around the $20,000 mark. March marked a more robust recovery, with Bitcoin breaking past $25,000, benefiting from global economic cues and inflation data. April continued the upward trend, with Bitcoin reaching highs around $27,000. Overall, the period was marked by recovery from earlier lows, with Bitcoin showing resilience in the face of ongoing economic uncertainties. As of April 2023, analysts anticipated a cautiously optimistic outlook for Bitcoin for the remainder of the year. They forecasted that Bitcoin's price could experience continued volatility but remain on an upward trajectory if the macroeconomic environment stabilize. However, they also warned of potential downward pressures from regulatory crackdowns and technological vulnerabilities.

You will receive daily market observations including:
- Current price of BTC
- Recent news articles related to BTC

For each trading day, decide: BUY (position=1), HOLD (position=0), or SELL (position=-1).
For each trading day, record your decision in the submission file as part of `daily_positions` (see below): position `1` = BUY, `0` = HOLD, `-1` = SELL; optional `rationale` per day is allowed inside each array element but grading uses `date` + `position` only.

Data available: 2022-11-29 to 2023-12-19 (386 days)
Evaluation metrics: Cumulative Return (CR), Sharpe Ratio (SR), Annualized Volatility (AV), Maximum Drawdown (MDD).
Higher CR and SR are better; lower AV and MDD are better.

Submission (programmatic grading):
- Write your answer to `/app/task_030_output.json`
- **Required for automated grading**: include top-level `"daily_positions"` — an array with **one entry per actionable trading day** in the test window (every calendar date from the first test date through the **penultimate** test date; do **not** include the last date). Each entry must be:
  - `"date"`: `"YYYY-MM-DD"`
  - `"position"`: integer `-1` (SELL), `0` (HOLD), or `1` (BUY)
- You may add narrative fields (`strategy`, `rationale`, `sector_analysis`, etc.), but scoring uses **`daily_positions` only** against prices in `/root/data/btc.json`. Test window: 2022-11-29 to 2023-12-19 (BTC evaluation window).
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
