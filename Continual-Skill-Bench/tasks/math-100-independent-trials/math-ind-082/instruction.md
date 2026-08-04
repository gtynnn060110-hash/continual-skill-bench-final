## Task 82 [L6] [realmath] [algebra]

Let \(\theta \in \operatorname{Aut}(F_q)\), \(\lambda \in F_q^\ast\), and let \(C\) be a \(\theta\)-cyclic code of length \(n\) over \(F_q\) (with \(C \neq \{0\}\) and \(C \neq F_q^n\)). Suppose its generator skew polynomial is
\[
g(x) = a_0 + a_1 x + \cdots + a_{n-k} x^{n-k},
\]
and that it satisfies
\[
x^n - \lambda = h(x) g(x).
\]
Define
\[
\hbar(x) = \lambda^{-1} h(x) \theta^{-k}(\lambda) = b_0 + b_1 x + \cdots + b_k x^k,
\]
and its \(\theta\)-reciprocal
\[
\hbar^{\ast}(x) = b_k + \theta(b_{k-1}) x + \cdots + \theta^k(b_0) x^k.
\]
If \(C^\perp\) denotes the dual code of \(C\), what is the generator skew polynomial \(g^\perp(x)\) of \(C^\perp\) in terms of \(\hbar^{\ast}(x)\) and \(b_0\)?

Output requirements:
- Write your answer to `/app/task_082_output.json`
- JSON object with at minimum:
  - `answer`: your final answer (plain string; include key math expressions)
  - optional: `reasoning`, `steps`, `calculations`
- This task is graded by an LLM judge against a reference answer (score 0 or 1).
- You must write the output file; chat-only responses receive no score.
