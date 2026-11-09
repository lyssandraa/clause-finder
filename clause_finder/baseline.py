"""Rule-based baseline: keyword / regex patterns per clause type.

The contract is split into rough sentences. A sentence is returned for a
clause type if it matches that clause type's rule. If no sentence matches,
the result for that clause type is an empty list ("not found").

The patterns were written by hand and adjusted on the dev split only
(never the test split).
"""

import re

from clause_finder import config
from clause_finder.text_utils import split_sentences


def _compile(pattern):
    return re.compile(pattern, re.IGNORECASE)


# Each rule is a list of "groups". A sentence matches the rule if, for at
# least one group, the sentence matches EVERY pattern in that group.
# (So: OR between groups, AND within a group.)
RULES = {
    "Governing Law": [
        [_compile(r"\bgoverned\b(\s+\w+){0,3}\s+by\b"), _compile(r"\blaws?\b")],
        [_compile(r"\b(in\s+accordance\s+with|pursuant\s+to)\s+the\s+laws?\s+of\b")],
        [_compile(r"\bconstrued\b"), _compile(r"\blaws?\s+of\b")],
        [_compile(r"\bgoverning\s+law\b"), _compile(r"\blaws?\s+of\b")],
        [_compile(r"\binterpreted\b"), _compile(r"\baccordance\s+with\s+the\s+laws?\b")],
    ],
    "Anti-Assignment": [
        [
            _compile(r"\bassign"),
            _compile(r"\b(without|prior)\b.{0,60}\b(consent|approval)\b"),
        ],
        [_compile(r"\b(shall|may|will)\s+not\b.{0,80}\bassign")],
        [_compile(r"\bnot\s+(be\s+)?assignable\b")],
        [_compile(r"\b(no|neither|not)\b.{0,40}\bright\b.{0,60}\bassign")],
        [_compile(r"\bagrees?\s+not\s+to\b.{0,60}\bassign")],
        [_compile(r"\bassign"), _compile(r"\bnotice\b"), _compile(r"\b(shall|must)\s+(give|provide|notify)")],
    ],
    "Change of Control": [
        [_compile(r"\bchange\s+(of|in)\s+(the\s+)?(control|ownership)\b")],
        [
            _compile(r"\b(merger|merge|consolidat\w*|reorgani[sz]ation|acquisition)\b"),
            _compile(r"\b(terminat\w*|consent|assign\w*|notify|notice)\b"),
            _compile(r"\b(control|substantial\w*|voting|operation\s+of\s+law|ownership|merger|consolidation)\b"),
        ],
    ],
    "Termination for Convenience": [
        [_compile(r"\bterminat"), _compile(r"\bfor\s+(its\s+)?convenience\b")],
        [_compile(r"\bterminat"), _compile(r"\bwithout\s+cause\b")],
        [_compile(r"\bterminat"), _compile(r"\bfor\s+any\s+reason\b")],
        [_compile(r"\bterminat"), _compile(r"\b(for\s+)?no\s+reason\b")],
        [
            _compile(r"\bterminat\w*\s+this\s+agreement\s+at\s+any\s+time\b"),
            _compile(r"\bnotice\b"),
        ],
        [
            _compile(r"\bterminat"),
            _compile(r"\bupon\s+(\w+\s+){0,2}\(?\d*\)?\s*(days|months)['’]?\s+(prior\s+)?(written\s+)?notice\b"),
            _compile(r"\b(either|any)\s+party\b"),
        ],
    ],
    "Cap on Liability": [
        [_compile(r"\bliabilit"), _compile(r"\b(shall\s+not\s+exceed|not\s+to\s+exceed|in\s+excess\s+of)\b")],
        [_compile(r"\bliabilit"), _compile(r"\blimited\s+to\b")],
        [_compile(r"\b(aggregate|total|maximum|cumulative)\s+liabilit")],
        [
            _compile(r"\b(in\s+no\s+event|under\s+no\s+circumstances|not\s+be\s+liable)\b"),
            _compile(r"\b(consequential|incidental|indirect|special|punitive|lost\s+profits)\b"),
        ],
        [_compile(r"\blimitation\s+of\s+liabilit")],
        [_compile(r"\bliabilit"), _compile(r"\b(is|are|shall\s+be)\s+excluded\b")],
        [_compile(r"\b(claim|action)\b"), _compile(r"\bmore\s+than\s+(\w+\s+){0,2}\(?\d*\)?\s*(years?|months?)\s+after\b")],
    ],
    "Non-Compete": [
        [_compile(r"\bnon-?compet")],
        [
            _compile(r"\b(shall|will|may)\s+not\b|\bagrees?\s+not\s+to\b|\brefrain\b|\bno\s+\w+\s+(shall|will|may)\b"),
            _compile(r"\bcompet\w*"),
        ],
        [
            _compile(r"\b(shall|will|may)\s+not\b|\bagrees?\s+not\s+to\b"),
            _compile(r"\b(engage|develop|manufacture|market|sell|distribute)\b"),
            _compile(r"\b(similar|competitive|competing)\b"),
        ],
    ],
}


def sentence_matches(sentence, rule_groups):
    """True if the sentence matches every pattern in at least one group."""
    for group in rule_groups:
        all_patterns_match = True
        for pattern in group:
            if not pattern.search(sentence):
                all_patterns_match = False
                break
        if all_patterns_match:
            return True
    return False


def extract(contract_text):
    """Run the baseline on one contract.

    Returns {clause_type: [matching sentence, ...]}; an empty list means
    "not found".
    """
    sentence_offsets = split_sentences(contract_text)
    sentences = []
    for start, end in sentence_offsets:
        sentences.append(contract_text[start:end])

    results = {}
    for clause_type in config.CLAUSE_TYPES:
        matches = []
        for sentence in sentences:
            if sentence_matches(sentence, RULES[clause_type]) and sentence not in matches:
                matches.append(sentence)
        results[clause_type] = matches
    return results
