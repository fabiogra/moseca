import pytest


def test_execution(separate_running_app):
    assert not separate_running_app.exception


@pytest.mark.parametrize(
    "selection",
    [
        "Vocals & Instrumental (Low Quality, Faster)",
        "Vocals & Instrumental (High Quality, Slower)",
        "Vocals, Drums, Bass & Other (Slower)",
        "Vocal, Drums, Bass, Guitar, Piano & Other (Slowest)",
    ],
)
def test_separation_mode(selection, separate_running_app):
    separate_running_app.selectbox(key="separation_mode").set_value(selection)
    assert separate_running_app.selectbox(key="separation_mode").value == selection
