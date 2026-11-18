"""news-image-20261117 entry for lathixbt (account 4).

Renders nothing at run time: the entry image is a fixed, pre-rendered
front page ("Tuesday 17 November 2026 — The Day in World News", a map
poster with 33 verified stories across 6 continents) produced by the
bundled draw.py with PIL. This entrypoint only copies that image to the
harness output directory, deterministically, using the standard library.
"""

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    # Fail loudly instead of shipping a missing or truncated image.
    with open(src, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a valid PNG")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
