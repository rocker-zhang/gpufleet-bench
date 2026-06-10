"""Benchmark metrics for gpufleet RCA verdicts.

A *case* has a ground-truth label (from the CLOSED answer key) and the solver
returns a *prediction*. Both are normalized to the dataclasses below. The
"ABSTAIN" fault class is the sentinel for "no fault adjudicated".

Release-gating metrics:
  - precision@fired      : of the cases where the solver FIRED a class, fraction correct
  - false_positive       : count of fires on cases whose truth is ABSTAIN (must be 0)
  - abstention_correctness : of truth-ABSTAIN cases, fraction the solver also ABSTAINed
  - evidence_grounding   : fraction of FIRED cases whose cited signals are all
                           a subset of the signals actually present in the case
                           (no hallucinated evidence)
"""

from __future__ import annotations

from dataclasses import dataclass, field

ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class Truth:
    case_id: str
    fault_class: str  # ABSTAIN means "no fault"
    present_signals: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Prediction:
    case_id: str
    fault_class: str  # ABSTAIN means the solver declined to adjudicate
    cited_signals: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Metrics:
    precision_at_fired: float
    false_positive: int
    abstention_correctness: float
    evidence_grounding: float
    fired: int
    abstained: int

    def passes_release_gate(self) -> bool:
        """The benchmark gate that BLOCKS release."""
        return (
            self.precision_at_fired >= 0.95
            and self.false_positive == 0
            and self.abstention_correctness >= 0.98
            and self.evidence_grounding >= 1.0
        )


def compute(truths: dict[str, Truth], preds: dict[str, Prediction]) -> Metrics:
    """Compute release metrics. Missing predictions count as ABSTAIN."""
    fired_total = 0
    fired_correct = 0
    false_positive = 0
    abstain_truth_total = 0
    abstain_correct = 0
    grounded_fires = 0

    for case_id, truth in truths.items():
        pred = preds.get(
            case_id, Prediction(case_id=case_id, fault_class=ABSTAIN)
        )
        truth_is_abstain = truth.fault_class == ABSTAIN
        pred_fired = pred.fault_class != ABSTAIN

        if truth_is_abstain:
            abstain_truth_total += 1
            if not pred_fired:
                abstain_correct += 1

        if pred_fired:
            fired_total += 1
            if pred.fault_class == truth.fault_class:
                fired_correct += 1
            if truth_is_abstain:
                false_positive += 1
            # Evidence grounding: every cited signal must actually be present.
            if pred.cited_signals <= truth.present_signals:
                grounded_fires += 1

    precision_at_fired = fired_correct / fired_total if fired_total else 1.0
    abstention_correctness = (
        abstain_correct / abstain_truth_total if abstain_truth_total else 1.0
    )
    evidence_grounding = grounded_fires / fired_total if fired_total else 1.0

    return Metrics(
        precision_at_fired=precision_at_fired,
        false_positive=false_positive,
        abstention_correctness=abstention_correctness,
        evidence_grounding=evidence_grounding,
        fired=fired_total,
        abstained=len(truths) - fired_total,
    )
