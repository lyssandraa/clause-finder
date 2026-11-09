"""Small text helpers shared by the extractors and the evaluation.

- tokenize / jaccard: used to decide whether two spans "match".
- find_span: locate a quoted span inside the contract (exact or fuzzy).
- split_sentences: used by the rule-based baseline.
- chunk_text: split long contracts into overlapping chunks for the LLM.
"""

import re

from rapidfuzz import fuzz

WORD_PATTERN = re.compile(r"\w+")


def tokenize(text):
    """Lower-case word tokens. Punctuation is ignored."""
    return WORD_PATTERN.findall(text.lower())


def jaccard(text_a, text_b):
    """Token-set Jaccard similarity between two pieces of text (0.0 to 1.0)."""
    tokens_a = set(tokenize(text_a))
    tokens_b = set(tokenize(text_b))
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return overlap / union


def normalize_with_map(text):
    """Collapse whitespace and lower-case the text.

    Returns (normalized_text, index_map) where index_map[i] is the position in
    the original text of character i in the normalized text. This lets us find
    a match in the normalized text and then cut the original text exactly.
    """
    normalized_chars = []
    index_map = []
    previous_was_space = True  # drops leading whitespace
    for position, char in enumerate(text):
        if char.isspace():
            if previous_was_space:
                continue
            normalized_chars.append(" ")
            index_map.append(position)
            previous_was_space = True
        else:
            normalized_chars.append(char.lower())
            index_map.append(position)
            previous_was_space = False
    # Drop a single trailing space, if any.
    if normalized_chars and normalized_chars[-1] == " ":
        normalized_chars.pop()
        index_map.pop()
    return "".join(normalized_chars), index_map


def normalize(text):
    normalized_text, _ = normalize_with_map(text)
    return normalized_text


def find_span(span, text, min_fuzzy_score=90.0):
    """Find where `span` occurs in `text`.

    Tries, in order:
      1. exact match,
      2. match after collapsing whitespace and ignoring case,
      3. fuzzy match (rapidfuzz partial_ratio) with score >= min_fuzzy_score.

    Returns (start, end) character offsets into `text`, or None if the span
    cannot be found. Very short spans (under 3 words) must match exactly or
    after normalisation; fuzzy matching on them is too unreliable.
    """
    if not span or not span.strip():
        return None

    # 1. Exact match.
    start = text.find(span)
    if start != -1:
        return start, start + len(span)

    # 2. Whitespace- and case-insensitive match.
    normalized_text, index_map = normalize_with_map(text)
    normalized_span = normalize(span)
    if not normalized_span:
        return None
    start = normalized_text.find(normalized_span)
    if start != -1:
        end = start + len(normalized_span) - 1
        return index_map[start], index_map[end] + 1

    # 3. Fuzzy match.
    if len(tokenize(span)) < 3:
        return None
    alignment = fuzz.partial_ratio_alignment(normalized_span, normalized_text)
    if alignment is None or alignment.score < min_fuzzy_score:
        return None
    start = alignment.dest_start
    end = alignment.dest_end - 1
    if end < start:
        return None
    return index_map[start], index_map[end] + 1


# A sentence ends at . ! ? or ; followed by whitespace and then something
# that looks like the start of a new sentence or list item.
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?;])\s+(?=[A-Z0-9(\"“])")
PARAGRAPH_BOUNDARY = re.compile(r"\n\s*\n")
MAX_SENTENCE_CHARS = 1500


def split_sentences(text):
    """Split contract text into rough sentences.

    Returns a list of (start, end) offsets into `text`. Contract text from
    EDGAR is messy (headings, numbering, odd line breaks), so this is only an
    approximation. Very long "sentences" are cut into pieces.
    """
    sentences = []
    for paragraph_match in _iterate_pieces(PARAGRAPH_BOUNDARY, text, 0, len(text)):
        paragraph_start, paragraph_end = paragraph_match
        for sentence_start, sentence_end in _iterate_pieces(
            SENTENCE_BOUNDARY, text, paragraph_start, paragraph_end
        ):
            for piece in _cut_long_piece(sentence_start, sentence_end):
                piece_text = text[piece[0]:piece[1]]
                if piece_text.strip():
                    sentences.append(_strip_offsets(text, piece[0], piece[1]))
    return sentences


def _iterate_pieces(boundary_pattern, text, start, end):
    """Yield (start, end) of the pieces of text[start:end] between boundaries."""
    piece_start = start
    for match in boundary_pattern.finditer(text, start, end):
        yield piece_start, match.start()
        piece_start = match.end()
    yield piece_start, end


def _cut_long_piece(start, end):
    pieces = []
    while end - start > MAX_SENTENCE_CHARS:
        pieces.append((start, start + MAX_SENTENCE_CHARS))
        start = start + MAX_SENTENCE_CHARS
    pieces.append((start, end))
    return pieces


def _strip_offsets(text, start, end):
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def chunk_text(text, chunk_size=20000, overlap=2000):
    """Split text into overlapping chunks.

    Returns a list of (start, end) offsets. Each chunk is at most `chunk_size`
    characters, and consecutive chunks share about `overlap` characters, so a
    clause that sits on a chunk boundary is fully contained in at least one
    chunk (as long as the clause is shorter than `overlap`). Chunk ends are
    moved back to a line break or space where possible so words are not cut.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            end = _move_back_to_break(text, start, end, search_window=overlap // 2)
        chunks.append((start, end))
        if end >= text_length:
            break
        next_start = end - overlap
        if next_start <= start:
            # Safety net so the loop always moves forward.
            next_start = end
        start = next_start
    return chunks


def _move_back_to_break(text, start, end, search_window):
    """Move `end` back to just after a newline (or failing that, a space)."""
    lowest_allowed = max(start + 1, end - search_window)
    newline_position = text.rfind("\n", lowest_allowed, end)
    if newline_position != -1:
        return newline_position + 1
    space_position = text.rfind(" ", lowest_allowed, end)
    if space_position != -1:
        return space_position + 1
    return end
