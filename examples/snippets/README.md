# Esempi eseguibili

Installare il progetto e avviare gli script dalla sua cartella principale:

```sh
python -m pip install -e .
python examples/snippets/01_selezione_amministrazione.py
```

Ogni file è eseguibile separatamente. `DATASET = None` preferisce la copia MongoDB locale e ripiega sul laboratorio se assente. `TARGET_CODE` permette di specificare l'ente. I file scaricati dall'interfaccia includono la selezione corrente quando pertinente.

Gli esempi 05 e 06 usano soltanto il laboratorio: il modello richiede le sue 42 feature. L'estrattore dei dati osservati restituisce 18 feature, conserva i mancanti come null e non inventa percentili, score o annotazioni. Non collegare queste feature al modello a 42 colonne.

Gli esempi 03 e 07 scrivono sotto `work/snippets`. Non modificano MongoDB o i template predefiniti. Per il riuso occorrono il pacchetto `controlled_d2t` installato e i file di dati e modelli indicati; lo ZIP degli esempi non contiene i dati della dashboard.
