from pathlib import Path

import pytest

from gpufleet_bench.runner import abstain_solver, load_cases, run

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"


def test_loads_question_only_cases():
    cases = load_cases(CASES_DIR)
    assert cases, "expected at least the EXAMPLE case"
    example = next(c for c in cases if c.case_id == "EXAMPLE-xid79")
    assert "dmesg.xid79" in example.signals
    assert "ecc.dbe.delta" in example.signals


def test_rejects_answer_key_in_cases(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("case_id: bad\nfault_class: xid79\nsignals: []\n")
    with pytest.raises(ValueError):
        load_cases(tmp_path)


def test_abstain_solver_never_fires():
    cases = load_cases(CASES_DIR)
    preds = run(cases, abstain_solver)
    assert all(p.fault_class == "ABSTAIN" for p in preds.values())
