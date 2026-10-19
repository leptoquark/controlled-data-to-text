"""Notebook links and an explicit, downloadable package for the selected profile."""
import io
import json
import os
import zipfile
from pathlib import Path
from urllib.parse import urlparse

NOTEBOOK_PATH='notebooks/controlled_data_to_text.ipynb'
DEFAULT_COLAB_URL='https://colab.research.google.com/github/leptoquark/controlled-data-to-text/blob/main/'+NOTEBOOK_PATH

def notebook_url():
    value=os.getenv('D2T_COLAB_NOTEBOOK_URL','').strip() or DEFAULT_COLAB_URL
    parsed=urlparse(value)
    if parsed.scheme!='https' or parsed.hostname!='colab.research.google.com' or parsed.username or parsed.password:
        raise ValueError('D2T_COLAB_NOTEBOOK_URL deve essere un link HTTPS di colab.research.google.com')
    return value

def colab_bundle(root,profile):
    root=Path(root)
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
        base='controlled-data-to-text/'
        paths=[root/'pyproject.toml',root/NOTEBOOK_PATH,root/'docs/FEATURES.md',root/'docs/COLAB.md']
        paths += [p for p in (root/'src/controlled_d2t').iterdir() if p.is_file() and p.suffix in {'.py','.json'}]
        for path in paths: archive.write(path,base+path.relative_to(root).as_posix())
        archive.writestr(base+'data/colab/profiles.jsonl',json.dumps(profile,ensure_ascii=False,allow_nan=False)+'\n')
        archive.writestr(base+'data/colab/manifest.json',json.dumps({'records':1,'codice_ente':profile['codice_ente'],'source':profile.get('data_origin','selected_profile'),'purpose':'Colab workshop; only the profile explicitly selected for download'},ensure_ascii=False,indent=2))
    return buffer.getvalue()
