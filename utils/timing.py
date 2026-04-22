from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timed(label: str) -> Iterator[None]:
    t0 = time.time()
    try:
        yield
    finally:
        dt = time.time() - t0
        print(f"⏱️ {label}: {dt:.2f}s")

