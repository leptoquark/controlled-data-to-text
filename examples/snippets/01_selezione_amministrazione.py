from pathlib import Path
from controlled_d2t.recipes import read_profile

ROOT = Path.cwd()  # Eseguire dalla cartella del progetto.
DATASET = None  # None: copia locale MongoDB, altrimenti laboratorio.
TARGET_CODE = None  # Impostare un codice ente per riprodurre una selezione.
profile = read_profile(ROOT, dataset=DATASET, code=TARGET_CODE)

from controlled_d2t.selection import group_profiles, typology
from controlled_d2t.synthetic import load

data_path = ROOT / DATASET if DATASET else ROOT / "data/real/profiles.jsonl"
if DATASET is None and not data_path.exists():
    data_path = ROOT / "data/synthetic.jsonl"
profiles = load(data_path)
groups = group_profiles(profiles)
selected_type = typology(profile)
candidates = [profiles[i] for i in groups[selected_type]]
print("Tipologia:", selected_type, "| Amministrazioni:", len(candidates))
for candidate in candidates[:10]:
    print(candidate["codice_ente"], candidate["denominazione"])
selected = next(d for d in candidates if d["codice_ente"] == profile["codice_ente"])
print("Selezionata:", selected["denominazione"])
