import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def separate_running_app():
    at = AppTest.from_file("app/pages/Separate.py")
    at.run(timeout=10)
    return at


@pytest.fixture
def karaoke_running_app():
    at = AppTest.from_file("app/pages/Karaoke.py")
    at.run(timeout=10)
    return at
