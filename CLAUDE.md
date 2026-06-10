# CLAUDE.md — gpufleet-bench (module session rules)

You are a Claude session **scoped to this repo only** (`gpufleet-bench`). This
is an OPEN module (Apache-2.0), Python + uv. Your edits are **confined to this
repo**.

## What this module is

The public benchmark harness + QUESTION-ONLY cases and the metrics
(precision@fired, false_positive, abstention_correctness, evidence_grounding).
The benchmark gate BLOCKS release at: precision@fired ≥ 0.95, false_positive =
0, abstention_correctness ≥ 0.98, evidence_grounding = 1.0.

## Hard boundaries (do not cross)

- **NO answer key here.** Never add ground-truth labels, expected classes, or
  `answer:`/`expected:`/`fault_class:` to any case in this repo. Answers live in
  the CLOSED eval-corpus. The runner rejects answer keys in case files — keep it
  that way. Never commit a pulled answer key (`.gitignore` blocks it).
- **Cases are question-only.** A case is a normalized signal window the solver
  must adjudicate or ABSTAIN on. Do not leak the correct answer in comments.
- **Edits confined here.** Need a change in another module, the eval-corpus, or
  the control plane? ABSTAIN and file a blocker. Do not reach across.
- **`proto/` is READ-ONLY.** A needed contract change = a *contract change
  proposal* blocker for the orchestrator.
- **No externally-sourced content.** No proprietary error-code semantics in cases
  or metrics.

## If you are blocked

File a short blocker and stop. No cross-repo workarounds.

## Definition of done

`uv run ruff check .` and `uv run pytest -q` pass; new metrics logic has a unit
test, and the release-gate thresholds are not weakened.
