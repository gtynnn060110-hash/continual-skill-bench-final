## Task 47 [L4] [putnam_axiom] [algebra]

Find the smallest constant $C$ such that for every real polynomial $P(x)$ of degree 3 that has a root in the interval $[0,1]$, \[ \int_0^1 \left| P(x) \right|\,dx \leq C \max_{x \in [0,1]} \left| P(x) \right|. \]

Output requirements:
- Write your answer to `/app/task_047_output.json`
- JSON object with at minimum:
  - `answer`: a single numeric value (number or numeric string). Do NOT wrap in nested objects.
- Optional fields: `reasoning`, `steps`. The `answer` field must directly answer the question.
