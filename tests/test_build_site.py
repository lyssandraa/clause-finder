"""Tests for the static results page generator."""

import pytest

from clause_finder.build_site import check_rows_match, label_quotes, render_page


def test_label_quotes_marks_only_matching_predictions():
    gold = ["this agreement may not be assigned without consent"]
    predicted = [
        "this agreement may not be assigned without consent",
        "the governing law is the law of Delaware",
    ]

    labelled = label_quotes(predicted, gold)

    assert labelled[0] == {"text": predicted[0], "matched": True}
    assert labelled[1] == {"text": predicted[1], "matched": False}


def test_render_page_cannot_be_closed_early_by_contract_text():
    template = "<script>const DATA = __SITE_DATA__;</script>"

    page = render_page(template, {"quote": "</script><b>text</b>"})

    assert page.count("</script>") == 1
    assert "\\u003c/script>" in page


def test_render_page_requires_the_placeholder():
    with pytest.raises(ValueError):
        render_page("<html></html>", {})


def test_check_rows_match_accepts_the_same_values():
    computed = [{"clause_type": "Non-Compete", "gold_spans": 3, "contract_f1": "0.79"}]
    saved = [{"clause_type": "Non-Compete", "gold_spans": "3", "contract_f1": "0.79"}]

    check_rows_match(computed, saved)


def test_check_rows_match_rejects_stale_results():
    computed = [{"clause_type": "Non-Compete", "gold_spans": 3, "contract_f1": "0.79"}]
    saved = [{"clause_type": "Non-Compete", "gold_spans": "3", "contract_f1": "0.65"}]

    with pytest.raises(ValueError):
        check_rows_match(computed, saved)
