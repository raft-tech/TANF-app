"""Sets an env variable to indicate that we are running tests. This is used to run custom migrations during testing."""
import os

def pytest_sessionstart(session):
    """Set PYTEST env variable to indicate that we are running tests."""
    os.environ['PYTEST'] = 'True'
