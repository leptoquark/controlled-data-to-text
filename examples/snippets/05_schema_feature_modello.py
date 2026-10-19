from controlled_d2t.synthetic import make_dataset
from controlled_d2t.schema import FEATURES
from controlled_d2t.experiment import matrix

# Genera un profilo del laboratorio con le sue feature e la policy simulata.
# Questo NON ricostruisce le feature mancanti dei profili MongoDB.
profile = make_dataset(n=1, seed=42)[0]
X = matrix([profile])  # Ordine fisso, definito da FEATURES.
assert X.shape == (1, 42)
for name, value in zip(FEATURES, X[0]):
    print(name, value)
print("Forma della matrice:", X.shape)
