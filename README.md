# gpufleet-bench

Apache-2.0 · OPEN module · Python (uv)

The **public benchmark harness** and **question-only cases** for gpufleet's
RCA/efficiency wedge. It contains **NO answer key** — ground-truth labels live
in the **closed** `eval-corpus` repo and are pulled at a fixed tag by the closed
benchmark-gate pipeline.

## What's here

- `gpufleet_bench/runner.py` — loads question-only YAML cases, invokes a
  pluggable solver, and (given an externally-supplied answer key) scores a run.
  It **rejects** any case file that contains an answer key.
- `gpufleet_bench/metrics.py` — the release-gating metrics:
  - `precision@fired` (must be ≥ 0.95)
  - `false_positive` (must be 0)
  - `abstention_correctness` (must be ≥ 0.98)
  - `evidence_grounding` (must be 1.0 — no hallucinated/ungrounded citations)
- `cases/EXAMPLE-xid79.yaml` — a question-only case (no label).

The benchmark gate **blocks release**: `Metrics.passes_release_gate()` encodes
the thresholds above.

## Run

```sh
uv sync --extra dev

# Emit predictions only (no answer key in this repo):
uv run gpufleet-bench --cases cases

# Score against an externally-supplied answer key (closed eval-corpus):
uv run gpufleet-bench --cases cases --answer-key /path/to/answer-key.yaml
```

The default solver (`abstain_solver`) always ABSTAINs — a safe baseline. A real
solver posts each case's evidence pack to a control-plane endpoint and parses
the returned `Verdict`.

## Boundaries

- **No answer key** in this repo (and `.gitignore` blocks pulled answer keys).
- `proto/` is a read-only dependency; this repo never edits it.

## Develop

```sh
uv run ruff check .
uv run pytest -q
```

CI runs ruff + pytest on `ubuntu-24.04` and `ubuntu-24.04-arm`, plus gitleaks.
