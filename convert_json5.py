"""Convert JSONC/JSON5 files in datasets/raw_json5 to plain JSON for DuckDB."""

import json5
import orjson
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

SRC_DIR = Path(__file__).parent / "datasets" / "raw_json5"
DST_DIR = Path(__file__).parent / "datasets" / "json"


def convert_file(args: tuple[Path, Path]) -> tuple[Path, str | None]:
    src, dst = args
    try:
        data = json5.loads(src.read_text(encoding="utf-8"))
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(orjson.dumps(data))
        return src, None
    except Exception as exc:
        return src, str(exc)


def collect_tasks(src_dir: Path, dst_dir: Path) -> list[tuple[Path, Path]]:
    tasks = []
    for src in src_dir.rglob("*.json"):
        rel = src.relative_to(src_dir)
        tasks.append((src, dst_dir / rel))
    return tasks


def main() -> None:
    tasks = collect_tasks(SRC_DIR, DST_DIR)
    if not tasks:
        print("No .json files found in", SRC_DIR)
        return

    workers = os.cpu_count() or 4
    errors: list[tuple[Path, str]] = []
    done = 0

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(convert_file, t): t for t in tasks}
        for fut in as_completed(futures):
            src, err = fut.result()
            if err:
                errors.append((src, err))
            done += 1
            if done % 500 == 0:
                print(f"  {done}/{len(tasks)}", flush=True)

    print(f"Converted {done - len(errors)}/{len(tasks)} files to {DST_DIR}")
    for path, msg in errors:
        print(f"  ERROR {path}: {msg}", file=sys.stderr)


if __name__ == "__main__":
    main()
