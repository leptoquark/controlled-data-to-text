from pathlib import Path
from controlled_d2t.recipes import read_profile

ROOT = Path.cwd()  # Eseguire dalla cartella del progetto.
DATASET = None  # None: copia locale MongoDB, altrimenti laboratorio.
TARGET_CODE = None  # Impostare un codice ente per riprodurre una selezione.
profile = read_profile(ROOT, dataset=DATASET, code=TARGET_CODE)

import json
from controlled_d2t.engine import DEFAULT_TEMPLATES, generate

templates = json.loads(DEFAULT_TEMPLATES.read_text(encoding="utf-8"))
templates["introduzione"] = [
    "Questa lettura presenta il profilo di {nome}.",
    "Di seguito sono illustrati i dati disponibili per {nome}.",
]
target = ROOT / "work/snippets/template_personalizzati.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8")
result = generate(profile, template_path=target)
if result["status"] == "blocked":
    raise ValueError(result["errors"])
for block in result["blocks"]:
    print(block["template_id"], block["text"])
# Il motore sceglie una variante con SHA-256(codice_ente + blocco).
# Controllare sempre che nuovi testi non introducano affermazioni senza evidenza.
