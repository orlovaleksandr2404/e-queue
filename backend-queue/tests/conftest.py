from datetime import datetime, timedelta, timezone

import pytest

from src.core.ws import manager


@pytest.fixture(autouse=True)
def _clear_ws_manager():
    manager.active.clear()
    yield
    manager.active.clear()


@pytest.fixture()
def dt():
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def _make(offset_sec: int = 0) -> datetime:
        return base + timedelta(seconds=offset_sec)

    return _make