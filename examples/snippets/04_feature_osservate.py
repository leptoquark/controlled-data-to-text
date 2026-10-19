from pathlib import Path
from controlled_d2t.recipes import read_profile

ROOT = Path.cwd()  # Eseguire dalla cartella del progetto.
DATASET = None  # None: copia locale MongoDB, altrimenti laboratorio.
TARGET_CODE = None  # Impostare un codice ente per riprodurre una selezione.
profile = read_profile(ROOT, dataset=DATASET, code=TARGET_CODE)

import json
from controlled_d2t.features import extract_observed_features

features = extract_observed_features(profile)
print(json.dumps(features, ensure_ascii=False, indent=2, allow_nan=False))
print("Feature osservabili:", len(features))
print("Non disponibili:", sum(value is None for value in features.values()))
# I dati mancanti rimangono None; zero rimane un valore disponibile.
# I trend sono differenze tra anni consecutivi in punti percentuali.
# Queste 18 feature NON sono l'input del modello dimostrativo a 42 colonne.
