from streamlit.testing.v1 import AppTest


def test_execution():
    at = AppTest.from_file("app/pages/separate.py")
    at.run()
    assert not at.exception
