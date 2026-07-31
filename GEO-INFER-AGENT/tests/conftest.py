"""Test fixtures for deterministic asyncio behavior under Python 3.12+."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def fresh_event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Give legacy unittest-style async tests an explicit isolated loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
