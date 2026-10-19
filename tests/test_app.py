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
    app.selectbox(key='administration').select_index(1).run()
    assert len(app.get('download_button'))==0
    assert not app.exception

def test_typology_filters_entities_and_resets_selection():
    import json
    root=Path(__file__).resolve().parents[1]
    docs=[json.loads(line) for line in (root/'data/synthetic.jsonl').read_text(encoding='utf-8').splitlines()]
    app=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    app.selectbox(key='data_source').set_value('Laboratorio dimostrativo').run()
    assert app.selectbox(key='administration_type').value=='Comune'
    assert len(app.selectbox(key='administration').options)==sum(d['categoria']=='COMUNE' for d in docs)
    app.button[0].click().run()
    app.selectbox(key='administration_type').set_value('Ente strumentale').run()
    assert not app.exception and not app.error
    assert len(app.selectbox(key='administration').options)==sum(d['categoria']=='ENTE STRUMENTALE' for d in docs)
    chosen=app.selectbox(key='administration').value
    assert docs[chosen]['categoria']=='ENTE STRUMENTALE'
    assert len(app.get('download_button'))==0

def test_lazy_pages_keep_entity_draft_and_generated_reading():
    import json
    root=Path(__file__).resolve().parents[1]
    app=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    app.selectbox(key='data_source').set_value('Laboratorio dimostrativo').run()
    app.selectbox(key='administration_type').set_value('Ente strumentale').run()
    app.selectbox(key='administration').select_index(2).run()
    chosen=app.selectbox(key='administration').value
    profile=json.loads(app.text_area[0].value)
    profile['denominazione']='Profilo per verifica navigazione'
    app.text_area[0].set_value(json.dumps(profile)).run()
    app.button[0].click().run()
    assert len(app.get('download_button'))==2
    assert not any(s.value=='Lo studio pubblicato' for s in app.subheader)
    app.session_state['main_page']='Risultati e confronti'
    app.run()
    assert not app.exception
    assert any(s.value=='Lo studio pubblicato' for s in app.subheader)
    assert len(app.button)==0
    app.session_state['main_page']='Come funziona'
    app.run()
    assert not app.exception
    assert not app.dataframe
    app.session_state['main_page']='Amministrazioni'
    app.run()
    assert not app.exception
    assert app.selectbox(key='administration_type').value=='Ente strumentale'
    assert app.selectbox(key='administration').value==chosen
    assert json.loads(app.text_area[0].value)['denominazione']=='Profilo per verifica navigazione'
    assert len(app.get('download_button'))==2
