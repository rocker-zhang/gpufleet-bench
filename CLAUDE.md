# bench — module brief (CLAUDE.md)

## 1. 身份

- **class**: OPEN (Apache-2.0)
- **language / tooling**: Python, `uv`
- **kind**: data (public benchmark harness + question-only case corpus)
- **on-path | bypass | shared-lib**: neither — off-product evaluation tooling;
  never runs inside the agent/controlplane data path.
- **one-line purpose**: the PUBLIC benchmark — question-only cases + the
  release-gating metrics that hold the deterministic RCA/efficiency wedge
  honest. Questions only; the answer key lives in the CLOSED `eval-corpus`.

## 2. 在系统里的位置

See `../ARCHITECTURE.md`.

- **Consumes**: normalized signal windows shaped like what `agent` emits
  (SignalSchema in `proto`) and the open `Verdict` a solver returns; `proto`
  contract shapes are a **read-only** dependency. The closed `eval-corpus`
  answer key is supplied **externally** at a fixed tag (never vendored here).
- **Produces**: `gpufleet_bench/runner.py` (loads question-only YAML cases,
  drives a pluggable solver, scores a run against an externally-supplied answer
  key), `gpufleet_bench/metrics.py` (the release-gate metrics), and the
  `cases/` corpus (question-only). A "solver" is anything that turns a case into
  a FIRE-class-or-ABSTAIN `Verdict` (default `abstain_solver`; a real solver
  posts the evidence pack to a controlplane endpoint and parses the `Verdict`).
- **Edges**: scores `rca`/`controlplane` adjudication quality; mirrors the
  `agent` SignalSchema so cases look like real windows. No runtime edge into any
  module — invoked by the benchmark-gate pipeline, not by the product.

## 3. 继承的红线

Inherits `../RULES.md`. Module-specific hard lines:

- **NO answer key in this repo.** Never add ground-truth labels, expected
  classes, or `answer:` / `expected:` / `fault_class:` to any case. The runner
  REJECTS case files that carry an answer key; `.gitignore` blocks any pulled
  key. Answers live ONLY in the closed `eval-corpus`.
- **Cases are question-only.** A case is a normalized signal window the solver
  must adjudicate or ABSTAIN on. Never leak the correct answer in comments.
- **Metrics are precision@fired / false_positive / abstention_correctness /
  evidence_grounding.** They encode the wedge's invariants: the ≥2-independent-
  signal gate, ABSTAIN-over-guess, and grounded-only citations. Do not weaken
  the release-gate thresholds.
- **`proto/` is READ-ONLY.** A needed contract change = a contract-change
  proposal blocker for the orchestrator — never edit proto.
- **No externally-sourced content.** No proprietary error-code semantics, no
  customer telemetry, in cases or metrics. Personal hardware/time only.

## 4. 当前任务 & 里程碑焦点

Pointers: `../ops/BOARD.md` (cards tagged `bench`).

Current milestone (M1): a question-only case schema that mirrors the `agent`
SignalSchema, a runner that rejects answer keys + drives a pluggable solver, and
the four release-gate metrics with the gate test wired into CI. Default solver
ABSTAINs (safe baseline). See `./ROADMAP.md`.

## 5. 构建与测试

`source ../.envrc` first (project-local toolchain; nothing global — RULES §J).

```sh
uv sync --extra dev

# Emit predictions only (no answer key in this repo):
uv run gpufleet-bench --cases cases

# Score against an externally-supplied answer key (closed eval-corpus, fixed tag):
uv run gpufleet-bench --cases cases --answer-key /path/to/answer-key.yaml

uv run ruff check .
uv run pytest -q
```

CI: ruff + pytest (incl. the metrics-gate test) on `ubuntu-24.04` and
`ubuntu-24.04-arm`, plus gitleaks.

## 6. session 工作规则

- Edits confined to **this repo** (`/home/user/code-money/bench`).
- `proto/` is read-only; need a contract change → ABSTAIN + file a contract-
  change proposal blocker.
- Need another module, the `eval-corpus`, or the controlplane → ABSTAIN and file
  a short blocker. No cross-repo workarounds, never pull/commit an answer key.
- Provenance: personal hardware/time, no externally-sourced content.
- Definition of done: `uv run ruff check .` and `uv run pytest -q` pass; new
  metrics logic has a unit test; release-gate thresholds not weakened.

## 7. 模块路线图

Mirrors `./ROADMAP.md`.

- **M1**: question-only case schema + runner (rejects answer keys) + 4 gate
  metrics + CI gate test.
- **M2**: cases that exercise the ≥2-independent-signal gate (by SOURCE) and
  ABSTAIN-on-single-signal; controlplane-solver adapter (posts evidence pack,
  parses `Verdict`).
- **M3**: cost/efficiency (MFU) attribution cases scored on numeric tolerance,
  not just fault classes.
- **M4**: D-0011 capability/ingestion cases — directive→signal windows across
  consent tiers (DCGM/Prom/dmesg vs eBPF/perf) without leaking how-to-interpret.
- **M5**: fleet-aggregation cases for the D-0010 paid cross-node view (open
  aggregation envelope only; no fleet answer key here).
- **M6**: stabilize corpus, publish public leaderboard format + reproducible
  scoring; freeze gate thresholds for GA.
