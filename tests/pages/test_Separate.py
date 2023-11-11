from streamlit.testing.v1 import AppTest


def test_execution():
    at = AppTest.from_file("app/pages/Separate.py")
    at.run(timeout=10)
    assert not at.exception
