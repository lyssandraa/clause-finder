"""Shared settings: clause types, file paths and environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CUAD_JSON_PATH = RAW_DIR / "CUAD_v1" / "CUAD_v1.json"
SPLIT_PATH = DATA_DIR / "splits.json"
CACHE_DIR = DATA_DIR / "cache" / "llm"
RESULTS_DIR = PROJECT_ROOT / "results"

# The six clause types this tool looks for.
# Key = the name we use everywhere in this project.
# Value = the category name used in the CUAD question IDs.
CLAUSE_TYPES = {
    "Change of Control": "Change Of Control",
    "Anti-Assignment": "Anti-Assignment",
    "Termination for Convenience": "Termination For Convenience",
    "Cap on Liability": "Cap On Liability",
    "Non-Compete": "Non-Compete",
    "Governing Law": "Governing Law",
}

# Definitions copied from the CUAD v1 datasheet, so the LLM is asked
# the same question the CUAD annotators were asked.
CLAUSE_DEFINITIONS = {
    "Change of Control": (
        "Does one party have the right to terminate or is consent or notice "
        "required of the counterparty if such party undergoes a change of "
        "control, such as a merger, stock sale, transfer of all or "
        "substantially all of its assets or business, or assignment by "
        "operation of law?"
    ),
    "Anti-Assignment": (
        "Is consent or notice required of a party if the contract is "
        "assigned to a third party?"
    ),
    "Termination for Convenience": (
        "Can a party terminate this contract without cause (solely by giving "
        "a notice and allowing a waiting period to expire)?"
    ),
    "Cap on Liability": (
        "Does the contract include a cap on liability upon the breach of a "
        "party's obligation? This includes time limitation for the "
        "counterparty to bring claims or maximum amount for recovery."
    ),
    "Non-Compete": (
        "Is there a restriction on the ability of a party to compete with "
        "the counterparty or operate in a certain geography or business or "
        "technology sector?"
    ),
    "Governing Law": (
        "Which state/country's law governs the interpretation of the contract?"
    ),
}

# Split sizes (by contract). Everything not in dev or test goes to train.
TEST_SIZE = 50
DEV_SIZE = 50
SPLIT_SEED = 42

# LLM settings, all overridable with environment variables (see .env.example).
DEFAULT_MODEL = "claude-opus-5-5"


def get_model_name():
    return os.environ.get("CLAUSE_FINDER_MODEL", DEFAULT_MODEL)


def get_effort():
    return os.environ.get("CLAUSE_FINDER_EFFORT", "medium")


def is_local_model(model_name):
    """Claude models use the Anthropic API; anything else runs through Ollama."""
    return not model_name.startswith("claude")


def get_ollama_url():
    return os.environ.get("OLLAMA_URL", "http://localhost:11434")


# Approximate prices in US dollars per million tokens (input, output).
# Used only for the cost estimate in the results table.
# Check https://www.anthropic.com/pricing before relying on these.
MODEL_PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
