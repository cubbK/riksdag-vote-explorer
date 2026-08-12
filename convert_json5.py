"""Convert JSON5 files in datasets/raw_json5 to standard JSON in datasets/raw."""

import json
import multiprocessing
import os
import re
from pathlib import Path

SRC = Path("datasets/raw_json5")
DST = Path("datasets/raw")
FOLDERS = ["betänkande", "motioner", "propositioner"]

# Matches /* ... */ block comments, including across newlines
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def convert_file(args: tuple[Path, Path]) -> str | None:
    src, dst = args
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    text = _BLOCK_COMMENT.sub("", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return f"ERROR {src.name}: {e}"
    dst.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return None


def main() -> None:
    pairs: list[tuple[Path, Path]] = []
    for folder in FOLDERS:
        files = list((SRC / folder).glob("*.json"))
        pairs.extend((f, DST / folder / f.name) for f in files)
        print(f"{folder}: {len(files)} files")

    with multiprocessing.Pool() as pool:
        results = pool.map(convert_file, pairs)

    errors = [r for r in results if r]
    for e in errors:
        print(e)
    print(
        f"\nDone: {len(pairs) - len(errors)}/{len(pairs)} converted, {len(errors)} errors"
    )


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
