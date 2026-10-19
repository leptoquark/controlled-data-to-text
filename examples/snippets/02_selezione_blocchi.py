from pathlib import Path
from controlled_d2t.recipes import read_profile

ROOT = Path.cwd()  # Eseguire dalla cartella del progetto.
DATASET = None  # None: copia locale MongoDB, altrimenti laboratorio.
TARGET_CODE = None  # Impostare un codice ente per riprodurre una selezione.
profile = read_profile(ROOT, dataset=DATASET, code=TARGET_CODE)

from controlled_d2t.engine import generate
from controlled_d2t.schema import BLOCKS

# Le regole di disponibilità rimangono sempre un vincolo.
automatic = generate(profile)
for decision in automatic["decisions"]:
    print(decision["block"], decision["included"], decision["reason"])

# Scegliere soltanto tre contenuti; un dato mancante non viene inventato.
selected = {block: block in {"introduzione", "entrate", "debito"} for block in BLOCKS}
result = generate(profile, selected=selected)
if result["status"] == "blocked":
    raise ValueError(result["errors"])
print(result["text"])
