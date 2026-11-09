"""Evaluate the baseline and/or the LLM extractor against CUAD gold labels.

Examples:
    python -m clause_finder.evaluate --approach baseline --split dev
    python -m clause_finder.evaluate --approach both --limit 5      # quick check first
    python -m clause_finder.evaluate --approach both                # full test set (50 contracts)

Outputs (in results/<split> or results/<split>_first<N>, with the model name
added to the folder for local models, e.g. results/test_qwen3-8b):
    results.md, results.csv        metrics table: baseline vs LLM
    failures.md                    up to 5 failures per clause type and approach
    predictions_<approach>.json    raw predictions, for manual review
"""

import argparse
import csv
import json
import time

from clause_finder import baseline, config
from clause_finder.data import load_contracts
from clause_finder.llm_extractor import CONFIGURATION_ERRORS, LLMExtractor, estimate_cost
from clause_finder.metrics import (
    Counts,
    contract_level_counts,
    f1,
    match_spans,
    precision,
    recall,
    span_level_counts,
)
from clause_finder.text_utils import jaccard

APPROACH_NAMES = {"baseline": "Baseline (regex)", "llm": "LLM"}
FAILURES_PER_CLAUSE = 5
MAX_QUOTE_CHARS = 700


# ---------------------------------------------------------------- running

def run_baseline(contracts):
    predictions = {}
    for contract in contracts:
        predictions[contract.contract_id] = baseline.extract(contract.text)
    return predictions, None


def run_llm(contracts, use_cache=True):
    extractor = LLMExtractor(use_cache=use_cache)
    predictions = {}
    stats = {
        "model": extractor.model,
        "effort": extractor.effort,
        "contracts": len(contracts),
        "chunks": 0,
        "api_calls_this_run": 0,
        "cached_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "quotes_returned": 0,
        "quotes_dropped": 0,
        "dropped_examples": [],
        "errors": [],
    }
    for number, contract in enumerate(contracts, start=1):
        started = time.time()
        result = extractor.extract(contract.text)
        predictions[contract.contract_id] = result.span_texts()

        stats["chunks"] += result.chunk_count
        stats["api_calls_this_run"] += result.api_calls
        stats["cached_calls"] += result.cached_calls
        stats["input_tokens"] += result.input_tokens
        stats["output_tokens"] += result.output_tokens
        stats["quotes_returned"] += result.quotes_returned
        stats["quotes_dropped"] += len(result.dropped_quotes)
        for clause_type, quote in result.dropped_quotes:
            stats["dropped_examples"].append(
                {"contract": contract.contract_id, "clause_type": clause_type, "quote": quote}
            )
        for error in result.errors:
            stats["errors"].append(f"{contract.contract_id}: {error}")

        seconds = time.time() - started
        print(
            f"  [{number}/{len(contracts)}] {contract.contract_id[:60]:<60} "
            f"chunks={result.chunk_count} new_calls={result.api_calls} "
            f"dropped={len(result.dropped_quotes)} errors={len(result.errors)} ({seconds:.0f}s)"
        )

    if stats["quotes_returned"] > 0:
        stats["hallucination_rate"] = stats["quotes_dropped"] / stats["quotes_returned"]
    else:
        stats["hallucination_rate"] = None
    stats["estimated_cost_usd"] = estimate_cost(
        stats["model"], stats["input_tokens"], stats["output_tokens"]
    )
    return predictions, stats


# ---------------------------------------------------------------- scoring

def score(contracts, predictions):
    """Return {clause_type or "All (micro)": {"contract": Counts, "span": Counts, "support": int}}."""
    scores = {}
    total = {"contract": Counts(), "span": Counts(), "support": 0, "gold_spans": 0}
    for clause_type in config.CLAUSE_TYPES:
        contract_counts = Counts()
        span_counts = Counts()
        support = 0
        gold_span_total = 0
        for contract in contracts:
            gold = contract.gold_spans[clause_type]
            predicted = predictions[contract.contract_id][clause_type]
            contract_counts.add(contract_level_counts(predicted, gold))
            span_counts.add(span_level_counts(predicted, gold))
            if gold:
                support += 1
            gold_span_total += len(gold)
        scores[clause_type] = {
            "contract": contract_counts,
            "span": span_counts,
            "support": support,
            "gold_spans": gold_span_total,
        }
        total["contract"].add(contract_counts)
        total["span"].add(span_counts)
        total["support"] += support
        total["gold_spans"] += gold_span_total
    scores["All (micro)"] = total
    return scores


def format_number(value):
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def build_rows(all_scores, contract_count):
    rows = []
    clause_names = list(config.CLAUSE_TYPES) + ["All (micro)"]
    for clause_type in clause_names:
        for approach, scores in all_scores.items():
            entry = scores[clause_type]
            contract_counts = entry["contract"]
            span_counts = entry["span"]
            # The "All" row counts (contract, clause type) pairs, not contracts.
            if clause_type == "All (micro)":
                possible = contract_count * len(config.CLAUSE_TYPES)
            else:
                possible = contract_count
            rows.append({
                "clause_type": clause_type,
                "approach": APPROACH_NAMES[approach],
                "contracts_with_clause": f"{entry['support']}/{possible}",
                "gold_spans": entry["gold_spans"],
                "contract_precision": format_number(precision(contract_counts)),
                "contract_recall": format_number(recall(contract_counts)),
                "contract_f1": format_number(f1(contract_counts)),
                "contract_tp_fp_fn_tn": f"{contract_counts.tp}/{contract_counts.fp}/{contract_counts.fn}/{contract_counts.tn}",
                "span_precision": format_number(precision(span_counts)),
                "span_recall": format_number(recall(span_counts)),
                "span_f1": format_number(f1(span_counts)),
            })
    return rows


# ---------------------------------------------------------------- failures

def shorten(text):
    text = " ".join(text.split())
    if len(text) > MAX_QUOTE_CHARS:
        return text[:MAX_QUOTE_CHARS] + " [...]"
    return text


def find_failures(contracts, predictions, clause_type):
    """Collect failure examples for one clause type, most serious first.

    Contract-level misses and false alarms come before span-level ones,
    alternating false negatives and false positives so both kinds appear.
    """
    contract_fn, contract_fp, span_fn, span_fp = [], [], [], []
    for contract in contracts:
        gold = contract.gold_spans[clause_type]
        predicted = predictions[contract.contract_id][clause_type]
        if gold and not predicted:
            contract_fn.append({
                "kind": "False negative: clause missed entirely (contract level)",
                "contract": contract.contract_id,
                "gold": gold,
                "predicted": [],
            })
        elif predicted and not gold:
            contract_fp.append({
                "kind": "False positive: clause reported but not in the gold labels (contract level)",
                "contract": contract.contract_id,
                "gold": [],
                "predicted": predicted,
            })
        elif gold and predicted:
            matches = match_spans(predicted, gold)
            matched_predicted = {match[0] for match in matches}
            matched_gold = {match[1] for match in matches}
            for gold_index, gold_text in enumerate(gold):
                if gold_index not in matched_gold:
                    best = max(predicted, key=lambda text: jaccard(text, gold_text))
                    span_fn.append({
                        "kind": "False negative: gold span not matched (span level)",
                        "contract": contract.contract_id,
                        "gold": [gold_text],
                        "predicted": [best],
                        "note": f"closest prediction has Jaccard {jaccard(best, gold_text):.2f}",
                    })
            for predicted_index, predicted_text in enumerate(predicted):
                if predicted_index not in matched_predicted:
                    span_fp.append({
                        "kind": "False positive: predicted span not matched (span level)",
                        "contract": contract.contract_id,
                        "gold": gold,
                        "predicted": [predicted_text],
                    })

    selected = []
    for group_a, group_b in [(contract_fn, contract_fp), (span_fn, span_fp)]:
        index = 0
        while len(selected) < FAILURES_PER_CLAUSE and (index < len(group_a) or index < len(group_b)):
            if index < len(group_a) and len(selected) < FAILURES_PER_CLAUSE:
                selected.append(group_a[index])
            if index < len(group_b) and len(selected) < FAILURES_PER_CLAUSE:
                selected.append(group_b[index])
            index += 1
    return selected


def write_failures(path, contracts, all_predictions):
    lines = [
        "# Failure examples for manual review",
        "",
        f"Up to {FAILURES_PER_CLAUSE} per clause type and approach. Contract-level "
        "misses are listed first because a missed clause is the most dangerous "
        "error in due diligence. Gold = CUAD lawyer labels.",
        "",
    ]
    for approach, predictions in all_predictions.items():
        lines.append(f"## {APPROACH_NAMES[approach]}")
        lines.append("")
        for clause_type in config.CLAUSE_TYPES:
            lines.append(f"### {clause_type}")
            lines.append("")
            failures = find_failures(contracts, predictions, clause_type)
            if not failures:
                lines.append("_No failures on this split._")
                lines.append("")
                continue
            for number, failure in enumerate(failures, start=1):
                lines.append(f"**{number}. {failure['kind']}**  ")
                lines.append(f"Contract: `{failure['contract']}`  ")
                if "note" in failure:
                    lines.append(f"Note: {failure['note']}  ")
                lines.append("")
                for gold_text in failure["gold"][:3]:
                    lines.append(f"- Gold: > {shorten(gold_text)}")
                if not failure["gold"]:
                    lines.append("- Gold: _(none)_")
                for predicted_text in failure["predicted"][:3]:
                    lines.append(f"- Predicted: > {shorten(predicted_text)}")
                if not failure["predicted"]:
                    lines.append("- Predicted: _(not found)_")
                lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- output

def write_results(out_dir, split, contracts, all_scores, llm_stats):
    rows = build_rows(all_scores, len(contracts))

    with open(out_dir / "results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    header = (
        "| Clause type | Approach | Contracts with clause | Contract P | Contract R | Contract F1 "
        "| TP/FP/FN/TN | Gold spans | Span P | Span R | Span F1 |"
    )
    lines = [
        f"# Results: {split} split, {len(contracts)} contracts",
        "",
        "Contract level = did it correctly say whether the clause exists. "
        "Span level = predicted text matches a gold span with token Jaccard >= 0.5 "
        "(one-to-one matching).",
        "",
        header,
        "|" + "---|" * 11,
    ]
    for row in rows:
        lines.append(
            f"| {row['clause_type']} | {row['approach']} | {row['contracts_with_clause']} "
            f"| {row['contract_precision']} | {row['contract_recall']} | {row['contract_f1']} "
            f"| {row['contract_tp_fp_fn_tn']} | {row['gold_spans']} "
            f"| {row['span_precision']} | {row['span_recall']} | {row['span_f1']} |"
        )

    if llm_stats is not None:
        rate = llm_stats["hallucination_rate"]
        rate_text = "n/a" if rate is None else f"{rate:.1%}"
        cost = llm_stats["estimated_cost_usd"]
        cost_text = "unknown (model not in price table)" if cost is None else f"${cost:.2f}"
        if config.is_local_model(llm_stats["model"]):
            tokens_note = ""
            cost_line = "- API cost: $0.00 (ran locally; electricity and hardware are not counted)"
        else:
            tokens_note = " (output includes the model's internal reasoning)"
            cost_line = (
                f"- Approximate API cost to produce these results: {cost_text} "
                "(list prices; re-runs from cache cost nothing)"
            )
        lines += [
            "",
            "## LLM run details",
            "",
            f"- Model: `{llm_stats['model']}` (effort: {llm_stats['effort']})",
            f"- Chunks sent: {llm_stats['chunks']} "
            f"({llm_stats['api_calls_this_run']} new model calls, {llm_stats['cached_calls']} from cache)",
            f"- Tokens: {llm_stats['input_tokens']:,} input, {llm_stats['output_tokens']:,} output"
            + tokens_note,
            cost_line,
            f"- Quotes returned by the model: {llm_stats['quotes_returned']}",
            f"- Quotes dropped because they could not be found in the contract text: "
            f"{llm_stats['quotes_dropped']}",
            f"- **Hallucination rate: {rate_text}** (dropped / returned)",
            f"- Errors: {len(llm_stats['errors'])}",
        ]
        for error in llm_stats["errors"][:20]:
            lines.append(f"  - {error}")

    (out_dir / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Evaluate clause extraction on CUAD.")
    parser.add_argument("--approach", choices=["baseline", "llm", "both"], default="both")
    parser.add_argument("--split", choices=["train", "dev", "test"], default="test")
    parser.add_argument("--limit", type=int, default=None,
                        help="only use the first N contracts (try 5 first)")
    parser.add_argument("--no-cache", action="store_true",
                        help="ignore the LLM response cache (costs money)")
    args = parser.parse_args()

    contracts = load_contracts(args.split, args.limit)
    folder_name = args.split if args.limit is None else f"{args.split}_first{args.limit}"
    # Local model results get their own folder so they don't overwrite Claude's.
    model_name = config.get_model_name()
    if args.approach != "baseline" and config.is_local_model(model_name):
        safe_model_name = model_name.replace(":", "-").replace("/", "-")
        folder_name = f"{folder_name}_{safe_model_name}"
    out_dir = config.RESULTS_DIR / folder_name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Evaluating on {len(contracts)} contracts from the {args.split} split -> {out_dir}")

    approaches = ["baseline", "llm"] if args.approach == "both" else [args.approach]
    all_predictions = {}
    all_scores = {}
    llm_stats = None
    for approach in approaches:
        print(f"\nRunning {APPROACH_NAMES[approach]}...")
        if approach == "baseline":
            predictions, _ = run_baseline(contracts)
        else:
            try:
                predictions, llm_stats = run_llm(contracts, use_cache=not args.no_cache)
            except CONFIGURATION_ERRORS as error:
                raise SystemExit(
                    f"\nLLM run stopped: {type(error).__name__}: {error}\n"
                    "For Claude, check ANTHROPIC_API_KEY in your .env file (see .env.example). "
                    "For a local model, check that Ollama is running and the model is pulled. "
                    "Also check CLAUSE_FINDER_MODEL. No results table was written."
                )
        all_predictions[approach] = predictions
        all_scores[approach] = score(contracts, predictions)
        with open(out_dir / f"predictions_{approach}.json", "w", encoding="utf-8") as file:
            json.dump(predictions, file, indent=2, ensure_ascii=False)

    if llm_stats is not None:
        with open(out_dir / "llm_stats.json", "w", encoding="utf-8") as file:
            json.dump(llm_stats, file, indent=2, ensure_ascii=False)

    report = write_results(out_dir, args.split, contracts, all_scores, llm_stats)
    write_failures(out_dir / "failures.md", contracts, all_predictions)
    print("\n" + report)
    print(f"\nWrote results.md, results.csv and failures.md to {out_dir}")


if __name__ == "__main__":
    main()
