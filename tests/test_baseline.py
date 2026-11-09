from clause_finder import baseline

CONTRACT = """
1. Term. This Agreement commences on the Effective Date.

2. Termination. Either party may terminate this Agreement for convenience upon thirty (30) days' prior written notice to the other party.

3. Assignment. Neither party may assign this Agreement without the prior written consent of the other party, which shall not be unreasonably withheld.

4. Limitation of Liability. In no event shall either party's aggregate liability under this Agreement exceed the fees paid in the twelve months preceding the claim.

5. Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of New York.
"""


def test_baseline_finds_each_clause_in_simple_contract():
    results = baseline.extract(CONTRACT)
    assert any("for convenience" in text for text in results["Termination for Convenience"])
    assert any("assign this Agreement" in text for text in results["Anti-Assignment"])
    assert any("aggregate liability" in text for text in results["Cap on Liability"])
    assert any("State of New York" in text for text in results["Governing Law"])


def test_baseline_returns_not_found_as_empty_list():
    results = baseline.extract(CONTRACT)
    assert results["Non-Compete"] == []
    assert results["Change of Control"] == []


def test_incorporation_recital_is_not_governing_law():
    text = "Acme Inc., a corporation organized under the laws of the State of Delaware, agrees as follows."
    assert baseline.extract(text)["Governing Law"] == []
