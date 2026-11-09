"""Build the static results page from a finished evaluation.

Usage:
    python -m clause_finder.build_site
    python -m clause_finder.build_site --results results/test_qwen3-8b --split test

The output is one self-contained file, docs/index.html, which GitHub Pages can
serve. It needs no server, no API key and no model. Numbers are recomputed from
the saved predictions and checked against results.csv, so the page cannot
silently show results that disagree with the evaluation.
"""

import argparse
import csv
import json
from pathlib import Path

from clause_finder import config
from clause_finder.data import load_contracts
from clause_finder.evaluate import build_rows, find_failures, score
from clause_finder.metrics import match_spans

DEFAULT_RESULTS = config.RESULTS_DIR / "test_qwen3-8b"
TEMPLATE_PATH = Path(__file__).parent / "site_template.html"
OUTPUT_PATH = config.PROJECT_ROOT / "docs" / "index.html"
PLACEHOLDER = "__SITE_DATA__"
APPROACHES = ["baseline", "llm"]


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def read_csv_rows(path):
    with open(path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def label_quotes(predicted, gold):
    """Return each predicted quote with whether it matched a gold span."""
    matched_indexes = set()
    for predicted_index, _gold_index, _similarity in match_spans(predicted, gold):
        matched_indexes.add(predicted_index)

    labelled = []
    for index, text in enumerate(predicted):
        labelled.append({"text": text, "matched": index in matched_indexes})
    return labelled


def check_rows_match(computed_rows, saved_rows):
    """Raise ValueError if recomputed metrics differ from the saved results.csv."""
    if len(computed_rows) != len(saved_rows):
        raise ValueError("results.csv has a different number of rows from the predictions.")

    for computed, saved in zip(computed_rows, saved_rows):
        for column, value in computed.items():
            if str(value) != saved[column]:
                raise ValueError(
                    f"{computed['clause_type']}, {column}: predictions give {value}, "
                    f"but results.csv has {saved[column]}. Re-run the evaluation."
                )


def build_contract_entries(contracts, all_predictions):
    entries = []
    for contract in contracts:
        clauses = {}
        for clause_type in config.CLAUSE_TYPES:
            gold = contract.gold_spans[clause_type]
            clauses[clause_type] = {"gold": gold}
            for approach in APPROACHES:
                predicted = all_predictions[approach][contract.contract_id][clause_type]
                clauses[clause_type][approach] = label_quotes(predicted, gold)
        entries.append({"name": contract.contract_id.strip(), "clauses": clauses})
    return entries


def build_failures(contracts, all_predictions):
    failures = {}
    for approach in APPROACHES:
        failures[approach] = {}
        for clause_type in config.CLAUSE_TYPES:
            failures[approach][clause_type] = find_failures(
                contracts, all_predictions[approach], clause_type
            )
    return failures


def render_page(template, site_data):
    """Insert the data into the template.

    "<" is escaped so that text from a contract can never close the <script> tag.
    """
    if PLACEHOLDER not in template:
        raise ValueError(f"The template does not contain {PLACEHOLDER}.")
    data_json = json.dumps(site_data, ensure_ascii=False).replace("<", "\\u003c")
    return template.replace(PLACEHOLDER, data_json)


def build_site(results_dir, split):
    contracts = load_contracts(split)
    all_predictions = {}
    all_scores = {}
    for approach in APPROACHES:
        all_predictions[approach] = read_json(results_dir / f"predictions_{approach}.json")
        all_scores[approach] = score(contracts, all_predictions[approach])

    rows = build_rows(all_scores, len(contracts))
    check_rows_match(rows, read_csv_rows(results_dir / "results.csv"))

    site_data = {
        "clause_types": list(config.CLAUSE_TYPES),
        "rows": rows,
        "stats": read_json(results_dir / "llm_stats.json"),
        "contracts": build_contract_entries(contracts, all_predictions),
        "failures": build_failures(contracts, all_predictions),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(render_page(template, site_data), encoding="utf-8")
    return OUTPUT_PATH


def main():
    parser = argparse.ArgumentParser(description="Build the static results page.")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--split", default="test", choices=["dev", "test"])
    args = parser.parse_args()

    output = build_site(args.results, args.split)
    print(f"Wrote {output} ({output.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
