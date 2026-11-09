"""Precision / recall / F1 at the contract level and the span level.

Contract level: for each (contract, clause type), did the system correctly
say whether the clause is present?
  - TP: the clause is present and the system found at least one span
  - FP: the clause is absent but the system returned something
  - FN: the clause is present but the system returned nothing
  - TN: absent and nothing returned

Span level: individual predicted spans are matched one-to-one against gold
spans. A pair counts as a match if their token Jaccard similarity is at least
0.5. Unmatched predictions are FPs, unmatched gold spans are FNs.
"""

from dataclasses import dataclass

from clause_finder.text_utils import jaccard

SPAN_MATCH_THRESHOLD = 0.5


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    def add(self, other):
        self.tp += other.tp
        self.fp += other.fp
        self.fn += other.fn
        self.tn += other.tn


def precision(counts):
    """None when the system made no predictions (precision is undefined)."""
    if counts.tp + counts.fp == 0:
        return None
    return counts.tp / (counts.tp + counts.fp)


def recall(counts):
    """None when there is nothing to find (recall is undefined)."""
    if counts.tp + counts.fn == 0:
        return None
    return counts.tp / (counts.tp + counts.fn)


def f1(counts):
    """Harmonic mean of precision and recall, written as 2TP / (2TP + FP + FN).

    This form gives 0.0 (not an error) when there were gold items but no
    correct predictions. None only when there was nothing to find and
    nothing was predicted.
    """
    denominator = 2 * counts.tp + counts.fp + counts.fn
    if denominator == 0:
        return None
    return 2 * counts.tp / denominator


def contract_level_counts(predicted_spans, gold_spans):
    """Counts for one contract and one clause type (exactly one of tp/fp/fn/tn is 1)."""
    predicted_present = len(predicted_spans) > 0
    gold_present = len(gold_spans) > 0
    if predicted_present and gold_present:
        return Counts(tp=1)
    if predicted_present and not gold_present:
        return Counts(fp=1)
    if not predicted_present and gold_present:
        return Counts(fn=1)
    return Counts(tn=1)


def match_spans(predicted_spans, gold_spans, threshold=SPAN_MATCH_THRESHOLD):
    """Greedy one-to-one matching between predicted and gold spans.

    All (predicted, gold) pairs with Jaccard >= threshold are sorted from most
    to least similar; each pair is accepted if neither side is already used.

    Returns a list of (predicted_index, gold_index, similarity).
    """
    candidate_pairs = []
    for predicted_index, predicted in enumerate(predicted_spans):
        for gold_index, gold in enumerate(gold_spans):
            similarity = jaccard(predicted, gold)
            if similarity >= threshold:
                candidate_pairs.append((similarity, predicted_index, gold_index))

    # Highest similarity first; ties broken by position so results are stable.
    candidate_pairs.sort(key=lambda pair: (-pair[0], pair[1], pair[2]))

    used_predicted = set()
    used_gold = set()
    matches = []
    for similarity, predicted_index, gold_index in candidate_pairs:
        if predicted_index in used_predicted or gold_index in used_gold:
            continue
        used_predicted.add(predicted_index)
        used_gold.add(gold_index)
        matches.append((predicted_index, gold_index, similarity))
    return matches


def span_level_counts(predicted_spans, gold_spans, threshold=SPAN_MATCH_THRESHOLD):
    """Span-level counts for one contract and one clause type (no TN at span level)."""
    matches = match_spans(predicted_spans, gold_spans, threshold)
    true_positives = len(matches)
    return Counts(
        tp=true_positives,
        fp=len(predicted_spans) - true_positives,
        fn=len(gold_spans) - true_positives,
    )
