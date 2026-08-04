# Science Core Agent Skills

## 1. science-common-reasoning
- Description: General scientific problem framing, assumption tracking, unit checks, and output discipline.
- Typical tasks:
  - Restate quantities, constraints, and requested output before solving.
  - Decide whether a task is numeric, exact-answer QA, data analysis, or open-ended workflow design.
  - Write a valid JSON result to the exact `/app/task_XXX_output.json` path.

## 2. math-physics-solving
- Description: Quantitative science and physics solving with equations, units, and numerical verification.
- Typical tasks:
  - Extract variables and constants from a physics prompt.
  - Choose and apply governing equations.
  - Use `sympy`, `scipy`, or a short script for algebra and numerical checks.

## 3. bio-lab-qa
- Description: Biology, biochemistry, protocol, sequence, figure, table, and literature QA.
- Typical tasks:
  - Match a candidate answer exactly to a LAB-Bench option.
  - Read protocol, figure, table, or literature evidence from task data.
  - Avoid synonym drift in exact-match answers.

## 4. scientific-data-analysis
- Description: Reproducible scientific data workflows for datasets, models, visualizations, and generated artifacts.
- Typical tasks:
  - Inspect folder trees, previews, schemas, and source metadata.
  - Design commands, model choices, validation checks, and output paths.
  - Produce analysis summaries with assumptions and limitations.

## 5. scientific-source-checking
- Description: Source-aware scientific evidence use across benchmark pages, project docs, and dataset records.
- Typical tasks:
  - Read task payloads before making assumptions.
  - Distinguish source facts from calculations.
  - Record unavailable upstream files and fallback reasoning honestly.
