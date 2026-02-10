import pytest
from flask_jwt_extended import JWTManager

pytest_plugins = ['pytest_flask']

@pytest.fixture(scope='session')
def _jwt_manager():
    """Fixture to provide JWT manager for tests"""
    return JWTManager()
