"""Helpers for executable, offline code recipes."""
import json
from pathlib import Path

def read_profile(root, dataset=None, code=None):
    root=Path(root)
    path=root/dataset if dataset else root/'data/real/profiles.jsonl'
    if dataset is None and not path.exists(): path=root/'data/synthetic.jsonl'
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            if not line.strip(): continue
            profile=json.loads(line)
            if code is None or profile.get('codice_ente')==str(code): return profile
    raise ValueError(f'Nessun profilo trovato per il codice {code!r} in {path}')
