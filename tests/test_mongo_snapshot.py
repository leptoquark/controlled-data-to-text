import copy
import json
from pathlib import Path
import pytest
from controlled_d2t.mongo_snapshot import adapt, FIELDS
from controlled_d2t.schema import validate
from controlled_d2t.engine import generate

def test_adapter_preserves_zero_and_removes_unneeded_fields():
    row={'codice_ente':'123','denominazione':'Comune di prova','categoria':'COMUNE',
         'indice_medio_debito_su_entrate':0,'debito_su_entrate_media':99,
         'media_regionale_media':{'debito_su_entrate':0.1},'cf':'excluded',
         'valori_annuali':{'2024':{'entrate_correnti':100,'debito_su_entrate':0,'variazione_debito':0,'cf':'excluded'}},
         'indice_efficienza':float('nan'),'narrazione_breve_md':'Testo originale'}
    original=copy.deepcopy(row)
    d=adapt(row)
    assert d['indice_medio_debito_su_entrate']==0
    assert d['indice_efficienza'] is None and d['synthetic'] is False
    assert d['territoriale'] and d['media_regionale_rapporto']==0.1
    assert 'cf' not in json.dumps(d) and 'features' not in d and 'labels' not in d
    assert row['valori_annuali']==original['valori_annuali']
    assert not validate(d) and generate(d)['status']!='blocked'
    assert 'cf' not in FIELDS

def test_local_snapshot_when_available():
    path=Path(__file__).resolve().parents[1]/'data/real/profiles.jsonl'
    if not path.exists(): pytest.skip('Snapshot locale non incluso nel repository')
    import hashlib
    manifest=json.loads(path.with_name('manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']
    docs=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert len(docs)==manifest['records_exported']
    assert docs and all(not validate(d) for d in docs)
    assert all(not d['synthetic'] and 'features' not in d and 'labels' not in d for d in docs)

def test_dashboard_ui_when_snapshot_available():
    from streamlit.testing.v1 import AppTest
    root=Path(__file__).resolve().parents[1]
    if not (root/'data/real/profiles.jsonl').exists(): pytest.skip('Snapshot locale non incluso nel repository')
    app=AppTest.from_file(str(root/'app.py'),default_timeout=60).run()
    assert not app.exception
    assert app.selectbox(key='data_source').value=='Dati dashboard (copia locale)'
    assert len(app.selectbox(key='administration').options)>0
    assert app.radio[0].options==['Regole di disponibilità']
    app.button[0].click().run()
    assert not app.exception and not app.error
