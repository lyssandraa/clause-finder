# clause-finder

A contract review aid that finds six M&A-relevant clause types in commercial contracts. It measures its own accuracy against clauses labelled by lawyers.

| Clause type | Why it matters in M&A due diligence |
|---|---|
| Change of Control | The deal itself may trigger termination or consent rights |
| Anti-Assignment | The contract may not transfer to the buyer without consent |
| Termination for Convenience | The counterparty can walk away regardless of the deal |
| Cap on Liability | Limits what can be recovered for breach |
| Non-Compete | May restrict the combined business after closing |
| Governing Law | Determines which law, and often which courts, apply |

The project compares two approaches:

1. **Baseline:** hand-written keyword and regex rules that return matching sentences.
2. **LLM:** a language model reads the contract in overlapping chunks and returns exact quotes. The code checks every quote against the source text and discards any quote it cannot find. Those are reported as a hallucination rate. The reported results use **Qwen 3 8B running locally** through Ollama, so no contract text left the machine. The code also supports Claude through the Anthropic API, but Claude has not been evaluated here.

> **This is a first-pass aid, not a reviewer.** It misses clauses. Every output must be checked by a lawyer. See [Limitations and legal risks](#limitations-and-legal-risks).

---

## Data

- **Source:** [CUAD v1](https://www.atticusprojectai.org/cuad) (Contract Understanding Atticus Dataset), from Hugging Face [`theatticusproject/cuad`](https://huggingface.co/datasets/theatticusproject/cuad). The code uses the file `CUAD_v1/CUAD_v1.json`. It contains 510 commercial contracts from SEC EDGAR filings, labelled by law students and checked by experienced lawyers across 41 clause categories. This project uses 6 of them.
  - The `theatticusproject/cuad-qa` repository holds only a loading script, which current versions of the `datasets` library no longer run. So the code downloads the official JSON release directly.
- **Licence:** CUAD is released under **Creative Commons Attribution 4.0 (CC BY 4.0)**, free for commercial and non-commercial use with attribution. Per the CUAD README, The Atticus Project makes no representations about the licence status of the underlying contracts, which are public EDGAR filings.
  - Citation: Hendrycks, Burns, Chen and Ball, *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review*, NeurIPS 2021.
- **Split:** fixed and **by contract**, so no contract appears in more than one split. The split is a seeded shuffle (seed 42), saved to [data/splits.json](data/splits.json):

| Split | Contracts | Use |
|---|---|---|
| train | 410 | not used yet (available for few-shot examples or training) |
| dev | 50 | used to tune the baseline regex rules |
| test | 50 | used only for the reported results |

How many test contracts contain each clause: Change of Control 14, Anti-Assignment 37, Termination for Convenience 19, Cap on Liability 28, Non-Compete 15, Governing Law 44.

**Small numbers warning:** with only 14–15 positive contracts for Change of Control and Non-Compete, one more hit or miss moves recall by about 7 points. Treat differences of a few points as noise.

---

## How it works

### Baseline ([clause_finder/baseline.py](clause_finder/baseline.py))
The baseline splits the contract into rough sentences and returns every sentence that matches a clause type's rule. A rule is a set of regex groups, for example: contains "assign" **and** "without … consent". No match means "not found". The rules were adjusted on the **dev** split only.

### LLM ([clause_finder/llm_extractor.py](clause_finder/llm_extractor.py))
1. **Chunking:** the contract is split into ~20,000-character chunks (about 5,000 tokens) with 2,000 characters of overlap. That way a clause on a chunk boundary still appears whole in one chunk.
2. **Prompt:** for each chunk, the model receives CUAD's own definition of each clause type and must return JSON shaped like `{clause_type: [exact quotes]}`. The API's structured-output mode enforces this shape. The prompt requires character-for-character quotes and empty lists when a clause isn't there.
3. **Validation:** every quote is located in the chunk, either exactly, ignoring whitespace and case, or by fuzzy match (rapidfuzz `partial_ratio` ≥ 90, quotes of 3+ words only). Quotes that can't be found are **dropped and counted**. The output always shows the contract's own text, never the model's version of it.
4. **Merging:** quotes from all chunks are mapped to positions in the full contract. A quote is dropped as a duplicate if at least 80% of it lies inside a longer quote, which handles repeats from overlapping chunks.
5. **Caching:** each API response is saved under `data/cache/llm/`. The cache key covers model, effort, prompt version and chunk text, so re-runs cost nothing.

Settings come from environment variables (see [.env.example](.env.example)):
- `CLAUSE_FINDER_MODEL` (default `claude-opus-5-5`)
- `CLAUSE_FINDER_EFFORT` (default `medium`)

For models that support it, the API's server-side refusal fallback is enabled. If the model declines a request, the API retries it on another model instead of returning nothing.

---

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env              # then put your Anthropic API key in .env

python -m clause_finder.data      # downloads CUAD (~40 MB) and prints split statistics

# 1. Check everything works on 5 contracts first (~17 API calls, roughly $1-2)
python -m clause_finder.evaluate --approach both --limit 5

# 2. Full test set: 50 contracts, ~188 API calls, roughly $10-15 with claude-opus-5-5
python -m clause_finder.evaluate --approach both

# Baseline only (free, no API key needed)
python -m clause_finder.evaluate --approach baseline --split test

# Web app: upload a PDF or .txt contract
streamlit run clause_finder/app.py

# Tests (no network or API key needed; the LLM is replaced by a fake client)
pytest
```

The cost figures are estimates from token counts at list price. The actual cost of each run is printed in `results.md`.

### Running with a local model (Qwen through Ollama)

Any model name that doesn't start with `claude` runs on your own computer through [Ollama](https://ollama.com). It needs no API key, and contract text doesn't leave the machine.

```powershell
ollama pull qwen3:8b
$env:CLAUSE_FINDER_MODEL = "qwen3:8b"
python -m clause_finder.evaluate --approach llm --limit 5
python -m clause_finder.evaluate --approach both
```

Results go to a separate folder such as `results/test_qwen3-8b/`. The context window is set to 16,384 tokens because Ollama's default is small and would silently cut off long chunks. If a prompt still fills the window, the chunk is reported as an error in the results. Results from a small local model aren't comparable to Claude's unless both are run on the same split.

### Results website

`python -m clause_finder.build_site` turns the saved results into one static page, [docs/index.html](docs/index.html). It explains the method and lets visitors compare each approach's answers with the lawyers' labels, without running a model. The script recomputes the metrics from the saved predictions and stops if they disagree with `results.csv`. To host it on GitHub Pages, publish the `docs/` folder from the repository settings.

Each evaluation writes to `results/<split>/` (or `results/<split>_first<N>/`):
- `results.md` and `results.csv`: the metrics table
- `failures.md`: up to 5 failures per clause type and approach, for manual review
- `predictions_<approach>.json`: every predicted span
- `llm_stats.json`: tokens, cost, dropped quotes and errors

---

## Results

### How the scoring works
- **Contract level:** did the tool correctly say whether the clause **exists** in the contract? This is the question that matters most in due diligence.
- **Span level:** does the extracted text match the lawyer-labelled text? A predicted span matches a gold span if their word overlap (token Jaccard) is **≥ 0.5**. Matching is one-to-one, so one prediction can't claim two gold spans.
- **Strictness of the span score:** CUAD labels are often a fragment of a sentence. A system that returns the whole sentence, or the whole numbered clause, can be useful to a reader and still fail the 0.5 threshold. The span scores are therefore a harsh measure.
- **"All (micro)"** pools the counts across all six clause types.

### Test set (50 contracts)

| Clause type | Approach | Contracts with clause | Contract P | Contract R | Contract F1 | Span P | Span R | Span F1 |
|---|---|---|---|---|---|---|---|---|
| Change of Control | Regex | 14/50 | 0.65 | 0.93 | **0.76** | 0.28 | 0.71 | **0.40** |
| | Qwen 3 8B | | 0.45 | 0.93 | 0.60 | 0.24 | 0.45 | 0.31 |
| Anti-Assignment | Regex | 37/50 | 0.97 | 0.97 | **0.97** | 0.69 | 0.63 | **0.66** |
| | Qwen 3 8B | | 1.00 | 0.92 | 0.96 | 0.56 | 0.52 | 0.54 |
| Termination for Convenience | Regex | 19/50 | 0.65 | 0.79 | **0.71** | 0.23 | 0.52 | 0.32 |
| | Qwen 3 8B | | 0.62 | 0.68 | 0.65 | 0.46 | 0.42 | **0.44** |
| Cap on Liability | Regex | 28/50 | 0.80 | 0.86 | 0.83 | 0.34 | 0.48 | 0.40 |
| | Qwen 3 8B | | 0.82 | 1.00 | **0.90** | 0.33 | 0.67 | **0.44** |
| Non-Compete | Regex | 15/50 | 0.62 | 0.67 | 0.65 | 0.27 | 0.23 | 0.25 |
| | Qwen 3 8B | | 0.72 | 0.87 | **0.79** | 0.33 | 0.35 | **0.34** |
| Governing Law | Regex | 44/50 | 1.00 | 0.95 | **0.98** | 0.94 | 0.94 | **0.94** |
| | Qwen 3 8B | | 0.98 | 0.93 | 0.95 | 0.56 | 0.85 | 0.68 |
| **All (micro)** | Regex | 157/300 | 0.83 | 0.89 | **0.86** | 0.43 | 0.59 | **0.50** |
| | Qwen 3 8B | | 0.80 | 0.90 | 0.85 | 0.41 | 0.56 | 0.47 |

Bold marks the higher F1 for that row pair.

**Qwen run details:** model `qwen3:8b` through Ollama, run on one consumer PC (RTX 2080, 8 GB). 188 chunks, 859,824 input tokens and 33,799 output tokens, no API cost, no errors. The model returned 394 quotes, and 15 could not be found in the contract, a **hallucination rate of 3.8%**. Several of those look like standard boilerplate that the contract doesn't contain, such as a generic New York governing-law clause. Those are the errors the validation step exists to catch. The full outputs are in [results/test_qwen3-8b/](results/test_qwen3-8b/).

**What the numbers say:**
- **Overall, the small local model did not beat the regex rules.** Contract-level F1 is 0.85 against 0.86, which is effectively a tie on this sample. I expected the model to win, and on this evidence it does not.
- **Each approach is better at different clauses.** Qwen is ahead on Cap on Liability (0.90 against 0.83) and Non-Compete (0.79 against 0.65). Regex is ahead on Change of Control (0.76 against 0.60) and Termination for Convenience (0.71 against 0.65).
- **Change of Control is Qwen's weakest result:** 16 false alarms against 13 correct finds.
- **Fixed wording is easy for rules.** Governing Law and Anti-Assignment reach F1 ≥ 0.97 for regex. Qwen finds these too, but its Governing Law text match is much lower (0.68 against 0.94) because it returns extra passages.
- **Differences of a few points are not meaningful here.** Most clause types have only 14–44 positive contracts.
- **These results describe one small model.** They say nothing about how a larger model such as Claude would score, and that comparison has not been run.

**How the prompt was developed:** the prompt was revised once, using errors on the first 15 dev contracts. Contract-level F1 on those contracts rose from 0.83 to 0.87. The first 5 test contracts had been viewed under the original prompt before that revision, including a Termination for Convenience false-alarm pattern that also appeared on dev. The wording changes were based on the dev errors, but the test set was not completely unseen. Neither the prompt nor the regex rules were changed after the full test run.

---

## Limitations and legal risks

**1. Missed clauses (false negatives) are the most dangerous error.**
In due diligence, a missed change-of-control or anti-assignment clause can mean the buyer loses a key contract at closing, and nobody flagged it. The tool *will* miss clauses. On the test set, the regex baseline fails to flag 11% of contracts where a clause is present (a third for Non-Compete), and Qwen fails to flag 10% (about a third for Termination for Convenience). "Not found" must never be read as "not present". The tool can help a reviewer find clauses faster. It cannot confirm that a clause is absent.

**2. Hallucinated text.**
LLMs can produce text that looks like a quote but isn't in the document, or that subtly changes it (for example, dropping "not", or changing an amount). This tool checks every quote against the source and discards ones it cannot find. It also always displays the contract's own wording, not the model's. The discarded share is reported as the hallucination rate. Two limits remain:
- The fuzzy match (≥ 90% similarity) could accept a quote that differs in a small but legally important word. Because the displayed text comes from the contract, the reader sees the real wording. Even so, a reviewer should read the clause in context.
- Validation proves the text exists. It does not prove the text is the right clause type.

**3. Confidentiality of client documents.**
With a Claude model, the LLM approach sends the full contract text to a third-party API (Anthropic). With a local model through Ollama, as in the reported results, the text stays on the machine running Ollama, which is a real advantage for confidential documents, though the machine itself still needs appropriate security. Before using the API option on client documents:
- confirm that the client's engagement terms and your firm's policies allow it;
- check the API provider's data retention and training-use terms for your account;
- consider whether information barriers, regulatory duties (for example, SRA rules in England and Wales) or NDAs restrict sharing.

All evaluation in this project uses public EDGAR contracts from CUAD. The rule-based baseline runs entirely locally.

**4. A lawyer must always review the output.**
The tool doesn't interpret clauses. It doesn't decide whether a change-of-control clause is actually triggered by a particular deal structure, whether a cap carves out fraud or IP indemnities, or how an exception changes a restriction. Those questions need legal judgement and the whole contract.

**5. Other limitations.**
- **Narrow, US-centric data:** CUAD contracts are US public-company filings, mostly from the 1990s to 2010s. Accuracy on other contracts (English-law, private M&A documents, other languages) is unknown and probably lower.
- **Scanned PDFs:** the app reads PDFs with pdfplumber, which cannot read scanned PDFs (there's no OCR). Tables, columns and headers can garble the extracted text.
- **Imperfect labels:** CUAD's annotators sometimes disagree on where a clause starts and ends. Some "errors" in `failures.md` are arguably labelling choices.
- **Small test set:** 50 contracts, and 14–15 positives for two clause types, so the scores carry wide uncertainty.
- **Not reproducible across models:** LLM results depend on the model version. Changing `CLAUSE_FINDER_MODEL` produces new, uncached results.
- **Approximate costs:** cost estimates use a hard-coded list-price table in [clause_finder/config.py](clause_finder/config.py), so check current pricing.

---

## Project structure

```
clause_finder/
  config.py          clause types, CUAD definitions, paths, model settings
  data.py            download CUAD, build and save the train/dev/test split
  text_utils.py      tokenising, Jaccard, span location (exact/fuzzy), sentence split, chunking
  baseline.py        regex rules
  llm_extractor.py   chunking, prompt, API call, cache, JSON parsing, validation, merging
  metrics.py         precision / recall / F1, contract-level and span-level matching
  evaluate.py        command-line evaluation, results tables, failure examples
  app.py             Streamlit app
  build_site.py      generates the static results page from saved results
  site_template.html page layout, styles and charts for that page
docs/index.html      the generated results page
tests/               pytest suite: span matching, metrics, JSON parsing, LLM pipeline (fake client), baseline
data/splits.json     the fixed split (committed, so results are reproducible)
```
