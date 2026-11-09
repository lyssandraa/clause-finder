"""Streamlit app: upload a contract, run the LLM extractor, review the results.

Run with:
    streamlit run clause_finder/app.py
"""

import html
import io
import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this file as a script, so make the project importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clause_finder import config  # noqa: E402
from clause_finder.llm_extractor import LLMExtractor, estimate_cost  # noqa: E402

CONTEXT_CHARS = 400  # characters of surrounding text shown around each clause


def read_uploaded_file(uploaded_file):
    """Return the text of an uploaded .txt or .pdf file."""
    data = uploaded_file.getvalue()
    if uploaded_file.name.lower().endswith(".pdf"):
        import pdfplumber

        pages = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n\n".join(pages)
    return data.decode("utf-8", errors="replace")


def highlighted_excerpt(text, start, end):
    """HTML showing the clause highlighted inside a little surrounding context."""
    before_start = max(0, start - CONTEXT_CHARS)
    after_end = min(len(text), end + CONTEXT_CHARS)
    before = html.escape(text[before_start:start])
    clause = html.escape(text[start:end])
    after = html.escape(text[end:after_end])
    prefix = "... " if before_start > 0 else ""
    suffix = " ..." if after_end < len(text) else ""
    return (
        '<div style="white-space: pre-wrap; font-family: serif; line-height: 1.5; '
        'border: 1px solid #ddd; border-radius: 6px; padding: 12px; margin-bottom: 12px;">'
        f'<span style="color: #888;">{prefix}{before}</span>'
        f'<mark style="background-color: #fff176; color: #000; padding: 1px 0;">{clause}</mark>'
        f'<span style="color: #888;">{after}{suffix}</span>'
        "</div>"
    )


def main():
    st.set_page_config(page_title="clause-finder", layout="wide")
    st.title("clause-finder")
    st.caption(
        "Finds six M&A-relevant clause types in a commercial contract using an LLM. "
        "A first-pass review aid only: it misses clauses, and a lawyer must check every result."
    )

    if config.is_local_model(config.get_model_name()):
        st.info(
            f"**Local model:** the contract text is processed by `{config.get_model_name()}` "
            f"through Ollama at {config.get_ollama_url()}. Check that this address is on your "
            "own computer or network before uploading confidential documents."
        )
    else:
        st.warning(
            "**Confidentiality:** the contract text is sent to a third-party API "
            f"(Anthropic, model `{config.get_model_name()}`). Do not upload client documents "
            "unless your firm and client have approved this use and the terms of the API account "
            "(data retention, training use) are acceptable."
        )

    uploaded_file = st.file_uploader("Upload a contract (.pdf or .txt)", type=["pdf", "txt"])
    if uploaded_file is None:
        return

    text = read_uploaded_file(uploaded_file)
    if not text.strip():
        st.error(
            "No text could be extracted. If this is a scanned PDF it needs OCR first; "
            "this tool does not do OCR."
        )
        return
    st.write(f"Extracted {len(text):,} characters of text.")
    with st.expander("Show extracted text"):
        st.text(text[:20000] + ("\n\n[... truncated for display ...]" if len(text) > 20000 else ""))

    if not st.button("Find clauses", type="primary"):
        return

    with st.spinner("Asking the model (long contracts are split into several requests)..."):
        extractor = LLMExtractor()
        try:
            result = extractor.extract(text)
        except Exception as error:
            st.error(f"The API call failed: {type(error).__name__}: {error}")
            return

    # Summary table
    st.subheader("Summary")
    summary_rows = []
    for clause_type in config.CLAUSE_TYPES:
        count = len(result.spans[clause_type])
        summary_rows.append({
            "Clause type": clause_type,
            "Result": "Found" if count > 0 else "Not found",
            "Passages": count,
        })
    st.table(summary_rows)
    st.info(
        '"Not found" means the tool did not find the clause. It does **not** mean the '
        "contract has no such clause. In testing the tool missed some clauses that lawyers "
        "had labelled, so check the contract yourself."
    )

    cost = estimate_cost(extractor.model, result.input_tokens, result.output_tokens)
    details = (
        f"{result.chunk_count} chunk(s); {result.input_tokens:,} input / "
        f"{result.output_tokens:,} output tokens"
    )
    if cost is not None:
        details += f"; approx. cost ${cost:.3f}"
    if result.cached_calls:
        details += f" ({result.cached_calls} chunk(s) from cache, no charge)"
    st.caption(details)

    if result.dropped_quotes:
        st.warning(
            f"The model returned {len(result.dropped_quotes)} quote(s) that do not appear in "
            "the contract text. They were discarded and are listed at the bottom of the page."
        )
    for error in result.errors:
        st.error(error)

    # Each clause type with highlighted text
    st.subheader("Extracted clauses")
    for clause_type in config.CLAUSE_TYPES:
        spans = result.spans[clause_type]
        label = f"{clause_type}: {len(spans)} found" if spans else f"{clause_type}: not found"
        with st.expander(label, expanded=bool(spans)):
            st.caption(config.CLAUSE_DEFINITIONS[clause_type])
            if not spans:
                st.write("Nothing found. Review the contract manually.")
            for span in spans:
                st.markdown(highlighted_excerpt(text, span["start"], span["end"]),
                            unsafe_allow_html=True)

    if result.dropped_quotes:
        st.subheader("Discarded quotes (not found in the contract)")
        for clause_type, quote in result.dropped_quotes:
            st.markdown(f"**{clause_type}:**")
            st.text(quote)


# Streamlit runs this file with __name__ == "__main__"; the guard lets tests
# import the helper functions without rendering the page.
if __name__ == "__main__":
    main()
