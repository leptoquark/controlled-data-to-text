# Notebook Colab e Jupyter

Il notebook `notebooks/controlled_data_to_text.ipynb` contiene un percorso guidato con codice, spiegazioni e prove modificabili. Usa le API reali del progetto e non avvia un server web nel runtime Colab.

## Percorso consigliato
1. Nella pagina **Codice e riuso** premi **Apri il notebook in Colab**.
2. Scarica dall'app il **pacchetto per Colab**: include i sorgenti necessari, il notebook e il solo profilo selezionato.
3. Esegui la prima cella del notebook; quando richiesto carica lo ZIP. L'installazione delle dipendenze richiede Internet, ma non servono MongoDB, credenziali del database o token GitHub.
4. Esegui le celle successive. Puoi modificare regole, template e selezione dell'ente, esaminare 18 feature osservabili e facoltativamente addestrare il comitato sul laboratorio a 42 feature.

Il pacchetto non viene caricato automaticamente su Google. Se scegli di caricarlo nel runtime Colab, il profilo contenuto nel file viene trasferito al servizio. Per esplorare l'intera copia locale usa invece lo ZIP completo del progetto, che contiene più profili.

## Repository privato
Il collegamento predefinito punta al notebook su GitHub. Il suo accesso dipende dai permessi e dalla sessione GitHub riconosciuta da Colab. Non viene cambiata la visibilità del repository.
Se il collegamento diretto non è utilizzabile, scarica il notebook e in Colab scegli **File → Carica notebook**. Il successivo caricamento del pacchetto non richiede accesso al repository.

## Configurare una copia su Drive
Apri il notebook in Colab, salva una copia nel tuo Drive e copia il relativo URL. Imposta in PowerShell:

```powershell
$env:D2T_COLAB_NOTEBOOK_URL = "https://colab.research.google.com/drive/ID_DEL_NOTEBOOK"
docker compose up --build
```

Oppure imposta la variabile in un file `.env` accanto a `compose.yaml`. Sono accettati soltanto link HTTPS del dominio Colab. Il link non concede permessi ai visitatori: configura la condivisione nella tua copia quando necessario.

## Esecuzione locale
```bash
python -m pip install -e '.[notebook]'
```
Apri il notebook in Jupyter o nell'editor che usi abitualmente. Imposta `PROJECT_DIR` se il progetto non viene trovato. Gli output sono salvati sotto `work/colab`.

## Contenuti
- lettura del pacchetto e preparazione dell'ambiente;
- selettori di tipologia e amministrazione;
- indicatori e andamento annuale;
- selezione dei blocchi e prova con dati mancanti;
- catalogo e personalizzazione dei template, verifica del determinismo;
- feature osservabili, zero e valori mancanti;
- schema del laboratorio e addestramento opzionale;
- esportazione di testo, evidenze, template e metadati.

Il notebook è distribuito senza risultati eseguiti o dati incorporati. Le metriche del laboratorio restano separate dai profili reali. Prima di esportare, riesegui le celle successive all'ultima modifica della selezione.

Riferimenti ufficiali: [FAQ Colab](https://research.google.com/colaboratory/intl/en-GB/faq.html), [collegamenti Open in Colab](https://github.com/googlecolab/open_in_colab).
