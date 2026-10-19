import io
import json
import zipfile
from pathlib import Path
import pytest
from controlled_d2t.colab import DEFAULT_COLAB_URL, NOTEBOOK_PATH, notebook_url, colab_bundle
from controlled_d2t.synthetic import make_dataset

ROOT=Path(__file__).resolve().parents[1]

def test_colab_link_configuration(monkeypatch):
    monkeypatch.delenv('D2T_COLAB_NOTEBOOK_URL',raising=False)
    assert notebook_url()==DEFAULT_COLAB_URL
    custom='https://colab.research.google.com/drive/my-notebook'
    monkeypatch.setenv('D2T_COLAB_NOTEBOOK_URL',custom)
    assert notebook_url()==custom
    monkeypatch.setenv('D2T_COLAB_NOTEBOOK_URL','javascript:alert(1)')
    with pytest.raises(ValueError): notebook_url()

def test_portable_package_contains_only_selected_profile_and_sources():
    profile=make_dataset(2)[1]
    with zipfile.ZipFile(io.BytesIO(colab_bundle(ROOT,profile))) as archive:
        assert archive.testzip() is None
        names=archive.namelist()
        base='controlled-data-to-text/'
        assert base+NOTEBOOK_PATH in names
        assert base+'src/controlled_d2t/engine.py' in names
        assert base+'pyproject.toml' in names
        assert not any('.env' in name or '/.git/' in name or '/data/real/' in name or name.endswith('.pkl') for name in names)
        rows=archive.read(base+'data/colab/profiles.jsonl').decode().splitlines()
        assert len(rows)==1 and json.loads(rows[0])==profile

def test_notebook_structure_and_python_cells():
    notebook=json.loads((ROOT/NOTEBOOK_PATH).read_text(encoding='utf-8'))
    assert notebook['nbformat']==4
    assert len(notebook['cells'])>=25
    for cell in notebook['cells']:
        if cell['cell_type']=='code':
            assert not cell['outputs'] and cell['execution_count'] is None
            compile(''.join(cell['source']),'notebook_cell.py','exec')

def test_notebook_cells_execute_locally(tmp_path,monkeypatch,capsys):
    pytest.importorskip('ipywidgets')
    pytest.importorskip('matplotlib').use('Agg',force=True)
    import sys
    monkeypatch.setattr(sys,'path',list(sys.path))
    # Exercise the portable package, without network calls, using a small dataset.
    with zipfile.ZipFile(io.BytesIO(colab_bundle(ROOT,make_dataset(1)[0]))) as archive:
        archive.extractall(tmp_path)
    project=tmp_path/'controlled-data-to-text'
    monkeypatch.chdir(project)
    monkeypatch.setenv('MPLBACKEND','Agg')
    notebook=json.loads((project/NOTEBOOK_PATH).read_text(encoding='utf-8'))
    namespace={'__name__':'__main__'}
    for cell in notebook['cells']:
        if cell['cell_type']=='code': exec(compile(''.join(cell['source']),'notebook_cell.py','exec'),namespace)
    assert namespace['IN_COLAB'] is False
    assert len(namespace['observed'])==18
    assert namespace['X'].shape==(300,42)
    assert namespace['export_zip'].exists()
    report=json.loads((project/'work/colab/rapporto.json').read_text(encoding='utf-8'))
    assert report['generation']['input_sha256']==report['input_sha256']
    capsys.readouterr()
