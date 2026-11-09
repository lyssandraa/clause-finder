# Results: test split, 50 contracts

Contract level = did it correctly say whether the clause exists. Span level = predicted text matches a gold span with token Jaccard >= 0.5 (one-to-one matching).

| Clause type | Approach | Contracts with clause | Contract P | Contract R | Contract F1 | TP/FP/FN/TN | Gold spans | Span P | Span R | Span F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Change of Control | Baseline (regex) | 14/50 | 0.65 | 0.93 | 0.76 | 13/7/1/29 | 31 | 0.28 | 0.71 | 0.40 |
| Change of Control | LLM | 14/50 | 0.45 | 0.93 | 0.60 | 13/16/1/20 | 31 | 0.24 | 0.45 | 0.31 |
| Anti-Assignment | Baseline (regex) | 37/50 | 0.97 | 0.97 | 0.97 | 36/1/1/12 | 67 | 0.69 | 0.63 | 0.66 |
| Anti-Assignment | LLM | 37/50 | 1.00 | 0.92 | 0.96 | 34/0/3/13 | 67 | 0.56 | 0.52 | 0.54 |
| Termination for Convenience | Baseline (regex) | 19/50 | 0.65 | 0.79 | 0.71 | 15/8/4/23 | 31 | 0.23 | 0.52 | 0.32 |
| Termination for Convenience | LLM | 19/50 | 0.62 | 0.68 | 0.65 | 13/8/6/23 | 31 | 0.46 | 0.42 | 0.44 |
| Cap on Liability | Baseline (regex) | 28/50 | 0.80 | 0.86 | 0.83 | 24/6/4/16 | 48 | 0.34 | 0.48 | 0.40 |
| Cap on Liability | LLM | 28/50 | 0.82 | 1.00 | 0.90 | 28/6/0/16 | 48 | 0.33 | 0.67 | 0.44 |
| Non-Compete | Baseline (regex) | 15/50 | 0.62 | 0.67 | 0.65 | 10/6/5/29 | 43 | 0.27 | 0.23 | 0.25 |
| Non-Compete | LLM | 15/50 | 0.72 | 0.87 | 0.79 | 13/5/2/30 | 43 | 0.33 | 0.35 | 0.34 |
| Governing Law | Baseline (regex) | 44/50 | 1.00 | 0.95 | 0.98 | 42/0/2/6 | 47 | 0.94 | 0.94 | 0.94 |
| Governing Law | LLM | 44/50 | 0.98 | 0.93 | 0.95 | 41/1/3/5 | 47 | 0.56 | 0.85 | 0.68 |
| All (micro) | Baseline (regex) | 157/300 | 0.83 | 0.89 | 0.86 | 140/28/17/115 | 267 | 0.43 | 0.59 | 0.50 |
| All (micro) | LLM | 157/300 | 0.80 | 0.90 | 0.85 | 142/36/15/107 | 267 | 0.41 | 0.56 | 0.47 |

## LLM run details

- Model: `qwen3:8b` (effort: medium)
- Chunks sent: 188 (188 new model calls, 0 from cache)
- Tokens: 859,824 input, 33,799 output
- API cost: $0.00 (ran locally; electricity and hardware are not counted)
- Quotes returned by the model: 394
- Quotes dropped because they could not be found in the contract text: 15
- **Hallucination rate: 3.8%** (dropped / returned)
- Errors: 0
