# Continual Skill Bench

Continual Skill Bench is a benchmark for evaluating whether language-model agents can build, retain, and reuse skills across a sequence of related subtasks.

Most agent benchmarks evaluate each task independently. Continual Skill Bench instead organizes each domain as a 100-subtask sequence. Earlier subtasks are intended to expose recurring operations, formats, formulas, domain constraints, or verification patterns that can help solve later subtasks. This makes it possible to compare independent execution against sequential execution with an evolving skill library or other memory mechanism.

## What This Benchmark Tests

Continual Skill Bench focuses on three questions:

1. Do agents improve when they solve related subtasks sequentially rather than independently?
2. Are the gains caused by reusable skills, by short-term context adaptation, or by superficial format alignment?
3. What kinds of skills do agents create, and how useful are those skills for later tasks?

Each domain contains a mixture of task formats:

- `exact_match`: strict label or string match.
- `numeric`: numerical answer with tolerance or normalization.
- `f1`: token-level overlap for extraction-style answers.
- `programmatic`: task-specific executable checks.
- `rubric_judge`: LLM-judge evaluation using task rubrics.

## Benchmark Domains

The main benchmark domains are under `tasks/`.

| Domain | Path | Subtasks | Evaluation mix |
| --- | --- | ---: | --- |
| Finance/Economics | `tasks/finance-econ-100` | 100 | 11 exact, 12 numeric, 13 F1, 13 programmatic, 51 rubric |
| Healthcare | `tasks/healthcare-100` | 100 | 28 exact, 4 programmatic, 68 rubric |
| Law | `tasks/law-100` | 100 | 40 exact, 10 programmatic, 50 rubric |
| Mathematics | `tasks/math-100` | 100 | 39 exact, 24 numeric, 12 programmatic, 25 rubric |
| Office | `tasks/office-100` | 100 | 2 exact, 43 numeric, 20 programmatic, 35 rubric |
| Science | `tasks/science-100` | 100 | science QA, lab reasoning, and multi-step scientific analysis |

The task sources include datasets and benchmarks such as TAT-QA, FinQA, FinanceBench, FinBen, InvestorBench, HealthBench, MedAgentsBench, PhysicianBench, LegalBench, LawBench, Harvey, OfficeQA, WritingBench, CLAW-Bench, and others.

## Repository Layout

```text
Continual-Skill-Bench/
├── tasks/                         # Released benchmark task directories
│   ├── finance-econ-100/
│   ├── healthcare-100/
│   ├── law-100/
│   ├── math-100/
│   ├── office-100/
│   └── science-100/
├── pipeline/                      # Domain construction pipeline
├── scripts/                       # Dataset download, filtering, curation, and generation scripts
│   ├── finance/
│   ├── healthcare/
│   ├── law/
│   ├── mathematics/
│   ├── office/
│   └── science/
├── analysis/                      # Analysis utilities
├── docs/                          # Design notes and research notes
└── experiments/                   # Example experiment configs
```

Each task directory follows the same high-level structure:

```text
tasks/<domain>-100/
├── task.toml                      # Metadata, resource limits, and execution settings
├── instruction.md                 # 100-subtask instruction sequence
├── environment/
│   ├── tasks_spec.json            # Structured task metadata and scoring specs
│   ├── data/                      # Static data files when needed
│   └── skills/                    # Optional initial domain skills
├── solution/                      # Reference or scaffolded solution assets, when available
└── tests/                         # Verification scripts
```

## Task Format

The core task metadata lives in `environment/tasks_spec.json`. A typical task entry contains:

```json
{
  "task_id": 1,
  "source": "TAT-QA",
  "question": "...",
  "answer": "...",
  "eval_type": "numeric",
  "difficulty": "easy",
  "rubrics": []
}
```

The exact fields vary by source and evaluation type. For rubric-judged tasks, `rubrics` or equivalent judge instructions describe the dimensions used for scoring. For programmatic tasks, the verifier checks generated files or executable outputs.

## Construction Pipeline

The benchmark is built with a four-step pipeline:

1. Domain selection: choose a domain, identify source benchmarks, and define the target mix of easy, medium, and hard subtasks.
2. Download and filtering: collect raw data, normalize schemas, remove duplicates, and select 100 candidate subtasks.
3. Skill-transfer ordering: order subtasks so earlier tasks can plausibly teach reusable operations needed by later tasks.
4. Task directory generation: convert selected tasks into a standard task directory with instructions, task specs, data files, initial skills, and verifiers.

See `pipeline/README.md` for the full construction workflow. Domain-specific scripts and notes live in `scripts/<domain>/`.

## Independent vs Sequential Evaluation

Continual Skill Bench is designed for two complementary settings:

- Independent: each subtask is solved in isolation, with no access to previous subtasks.
- Sequential: a single agent solves the 100 subtasks in order and may create, update, retrieve, or otherwise reuse skills and memories.

The comparison between these settings measures whether sequential experience improves future-task performance. Additional analyses can separate explicit skill reuse from broader context adaptation by inspecting generated skill files, skill-call traces, and verifier feedback.

## Analysis Utilities

This repository includes helper scripts for post-hoc analysis of agent trajectories and generated skills.

From the repository root:

```bash
# Extract skills created by an agent run.
python scripts/extract_created_skills.py \
  /path/to/jobs/<job-name> \
  --output created_skills.md

# Count skill references in a trajectory.
python scripts/count_skill_calls.py \
  --trajectory /path/to/jobs/<job-name>

# Static quality metrics for extracted skills.
python scripts/score_skill_static.py \
  --input-glob "skill_analysis/*_created_skills.md"

# LLM-judge quality metrics for extracted skills.
OPENAI_API_KEY=... python scripts/judge_skill_quality_llm.py \
  --input-glob "*5.3codex_created_skills.md" \
  --model gpt-4.1-mini
```

The skill-quality judge reports separate indicators for format/loadability, procedure quality, generalization, verification, pitfalls, conciseness, toolability, and domain grounding.

## Adding a New Domain

To add a new 100-subtask domain:

1. Create a domain folder under `scripts/<domain>/`.
2. Collect candidate tasks from public or licensed sources.
3. Normalize them into a JSONL schema with `source`, `question`, `answer`, `difficulty`, `eval_type`, and optional `rubrics`.
4. Curate and order 100 subtasks with increasing or recurring skill requirements.
5. Generate `tasks/<domain>-100/` with `instruction.md`, `environment/tasks_spec.json`, data files, initial skills, and tests.
6. Run independent and sequential evaluations and inspect trajectory logs for skill creation and reuse.

The finance pipeline is the most complete reference implementation:

```text
scripts/finance/PIPELINE.md
scripts/finance/finance_tasks_100.md
tasks/finance-econ-100/BUILD.md
```

## Notes

- Some evaluations use LLM judges. Set the required model API keys before running those verifiers.
- Some task environments require internet access for source-data lookup or benchmark setup.
- Generated job logs, extracted skills, and analysis outputs are usually stored outside `Continual-Skill-Bench/` in the repository-level `jobs/`, `skill_analysis/`, or `rebuttal/` directories.

## Citation

If you use Continual Skill Bench, please cite the accompanying paper. Citation information will be added after release.

