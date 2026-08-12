import json
from pathlib import Path

from prefect import flow, task
from prefect.tasks import task_input_hash


@task(
    retries=3,
    retry_delay_seconds=2,
    log_prints=True,
    # cache_key_fn=task_input_hash,
    # persist_result=True,
)
def process_betankande(file_path: str) -> dict:
    p = Path(file_path)
    print(f"Processing {p.name}")
    with open(p) as f:
        obj = json.load(f)
    referens = obj["dokumentstatus"]["dokreferens"]["referens"]
    referens_filtered = [
        r for r in referens if r["ref_dok_typ"] == "mot" or r["ref_dok_typ"] == "prop"
    ]

    ref_dok_ids = [r["ref_dok_id"] for r in referens_filtered]

    return {"file": p.name, "keys": referens_filtered, "ref_dok_ids": ref_dok_ids}


@task(log_prints=True)
def process_ref_dok_id(ref_dok_id: str) -> dict:
    print(f"Processing ref_dok_id: {ref_dok_id}")
    # TODO: fetch/process the referenced document
    return {"ref_dok_id": ref_dok_id}


_DATASETS_DIR = Path(__file__).parent / "datasets"


@flow(log_prints=True)
def process_betankande_flow(file_path: str):
    result = process_betankande(file_path)
    return process_ref_dok_id.map(result["ref_dok_ids"])


@flow(log_prints=True)
def betankande_pipeline(limit: int | None = None):
    json_files = sorted((_DATASETS_DIR / "betänkande").glob("*.json"))
    if limit:
        json_files = json_files[:limit]
    print(f"Found {len(json_files)} files")
    for p in json_files:
        process_betankande_flow(str(p))


if __name__ == "__main__":
    betankande_pipeline(limit=1)
