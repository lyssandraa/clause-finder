"""Load CUAD and create a fixed train/dev/test split by contract.

Usage:
    python -m clause_finder.data            # download CUAD (if needed) and create the split
    python -m clause_finder.data --force    # re-create the split (changes your test set!)
"""

import argparse
import json
import random
from dataclasses import dataclass, field

from clause_finder import config


@dataclass
class Contract:
    contract_id: str  # the CUAD title, e.g. "LIMEENERGYCO_09_09_1999-EX-10-DISTRIBUTOR AGREEMENT"
    text: str
    # clause type -> list of gold (lawyer-labelled) text spans
    gold_spans: dict = field(default_factory=dict)


def download_cuad():
    """Download CUAD_v1.json from Hugging Face if it is not already on disk."""
    if config.CUAD_JSON_PATH.exists():
        return config.CUAD_JSON_PATH

    from huggingface_hub import hf_hub_download

    print("Downloading CUAD v1 from Hugging Face (theatticusproject/cuad)...")
    hf_hub_download(
        repo_id="theatticusproject/cuad",
        filename="CUAD_v1/CUAD_v1.json",
        repo_type="dataset",
        local_dir=str(config.RAW_DIR),
    )
    return config.CUAD_JSON_PATH


def load_all_contracts():
    """Read every contract in CUAD and its gold spans for our six clause types."""
    json_path = download_cuad()
    with open(json_path, encoding="utf-8") as file:
        cuad = json.load(file)

    # CUAD category name -> our clause type name
    cuad_name_to_ours = {}
    for our_name, cuad_name in config.CLAUSE_TYPES.items():
        cuad_name_to_ours[cuad_name] = our_name

    contracts = []
    for document in cuad["data"]:
        # Every CUAD document has exactly one "paragraph": the full contract text.
        paragraph = document["paragraphs"][0]
        contract = Contract(contract_id=document["title"], text=paragraph["context"])
        for clause_type in config.CLAUSE_TYPES:
            contract.gold_spans[clause_type] = []

        for question in paragraph["qas"]:
            cuad_category = question["id"].split("__")[-1]
            if cuad_category not in cuad_name_to_ours:
                continue
            our_name = cuad_name_to_ours[cuad_category]
            for answer in question["answers"]:
                span_text = answer["text"]
                if span_text not in contract.gold_spans[our_name]:
                    contract.gold_spans[our_name].append(span_text)

        contracts.append(contract)
    return contracts


def create_split(contracts, seed=config.SPLIT_SEED):
    """Randomly assign whole contracts to train / dev / test."""
    contract_ids = sorted(contract.contract_id for contract in contracts)
    random_generator = random.Random(seed)
    random_generator.shuffle(contract_ids)

    test_ids = sorted(contract_ids[: config.TEST_SIZE])
    dev_ids = sorted(contract_ids[config.TEST_SIZE: config.TEST_SIZE + config.DEV_SIZE])
    train_ids = sorted(contract_ids[config.TEST_SIZE + config.DEV_SIZE:])
    return {
        "seed": seed,
        "source": "theatticusproject/cuad, CUAD_v1/CUAD_v1.json",
        "train": train_ids,
        "dev": dev_ids,
        "test": test_ids,
    }


def save_split(split):
    config.SPLIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(config.SPLIT_PATH, "w", encoding="utf-8") as file:
        json.dump(split, file, indent=2)


def load_split_ids():
    """Read the saved split. Creates it on first use."""
    if not config.SPLIT_PATH.exists():
        split = create_split(load_all_contracts())
        save_split(split)
        return split
    with open(config.SPLIT_PATH, encoding="utf-8") as file:
        return json.load(file)


def load_contracts(split_name, limit=None):
    """Return the contracts in one split ("train", "dev" or "test").

    `limit` keeps only the first N contracts (in the saved order), which is
    handy for a quick, cheap check before a full run.
    """
    split = load_split_ids()
    wanted_ids = split[split_name]
    if limit is not None:
        wanted_ids = wanted_ids[:limit]

    contracts_by_id = {}
    for contract in load_all_contracts():
        contracts_by_id[contract.contract_id] = contract

    selected = []
    for contract_id in wanted_ids:
        selected.append(contracts_by_id[contract_id])
    return selected


def describe_split():
    """Print how many contracts in each split contain each clause type."""
    split = load_split_ids()
    contracts_by_id = {}
    for contract in load_all_contracts():
        contracts_by_id[contract.contract_id] = contract

    for split_name in ["train", "dev", "test"]:
        ids = split[split_name]
        print(f"\n{split_name}: {len(ids)} contracts")
        for clause_type in config.CLAUSE_TYPES:
            count = 0
            for contract_id in ids:
                if contracts_by_id[contract_id].gold_spans[clause_type]:
                    count += 1
            print(f"  {clause_type:<30} present in {count:>3}")


def main():
    parser = argparse.ArgumentParser(description="Download CUAD and create the split.")
    parser.add_argument("--force", action="store_true", help="re-create the split file")
    args = parser.parse_args()

    if args.force or not config.SPLIT_PATH.exists():
        split = create_split(load_all_contracts())
        save_split(split)
        print(f"Saved split to {config.SPLIT_PATH}")
    else:
        print(f"Split already exists at {config.SPLIT_PATH} (use --force to re-create)")
    describe_split()


if __name__ == "__main__":
    main()
