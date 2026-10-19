from pathlib import Path
import pickle
import numpy as np
from controlled_d2t.recipes import read_profile
from controlled_d2t.experiment import predict
from controlled_d2t.schema import BLOCKS, FEATURES
from controlled_d2t.engine import generate

ROOT = Path.cwd()
# Il modello incluso è addestrato sul laboratorio, non sui profili reali.
profile = read_profile(ROOT, dataset="data/synthetic.jsonl")
# Caricare esclusivamente il modello locale creato da questo progetto.
with (ROOT / "results/latest/model.local.pkl").open("rb") as handle:
    bundle = pickle.load(handle)
if bundle["features"] != FEATURES:
    raise ValueError("Schema delle feature incompatibile")
scores = predict(bundle, [profile])[0]
selected = {block: bool(score >= 0.5) for block, score in zip(BLOCKS, scores)}
margin = float(np.mean(abs(scores - 0.5) * 2))
result = generate(profile, selected=selected, confidence=margin)
print(result["text"])
print("Margine di selezione non calibrato:", margin)
