"""Pytest configuration and shared fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test.
    
    This fixture ensures test isolation by resetting the in-memory
    activities database to its original state before each test runs.
    """
    # Store the original state
    original_activities = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for name, activity in activities.items()
    }
    
    yield
    
    # Reset activities after each test
    for name, original_activity in original_activities.items():
        activities[name]["participants"] = original_activity["participants"].copy()


@pytest.fixture
def client(reset_activities):
    """Provide a TestClient for the FastAPI application.
    
    Depends on reset_activities to ensure fresh state for each test.
    """
    return TestClient(app)
