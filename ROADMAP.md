# bench — module roadmap (M1..M6)

OPEN, Python/uv. The PUBLIC benchmark: question-only cases + release-gating
metrics. NO answer key here (the key lives in the closed `eval-corpus`, pulled at
a fixed tag by the benchmark-gate pipeline). Mirrors the workspace `ROADMAP.md`;
keep tight. See `./CLAUDE.md` §3 for the hard lines.

Release gate (must hold at every milestone): `precision@fired ≥ 0.95`,
`false_positive = 0`, `abstention_correctness ≥ 0.98`, `evidence_grounding = 1.0`.

---

## M1 — harness + gate (foundation)
Question-only case schema mirroring the `agent` SignalSchema; runner that loads
YAML cases, REJECTS any answer key, and drives a pluggable solver (default
`abstain_solver`); the four metrics with `passes_release_gate()`.
- **Exit**: `ruff` + `pytest` green on x86 + arm; gate test enforces all four
  thresholds; at least one EXAMPLE case; `.gitignore` blocks pulled answer keys.

## M2 — two-signal gate + solver adapter
Cases that exercise the `rca` invariant: FIRE only with ≥2 **independent**
signals (independent by SOURCE, not by declared field) else ABSTAIN; cases that
must ABSTAIN on a single corroborating source. A controlplane-solver adapter
that posts a case's evidence pack and parses the returned open `Verdict`.
- **Exit**: single-source cases score as correct-ABSTAIN; multi-source cases as
  correct-FIRE; adapter scores a real `Verdict` against an external key; no
  answer-key leakage (runner reject test still green).

## M3 — cost / efficiency (MFU) cases
Extend cases + metrics to deterministic COST/EFFICIENCY attribution (device→job,
MFU/idle). Numeric verdicts scored on tolerance, with grounding still = 1.0.
- **Exit**: efficiency cases run end-to-end; numeric-tolerance scoring tested;
  `evidence_grounding` unaffected; gate unchanged.

## M4 — capability / ingestion cases (D-0009 + D-0011)
Cases derived from declarative-directive → signal-window across consent tiers:
Tier-0 (DCGM/Prom/dmesg) vs Tier-1 (eBPF/perf). Verify the corpus never encodes
what-to-collect / how-to-interpret (that moat stays server-side).
- **Exit**: tier-tagged cases run; a lint/test asserts no directive-selection or
  interpretation logic leaks into the open corpus; gate unchanged.

## M5 — fleet-aggregation cases (D-0010 paid view)
Cases that exercise cross-node aggregation using ONLY the open aggregation
envelope (open `Verdict` + small envelope in open proto). No fleet answer key
here; license/fleet adjudication stays server-side at the controlplane.
- **Exit**: aggregation-envelope cases score against an external fleet key;
  repo holds no fleet answer key and no license logic; gate unchanged.

## M6 — public leaderboard + GA freeze
Stabilize the case corpus; publish a public leaderboard format + reproducible
scoring instructions (deterministic, key-supplied-externally). Freeze gate
thresholds for GA.
- **Exit**: documented reproducible run; leaderboard schema published; thresholds
  frozen and versioned; CI green on x86 + arm.
