"""Benchmark runner.

Loads question-only YAML cases (NO answer key in this repo), invokes a pluggable
solver for each case, and — when given a separately-supplied answer key —
computes the release metrics via gpufleet_bench.metrics.

The answer key is NOT in this repo. It lives in the closed eval-corpus and is
provided at run time (a path/loader) by the closed benchmark-gate pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import yaml

from .metrics import ABSTAIN, Prediction, Truth, compute


@dataclass(frozen=True)
class Case:
    """A question-only case: the evidence window, with NO ground-truth label."""

    case_id: str
    device_uuid: str
    signals: frozenset[str]
    raw: dict


# A Solver maps a Case to a Prediction. The default solver is an example; the
# real solver posts the evidence pack to a control-plane endpoint.
Solver = Callable[[Case], Prediction]


def load_cases(cases_dir: str | Path) -> list[Case]:
    """Load every question-only YAML case in a directory."""
    out: list[Case] = []
    for path in sorted(Path(cases_dir).glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if doc is None:
            continue
        if "expected" in doc or "answer" in doc or "fault_class" in doc:
            raise ValueError(
                f"{path} contains an answer key; cases in this repo are "
                "question-only (answers live in the closed eval-corpus)"
            )
        signals = frozenset(s["name"] for s in doc.get("signals", []))
        out.append(
            Case(
                case_id=doc["case_id"],
                device_uuid=doc.get("device_uuid", ""),
                signals=signals,
                raw=doc,
            )
        )
    return out


def abstain_solver(case: Case) -> Prediction:
    """A trivial, always-safe solver: it never fires (always ABSTAINs).

    Useful as a smoke-test baseline and for the metrics unit test. A real solver
    posts case.raw as an evidence pack to a control-plane endpoint and parses the
    returned Verdict.
    """
    return Prediction(case_id=case.case_id, fault_class=ABSTAIN)


def run(cases: list[Case], solver: Solver) -> dict[str, Prediction]:
    return {c.case_id: solver(c) for c in cases}


def load_answer_key(path: str | Path) -> dict[str, Truth]:
    """Load a ground-truth answer key (supplied externally, e.g. eval-corpus).

    Expected YAML shape:
        truths:
          - case_id: ...
            fault_class: ABSTAIN | <class>
            present_signals: [name, ...]
    """
    doc = yaml.safe_load(Path(path).read_text())
    truths: dict[str, Truth] = {}
    for t in doc.get("truths", []):
        truths[t["case_id"]] = Truth(
            case_id=t["case_id"],
            fault_class=t.get("fault_class", ABSTAIN),
            present_signals=frozenset(t.get("present_signals", [])),
        )
    return truths


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="gpufleet-bench")
    p.add_argument("--cases", default="cases", help="dir of question-only YAML cases")
    p.add_argument(
        "--answer-key",
        default=None,
        help="path to an external answer key (NOT in this repo). If omitted, "
        "only predictions are emitted (no scoring).",
    )
    args = p.parse_args(argv)

    cases = load_cases(args.cases)
    preds = run(cases, abstain_solver)

    if args.answer_key is None:
        json.dump(
            {cid: {"fault_class": pr.fault_class} for cid, pr in preds.items()},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0

    truths = load_answer_key(args.answer_key)
    m = compute(truths, preds)
    json.dump(
        {
            "precision_at_fired": m.precision_at_fired,
            "false_positive": m.false_positive,
            "abstention_correctness": m.abstention_correctness,
            "evidence_grounding": m.evidence_grounding,
            "fired": m.fired,
            "abstained": m.abstained,
            "release_gate_pass": m.passes_release_gate(),
        },
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if m.passes_release_gate() else 1


if __name__ == "__main__":
    raise SystemExit(main())
