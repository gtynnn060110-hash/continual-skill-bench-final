# Continual Skill Bench

This repository packages the Continual Skill Bench tasks together with a slim Harbor-based evaluation harness. Harbor provides the agent execution, sandbox management, job orchestration, verifier execution, and trajectory logging. Continual Skill Bench provides the benchmark tasks, construction pipeline, and experiment configs.

## Repository Layout

```text
.
├── src/harbor/                    # Core Harbor harness
├── pyproject.toml                 # Editable Harbor install target
├── Continual-Skill-Bench/
│   ├── tasks/                     # Benchmark task directories
│   ├── experiments/configs/       # Example Harbor job configs
│   ├── pipeline/                  # Benchmark construction pipeline
│   ├── scripts/                   # Dataset download/filter/generation scripts
│   └── docs/                      # Benchmark notes
└── README.md
```

The included Harbor harness keeps the core agents used for our experiments:

```text
codex, codex-seq, codex-seq-icl,
claude-code, claude-code-seq, claude-code-seq-debug, claude-code-rag,
nop, oracle
```

## Installation

Create an environment and install Harbor from this repository in editable mode:

```bash
cd Continual-Skill-Bench-final
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

You should then be able to run:

```bash
harbor --help
harbor jobs start --help
```

Most tasks use Docker sandboxes, so Docker should be installed and running. Set the API key required by the agent/model you use, for example:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
```

## Running A Benchmark Task

A domain-level sequential task can be run directly with `--path`:

```bash
harbor jobs start \
  --path Continual-Skill-Bench/tasks/finance-econ-100 \
  --agent codex-seq \
  --model openai/gpt-4o \
  --job-name finance_seq_codex \
  --jobs-dir jobs
```

Other main domains are:

```text
Continual-Skill-Bench/tasks/healthcare-100
Continual-Skill-Bench/tasks/law-100
Continual-Skill-Bench/tasks/math-100
Continual-Skill-Bench/tasks/office-100
Continual-Skill-Bench/tasks/science-100
```

## Independent Trial Runs

Independent-trial task directories are also included. For example:

```bash
harbor jobs start \
  --path Continual-Skill-Bench/tasks/finance-econ-100-independent-trials \
  --agent codex \
  --model openai/gpt-4o \
  --job-name finance_ind_codex \
  --jobs-dir jobs \
  --n-concurrent 4
```

Equivalent independent-trial directories are provided for healthcare, law, math, and office.

## Running With Config Files

Example Harbor job configs live under:

```text
Continual-Skill-Bench/experiments/configs/
```

Run a config from the benchmark directory so relative task paths resolve:

```bash
cd Continual-Skill-Bench
harbor jobs start -c experiments/configs/finance_econ_100_independent_trials.yaml
```

or from the repository root:

```bash
harbor jobs start -c Continual-Skill-Bench/experiments/configs/finance_econ_100_independent_trials.yaml
```

If a config contains relative paths such as `./tasks/...`, run it from `Continual-Skill-Bench/` or update the paths.

## Outputs

Job outputs are written to the selected `jobs_dir`. A typical trial contains:

```text
jobs/<job_name>/<trial_name>/
├── result.json
├── agent/
│   ├── command-*/stdout.txt
│   ├── trajectory.json
│   └── skills-verified.txt
└── verifier/
    ├── reward.txt
    └── ctrf.json
```

Sequential agents may also create or update skills during the run. These are reflected in the agent logs and trajectory files.

## Benchmark Contents

Continual Skill Bench evaluates whether agents can build, retain, and reuse skills across related subtasks. Each main domain contains a 100-subtask sequence mixing exact-match, numeric, F1, programmatic, and rubric-judge evaluation.

The main task directories are:

| Domain | Path |
| --- | --- |
| Finance/Economics | `Continual-Skill-Bench/tasks/finance-econ-100` |
| Healthcare | `Continual-Skill-Bench/tasks/healthcare-100` |
| Law | `Continual-Skill-Bench/tasks/law-100` |
| Mathematics | `Continual-Skill-Bench/tasks/math-100` |
| Office | `Continual-Skill-Bench/tasks/office-100` |
| Science | `Continual-Skill-Bench/tasks/science-100` |

See `Continual-Skill-Bench/README.md` for more detail on task format, construction pipeline, and analysis utilities.

## Development Notes

- Use `pip install -e .` after editing Harbor code under `src/harbor/`.
- Use `harbor jobs start --help` to inspect the current CLI options.
- The benchmark construction scripts are under `Continual-Skill-Bench/scripts/`.
- The construction pipeline is documented under `Continual-Skill-Bench/pipeline/`.

## Citation

If you use Continual Skill Bench, please cite the accompanying paper. Citation information will be added after release.
