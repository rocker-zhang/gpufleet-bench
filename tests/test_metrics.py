from gpufleet_bench.metrics import ABSTAIN, Prediction, Truth, compute


def test_perfect_run_passes_gate():
    truths = {
        "c1": Truth("c1", "xid79", frozenset({"dmesg.xid79", "ecc.dbe.delta"})),
        "c2": Truth("c2", ABSTAIN, frozenset({"thermal.throttle"})),
    }
    preds = {
        "c1": Prediction("c1", "xid79", frozenset({"dmesg.xid79", "ecc.dbe.delta"})),
        "c2": Prediction("c2", ABSTAIN),
    }
    m = compute(truths, preds)
    assert m.precision_at_fired == 1.0
    assert m.false_positive == 0
    assert m.abstention_correctness == 1.0
    assert m.evidence_grounding == 1.0
    assert m.passes_release_gate()


def test_false_positive_blocks_gate():
    # Solver fires on a case whose truth is ABSTAIN -> FP=1 -> gate fails.
    truths = {"c1": Truth("c1", ABSTAIN, frozenset({"thermal.throttle"}))}
    preds = {"c1": Prediction("c1", "xid79", frozenset({"thermal.throttle"}))}
    m = compute(truths, preds)
    assert m.false_positive == 1
    assert not m.passes_release_gate()


def test_hallucinated_evidence_fails_grounding():
    truths = {"c1": Truth("c1", "xid79", frozenset({"dmesg.xid79"}))}
    # Cites a signal not present in the case -> grounding < 1.0.
    preds = {
        "c1": Prediction("c1", "xid79", frozenset({"dmesg.xid79", "ghost.signal"}))
    }
    m = compute(truths, preds)
    assert m.evidence_grounding < 1.0
    assert not m.passes_release_gate()


def test_missing_prediction_counts_as_abstain():
    truths = {"c1": Truth("c1", ABSTAIN, frozenset())}
    m = compute(truths, {})  # no prediction supplied
    assert m.abstention_correctness == 1.0
    assert m.fired == 0
