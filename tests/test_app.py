from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

@pytest.mark.parametrize('mode', ['Regole di disponibilità', 'Comitato ML dimostrativo'])
def test_demo_generates_without_errors(mode):
    root=Path(__file__).resolve().parents[1]
    app=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    assert not app.exception
    app.selectbox(key='data_source').set_value('Laboratorio dimostrativo').run()
    app.radio[0].set_value(mode).run()
    app.button[0].click().run()
    assert not app.exception
    assert not app.error

def test_generated_reading_survives_rerun_and_is_not_reused_for_another_entity():
    root=Path(__file__).resolve().parents[1]
    app=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    app.selectbox(key='data_source').set_value('Laboratorio dimostrativo').run()
    app.button[0].click().run()
    assert len(app.get('download_button'))==2
    app.run()
    assert len(app.get('download_button'))==2
    current=app.selectbox(key='administration').value
    app.selectbox(key='administration').set_value(1 if current!=1 else 2).run()
    assert len(app.get('download_button'))==0
    assert not app.exception
