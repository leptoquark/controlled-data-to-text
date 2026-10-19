from pathlib import Path
from controlled_d2t.recipes import read_profile

ROOT = Path.cwd()  # Eseguire dalla cartella del progetto.
DATASET = None  # None: copia locale MongoDB, altrimenti laboratorio.
TARGET_CODE = None  # Impostare un codice ente per riprodurre una selezione.
profile = read_profile(ROOT, dataset=DATASET, code=TARGET_CODE)

import json
from controlled_d2t.features import extract_observed_features
from controlled_d2t.engine import generate

observed = extract_observed_features(profile)
result = generate(profile)
if result["status"] == "blocked":
    raise ValueError(result["errors"])
output = ROOT / "work/snippets"
output.mkdir(parents=True, exist_ok=True)
(output / "spiegazione.txt").write_text(result["text"], encoding="utf-8")
(output / "rapporto.json").write_text(
    json.dumps({"observed_features": observed, "generation": result},
               ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
)
print("Testo ed evidenze salvati in", output)
