"""Tests for JSON parsing and the LLM pipeline, using a fake API client (no network)."""

import json
from types import SimpleNamespace

import pytest

from clause_finder import config, llm_extractor
from clause_finder.llm_extractor import (
    LLMExtractor,
    estimate_cost,
    parse_model_json,
    remove_duplicate_spans,
)


# ---------------------------------------------------------------- parse_model_json

def test_parse_plain_json():
    text = json.dumps({"Governing Law": ["governed by Delaware law"], "Non-Compete": []})
    result = parse_model_json(text)
    assert result["Governing Law"] == ["governed by Delaware law"]
    assert result["Non-Compete"] == []


def test_parse_fills_missing_clause_types():
    result = parse_model_json('{"Governing Law": []}')
    assert set(result) == set(config.CLAUSE_TYPES)
    for quotes in result.values():
        assert quotes == []


def test_parse_strips_code_fence_and_surrounding_text():
    text = 'Here you go:\n```json\n{"Anti-Assignment": ["may not assign"]}\n```\nDone.'
    assert parse_model_json(text)["Anti-Assignment"] == ["may not assign"]


def test_parse_keys_are_case_insensitive():
    result = parse_model_json('{"governing law": ["laws of Texas"]}')
    assert result["Governing Law"] == ["laws of Texas"]


def test_parse_ignores_bad_values():
    text = json.dumps({
        "Governing Law": "a single string",  # accepted as a one-item list
        "Non-Compete": None,  # wrong type -> empty
        "Cap on Liability": ["ok", "", 42, "   "],  # only real strings kept
        "Unknown Clause": ["ignored"],
    })
    result = parse_model_json(text)
    assert result["Governing Law"] == ["a single string"]
    assert result["Non-Compete"] == []
    assert result["Cap on Liability"] == ["ok"]
    assert "Unknown Clause" not in result


@pytest.mark.parametrize("bad_text", ["", "no json here", "[1, 2, 3]", '{"Governing Law": [}'])
def test_parse_raises_on_unreadable_responses(bad_text):
    with pytest.raises(ValueError):
        parse_model_json(bad_text)


# ---------------------------------------------------------------- de-duplication

def test_remove_duplicate_spans():
    spans = [(0, 100), (10, 60), (0, 100), (200, 250), (90, 150)]
    # (10, 60) is inside (0, 100); the exact repeat is removed;
    # (90, 150) only overlaps 10 of its 60 characters, so it is kept.
    assert remove_duplicate_spans(spans) == [(0, 100), (90, 150), (200, 250)]


def test_estimate_cost_known_and_unknown_model():
    assert estimate_cost("claude-opus-5-5", 1_000_000, 100_000) == pytest.approx(4.0 + 2.0)
    assert estimate_cost("claude-unknown-model", 1000, 1000) is None
    assert estimate_cost("qwen3:8b", 1_000_000, 100_000) == 0.0


# ---------------------------------------------------------------- full pipeline with a fake client

class FakeMessages:
    """Stands in for client.messages / client.beta.messages."""

    def __init__(self, answer_for_chunk):
        self.answer_for_chunk = answer_for_chunk
        self.calls = 0

    def create(self, **request):
        self.calls += 1
        user_message = request["messages"][0]["content"]
        answer = self.answer_for_chunk(user_message)
        return SimpleNamespace(
            model=request["model"],
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text=json.dumps(answer))],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200),
        )


class FakeClient:
    def __init__(self, answer_for_chunk):
        self.messages = FakeMessages(answer_for_chunk)
        self.beta = SimpleNamespace(messages=self.messages)


GOVERNING_LAW = "This Agreement shall be governed by the laws of the State of Delaware."
ASSIGNMENT = "Neither party may assign this Agreement without the other party's consent."


def make_contract():
    filler = "The parties agree to cooperate in good faith on all matters. " * 400
    return filler + GOVERNING_LAW + "\n" + filler + ASSIGNMENT + "\n" + filler


def fake_answer(user_message):
    answer = {clause_type: [] for clause_type in config.CLAUSE_TYPES}
    if GOVERNING_LAW in user_message:
        # Quote with collapsed spacing and lower case - should still be accepted.
        answer["Governing Law"] = [GOVERNING_LAW.lower()]
    if ASSIGNMENT in user_message:
        answer["Anti-Assignment"] = [ASSIGNMENT]
    # A hallucinated quote in every chunk: not in the contract, must be dropped.
    answer["Change of Control"] = ["Upon a change of control, either party may terminate immediately."]
    return answer


def test_pipeline_validates_merges_and_counts(tmp_path):
    client = FakeClient(fake_answer)
    extractor = LLMExtractor(client=client, model="claude-opus-5-5", effort="low",
                             cache_dir=tmp_path, parallel_requests=1)
    contract = make_contract()
    result = extractor.extract(contract)

    assert result.chunk_count > 1
    assert result.api_calls == result.chunk_count
    assert result.errors == []

    # Real quotes found once each, with original text and correct offsets.
    texts = result.span_texts()
    assert texts["Governing Law"] == [GOVERNING_LAW]
    assert texts["Anti-Assignment"] == [ASSIGNMENT]
    for span in result.spans["Governing Law"]:
        assert contract[span["start"]:span["end"]] == span["text"]

    # Hallucinated quotes are dropped and counted, one per chunk.
    assert texts["Change of Control"] == []
    assert len(result.dropped_quotes) == result.chunk_count
    assert result.quotes_returned >= result.chunk_count + 2


def test_pipeline_uses_disk_cache(tmp_path):
    contract = make_contract()
    first_client = FakeClient(fake_answer)
    LLMExtractor(client=first_client, model="claude-opus-5-5", effort="low",
                 cache_dir=tmp_path, parallel_requests=1).extract(contract)
    assert first_client.messages.calls > 0

    second_client = FakeClient(fake_answer)
    result = LLMExtractor(client=second_client, model="claude-opus-5-5", effort="low",
                          cache_dir=tmp_path, parallel_requests=1).extract(contract)
    assert second_client.messages.calls == 0
    assert result.cached_calls == result.chunk_count
    assert result.span_texts()["Governing Law"] == [GOVERNING_LAW]


def test_pipeline_records_unparseable_response(tmp_path):
    class BrokenMessages(FakeMessages):
        def create(self, **request):
            response = super().create(**request)
            response.content = [SimpleNamespace(type="text", text="sorry, no JSON")]
            return response

    client = FakeClient(fake_answer)
    client.messages = BrokenMessages(fake_answer)
    client.beta = SimpleNamespace(messages=client.messages)
    result = LLMExtractor(client=client, model="claude-opus-5-5", effort="low",
                          cache_dir=tmp_path, parallel_requests=1).extract("short contract text")
    assert len(result.errors) == 1
    assert "No JSON object" in result.errors[0]


# ---------------------------------------------------------------- local model (Ollama), faked

class FakeOllamaResponse:
    def __init__(self, data, status_code=200, text=""):
        self.data = data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


def ollama_reply(content, done_reason="stop", prompt_tokens=1000):
    return FakeOllamaResponse({
        "message": {"content": content},
        "done_reason": done_reason,
        "prompt_eval_count": prompt_tokens,
        "eval_count": 50,
    })


def make_local_extractor(tmp_path):
    return LLMExtractor(model="qwen3:8b", effort="low", cache_dir=tmp_path)


def test_ollama_request_and_quote_validation(tmp_path, monkeypatch):
    sent = {}

    def fake_post(url, json, timeout):
        sent["url"] = url
        sent["payload"] = json
        return ollama_reply('{"Governing Law": ["' + GOVERNING_LAW + '", "Invented sentence about Mars law."]}')

    monkeypatch.setattr(llm_extractor.requests, "post", fake_post)
    extractor = make_local_extractor(tmp_path)
    assert extractor.parallel_requests == 1

    result = extractor.extract(GOVERNING_LAW)

    assert sent["url"].endswith("/api/chat")
    assert sent["payload"]["options"]["num_ctx"] == llm_extractor.OLLAMA_CONTEXT_TOKENS
    assert sent["payload"]["format"]["required"] == list(config.CLAUSE_TYPES)
    assert result.span_texts()["Governing Law"] == [GOVERNING_LAW]
    assert len(result.dropped_quotes) == 1
    assert result.errors == []
    assert list(tmp_path.iterdir())  # a complete answer is cached


def test_ollama_truncated_input_is_reported_and_not_cached(tmp_path, monkeypatch):
    def fake_post(url, json, timeout):
        return ollama_reply("{}", prompt_tokens=llm_extractor.OLLAMA_CONTEXT_TOKENS)

    monkeypatch.setattr(llm_extractor.requests, "post", fake_post)
    result = make_local_extractor(tmp_path).extract("short contract text")
    assert "context_overflow" in result.errors[0]
    assert not list(tmp_path.iterdir())


def test_ollama_not_running_stops_the_run(tmp_path, monkeypatch):
    def fake_post(url, json, timeout):
        raise llm_extractor.requests.ConnectionError("refused")

    monkeypatch.setattr(llm_extractor.requests, "post", fake_post)
    with pytest.raises(llm_extractor.LocalModelSetupError):
        make_local_extractor(tmp_path).extract("short contract text")


def test_ollama_missing_model_stops_the_run(tmp_path, monkeypatch):
    def fake_post(url, json, timeout):
        return FakeOllamaResponse({}, status_code=404, text="model not found")

    monkeypatch.setattr(llm_extractor.requests, "post", fake_post)
    with pytest.raises(llm_extractor.LocalModelSetupError, match="ollama pull"):
        make_local_extractor(tmp_path).extract("short contract text")
