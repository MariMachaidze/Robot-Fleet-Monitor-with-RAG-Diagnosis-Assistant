"""Shared fixtures: each test gets a fresh service backed by its own temporary SQLite file."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from erp_mock.main import create_app as create_erp_app
from fleet_api.main import create_app as create_fleet_app


@pytest.fixture
def fleet_client(tmp_path) -> Iterator[TestClient]:
    # The "with" block runs the app's lifespan, which creates and seeds the database.
    with TestClient(create_fleet_app(str(tmp_path / "fleet.db"))) as client:
        yield client


@pytest.fixture
def erp_client(tmp_path) -> Iterator[TestClient]:
    with TestClient(create_erp_app(str(tmp_path / "erp.db"))) as client:
        yield client
