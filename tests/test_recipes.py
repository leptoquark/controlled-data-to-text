import io
import json
import runpy
import shutil
import zipfile
from pathlib import Path
from controlled_d2t.features import extract_observed_features
from controlled_d2t.synthetic import make_dataset, save
from controlled_d2t.ui_code import RECIPES, recipe_bundle, recipe_code

ROOT=Path(__file__).resolve().parents[1]

def test_observed_features_preserve_missing_and_zero():
    d=make_dataset(1)[0]
    d['popolazione_media']=None
    d['PERSONALE']=0
    d['importo_appalti_media']=0
    d['indice_efficienza']=0
    f=extract_observed_features(d)
    assert len(f)==18
    assert f['pop_log'] is None
    assert f['personale_presente']==1 and f['appalti_presenti']==1
    assert f['score_efficienza']==0
    assert 'percentile_0' not in f and 'score_trasparenza' not in f

def test_observed_trends_do_not_bridge_missing_years():
    d=make_dataset(1)[0]
    d['valori_annuali']={'2020':{'debito_su_entrate':.1},'2022':{'debito_su_entrate':.2},'2023':{'debito_su_entrate':.25}}
    f=extract_observed_features(d)
    assert abs(f['trend_debito_pp_1']-5)<1e-8
    assert f['trend_debito_pp_2'] is None

def test_every_downloadable_recipe_runs_from_project_root(tmp_path,monkeypatch,capsys):
    save(make_dataset(20),tmp_path/'data/synthetic.jsonl')
    target=tmp_path/'results/latest/model.local.pkl'
    target.parent.mkdir(parents=True)
    shutil.copy2(ROOT/'results/latest/model.local.pkl',target)
    monkeypatch.chdir(tmp_path)
    for _,_,filename,_,_ in RECIPES:
        runpy.run_path(str(ROOT/'examples/snippets'/filename),run_name='__main__')
    report=json.loads((tmp_path/'work/snippets/rapporto.json').read_text(encoding='utf-8'))
    assert len(report['observed_features'])==18
    assert report['generation']['blocks']
    assert (tmp_path/'work/snippets/template_personalizzati.json').exists()
    capsys.readouterr()

def test_customized_snippets_select_the_requested_entity(tmp_path,monkeypatch,capsys):
    docs=make_dataset(2)
    save(docs,tmp_path/'data/real/profiles.jsonl')
    profile=docs[1]
    monkeypatch.chdir(tmp_path)
    code=recipe_code(ROOT,'04_feature_osservate.py',profile,'data/real/profiles.jsonl')
    namespace={'__name__':'__main__'}
    exec(compile(code,'downloaded_recipe.py','exec'),namespace)
    assert namespace['profile']['codice_ente']==profile['codice_ente']
    with zipfile.ZipFile(io.BytesIO(recipe_bundle(ROOT,profile,'data/real/profiles.jsonl'))) as archive:
        assert len(archive.namelist())==8
        assert all(name.startswith('examples/snippets/') for name in archive.namelist())
        for name in archive.namelist():
            if name.endswith('.py'): compile(archive.read(name),name,'exec')
    capsys.readouterr()

def test_code_library_has_live_feature_preview_and_downloads():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    app.selectbox(key='data_source').set_value('Laboratorio dimostrativo').run()
    chosen=app.selectbox(key='administration').value
    docs=[json.loads(line) for line in (ROOT/'data/synthetic.jsonl').read_text(encoding='utf-8').splitlines()]
    app.session_state['main_page']='Codice e riuso'
    app.run()
    assert not app.exception
    assert len(app.get('download_button'))==4
    assert any(repr(docs[chosen]['codice_ente']) in block.proto.code_text for block in app.get('code'))
    app.selectbox(key='recipe_topic').set_value('Feature').run()
    assert not app.exception
    assert len(app.dataframe[0].value)==18
    app.selectbox(key='recipe_topic').set_value('Template').run()
    assert not app.exception
    assert app.selectbox(key='template_catalog_block').value=='introduzione'
