# Controlled Data-to-Text — laboratorio per il riuso

Ambiente locale per generazione controllata, selezione dei blocchi e confronto dei risultati. Basato sul paper di Claudio Biancalana e Fabrizio Sbicca e sul generatore dell'archivio fornito dall'utente.

**I dati inclusi sono sintetici e le etichette sono simulate. I risultati locali non sono una replica dei risultati scientifici pubblicati.**

## Avvio rapido Windows (PowerShell)
Da questa cartella, con Python 3.11 o successivo:
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Per riprodurre le versioni verificate usare prima `pip install -r requirements-lock.txt`, poi `pip install -e ".[test]"`.
La demo include già dataset e risultati. Se il modello locale non è compatibile con la versione di scikit-learn installata, rigenerarlo con il comando experiment.

## Linux/macOS
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m streamlit run app.py
```

## Ripetere gli esperimenti
Nell'ambiente attivato:
```bash
d2t synth --n 1200 --seed 42 --output data/synthetic.jsonl
d2t experiment --data data/synthetic.jsonl --output results/latest --seed 42 --bootstrap 200
d2t generate data/synthetic.example.json --output results/generated.json
python -m pytest
```
`generate` usa le regole. Il comitato ML si prova nella demo o tramite `experiment.predict` seguito da `engine.generate`.
I risultati includono metriche, split con identificativi, versioni, hash dataset e importanze globali. I testi includono hash di input e template, decisioni ed evidenze.

## Docker
```bash
docker compose up --build
```
Aprire http://localhost:8502. La porta del container resta 8501; la porta locale predefinita è 8502 per consentire l'esecuzione contemporanea della demo Python.
Per scegliere un'altra porta in PowerShell:
```powershell
$env:DEMO_PORT = "8503"
docker compose up --build
```
In questo caso aprire http://localhost:8503. La build installa dipendenze da Internet. Non richiede MongoDB o credenziali.

## Struttura
- `src/controlled_d2t`: framework, CLI, esperimenti e modulo legacy isolato
- `config/templates.json`: copia leggibile dei template iniziali; per usarne una modifica passare `template_path` a `generate`
- `src/controlled_d2t/templates.json`: template predefiniti distribuiti nel pacchetto
- `data`: profili JSONL e un profilo di esempio
- `results/paper_reported.json`: risultati trascritti dal paper
- `results/latest`: risultati sintetici e modello locale
- `docs/METHOD.md`: metodo, differenze, limiti e passaggio a dati reali
- `PROVENANCE.md`: origine del codice e condizioni di riuso da verificare

## Compatibilità con lo scheduler
Il modulo `legacy.narrazione_cittadina(doc)` conserva i testi storici brevi ed estesi senza dipendenze MongoDB; è un percorso di compatibilità, non il generatore validato della demo. Non avviare gli script di ingestion per provare questo laboratorio.
Lo ZIP originale rimane separato e non è ridistribuito. Nessun certificato, endpoint interno, configurazione di esercizio o rubrica è necessario nel nuovo progetto.

## Sicurezza dei modelli
Caricare soltanto il modello pickle creato localmente da questo progetto. Non caricare pickle ricevuti da terzi. La demo non accetta upload di modelli.
