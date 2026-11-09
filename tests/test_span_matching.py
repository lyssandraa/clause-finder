from clause_finder.text_utils import chunk_text, find_span, jaccard, split_sentences, tokenize


CONTRACT = (
    "12.1  Assignment.\n"
    "Neither party may assign this Agreement without the prior written\n"
    "consent of the other party.   This Agreement shall be governed by the "
    "laws of the State of New York."
)


def test_tokenize_ignores_case_and_punctuation():
    assert tokenize("The Laws, of NEW York.") == ["the", "laws", "of", "new", "york"]


def test_jaccard_identical_and_disjoint():
    assert jaccard("governed by New York law", "governed by New York law") == 1.0
    assert jaccard("apple banana", "cherry date") == 0.0


def test_jaccard_partial_overlap():
    # tokens {a, b, c} vs {b, c, d}: overlap 2, union 4
    assert jaccard("a b c", "b c d") == 0.5


def test_jaccard_empty_inputs():
    assert jaccard("", "") == 1.0
    assert jaccard("something", "") == 0.0


def test_find_span_exact():
    span = "This Agreement shall be governed by the laws of the State of New York."
    start, end = find_span(span, CONTRACT)
    assert CONTRACT[start:end] == span


def test_find_span_ignores_whitespace_and_case():
    # The model collapsed the line break and the triple space, and changed case.
    span = "neither party may assign this agreement without the prior written consent of the other party."
    start, end = find_span(span, CONTRACT)
    found = CONTRACT[start:end]
    assert found.startswith("Neither party may assign")
    assert found.endswith("other party.")
    assert "\n" in found  # we return the original text, not the normalised one


def test_find_span_fuzzy_small_typo():
    span = "Neither party may asign this Agreement without the prior writen consent of the other party."
    location = find_span(span, CONTRACT)
    assert location is not None
    start, end = location
    assert "assign this Agreement" in CONTRACT[start:end]


def test_find_span_rejects_invented_text():
    span = "Either party may terminate this Agreement for convenience on thirty days notice."
    assert find_span(span, CONTRACT) is None


def test_find_span_rejects_empty_and_short_fuzzy():
    assert find_span("", CONTRACT) is None
    assert find_span("   ", CONTRACT) is None
    # Short spans are not fuzzy matched: "New Yrok" must not match "New York".
    assert find_span("New Yrok", CONTRACT) is None


def test_split_sentences_returns_offsets_into_text():
    sentences = split_sentences(CONTRACT)
    texts = [CONTRACT[start:end] for start, end in sentences]
    assert any(text.startswith("Neither party may assign") for text in texts)
    assert any(text.startswith("This Agreement shall be governed") for text in texts)
    for text in texts:
        assert text == text.strip()


def test_chunk_text_covers_everything_with_overlap():
    text = ("word " * 5000).strip()  # about 25,000 characters
    chunks = chunk_text(text, chunk_size=6000, overlap=1000)
    assert chunks[0][0] == 0
    assert chunks[-1][1] == len(text)
    for (start_a, end_a), (start_b, end_b) in zip(chunks, chunks[1:]):
        assert start_b < end_a  # consecutive chunks overlap
        assert end_a - start_b >= 500  # by a meaningful amount
        assert end_a - start_a <= 6000


def test_chunk_text_short_text_is_one_chunk():
    assert chunk_text("short contract", chunk_size=100, overlap=10) == [(0, 14)]


def test_chunk_text_does_not_cut_words():
    text = ("abcdefghij " * 1000).strip()
    for start, end in chunk_text(text, chunk_size=1000, overlap=100):
        chunk = text[start:end].strip()
        for word in chunk.split():
            assert word == "abcdefghij"
