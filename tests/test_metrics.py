import pytest

from clause_finder.metrics import (
    Counts,
    contract_level_counts,
    f1,
    match_spans,
    precision,
    recall,
    span_level_counts,
)


def test_precision_recall_f1_basic():
    counts = Counts(tp=3, fp=1, fn=2)
    assert precision(counts) == pytest.approx(0.75)
    assert recall(counts) == pytest.approx(0.6)
    # 2*3 / (2*3 + 1 + 2) = 6/9
    assert f1(counts) == pytest.approx(6 / 9)


def test_undefined_metrics_are_none():
    nothing_predicted = Counts(tp=0, fp=0, fn=4)
    assert precision(nothing_predicted) is None
    assert recall(nothing_predicted) == 0.0
    assert f1(nothing_predicted) == 0.0

    nothing_to_find = Counts(tp=0, fp=0, fn=0, tn=10)
    assert recall(nothing_to_find) is None
    assert f1(nothing_to_find) is None


def test_contract_level_counts_all_four_cases():
    assert contract_level_counts(["x"], ["y"]) == Counts(tp=1)
    assert contract_level_counts(["x"], []) == Counts(fp=1)
    assert contract_level_counts([], ["y"]) == Counts(fn=1)
    assert contract_level_counts([], []) == Counts(tn=1)


def test_contract_level_tp_even_if_wrong_text():
    # Contract level only asks "is the clause there?", not "is the text right?".
    assert contract_level_counts(["completely different"], ["gold text"]) == Counts(tp=1)


def test_match_spans_threshold():
    gold = ["this agreement is governed by the laws of new york"]
    close = ["governed by the laws of new york"]  # 7 of 10 tokens -> 0.7
    far = ["the laws of new york"]  # 5 of 10 tokens -> 0.5 (exactly at threshold)
    too_far = ["new york"]  # 2 of 10 tokens -> 0.2
    assert len(match_spans(close, gold)) == 1
    assert len(match_spans(far, gold)) == 1
    assert len(match_spans(too_far, gold)) == 0


def test_match_spans_is_one_to_one():
    gold = ["neither party may assign this agreement"]
    predicted = [
        "neither party may assign this agreement",
        "neither party may assign this agreement without consent",
    ]
    matches = match_spans(predicted, gold)
    assert len(matches) == 1
    assert matches[0][0] == 0  # the exact copy wins
    counts = span_level_counts(predicted, gold)
    assert counts == Counts(tp=1, fp=1, fn=0)


def test_span_level_counts_mixed():
    gold = ["governed by the laws of delaware", "liability shall not exceed the fees paid"]
    predicted = ["governed by the laws of delaware", "some unrelated sentence about notices"]
    assert span_level_counts(predicted, gold) == Counts(tp=1, fp=1, fn=1)


def test_counts_add():
    total = Counts()
    total.add(Counts(tp=1, fp=2))
    total.add(Counts(fn=3, tn=4))
    assert total == Counts(tp=1, fp=2, fn=3, tn=4)
