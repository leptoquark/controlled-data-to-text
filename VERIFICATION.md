# Verifiche eseguite

## Revisione del 20 ottobre 2026

Sul commit `d6dd4c1aac396147b1d8d100d372447a12bc810a`, GitHub Actions ha completato
con successo la verifica su Ubuntu e Python 3.12: 49 test superati e 2 saltati
per assenza dello snapshot locale non versionato. Sono stati rigenerati 1.200
profili sintetici e il modello di prova (seed 42, 20 repliche bootstrap per il
controllo CI, non per aggiornare le metriche scientifiche). `pip check`, build
Docker e controllo HTTP dell'endpoint health del container sono passati.

Esecuzione verificabile: https://github.com/leptoquark/controlled-data-to-text/actions/runs/39406354666

I test comprendono gli input non validi di confidenza e soglia, i confini del
review gate, la tipizzazione della territorialità e il perimetro degli stati di
bozza. Nessun esito autorizza la pubblicazione. Queste verifiche riguardano il
laboratorio, non la validazione del servizio ANAC o la replica del paper.
Colab cloud e dati reali non sono stati verificati in questa esecuzione.
Il cambio di stato da `validated_draft` a `automated_checks_passed_draft` richiede
l'aggiornamento di eventuali integrazioni che confrontano il vecchio nome.

## Verifiche precedenti nell'ambiente Windows originale

Le verifiche seguenti descrivono l'ambiente originale e non lo snapshot pubblico
o la verifica CI sopra indicata. I limiti Docker/Linux riportati in questa parte
si riferiscono a quelle esecuzioni precedenti.

- Ambiente Python 3.12.14, dipendenze fissate in `requirements-lock.txt`.
- Generazione di 1200 profili sintetici con seed 42.
- Addestramento e confronto di RF, comitato a maggioranza, comitato pesato e baseline a regole.
- Salvataggio di modello, split, metriche, intervalli bootstrap e importanze globali.
- Generazione da CLI su un profilo di esempio.
- 27 test superati: regole numeriche, determinismo, valori mancanti e zero, tracciabilità, ordine annualità, due percorsi del laboratorio, filtro tipologia/amministrazione con aggiornamento della selezione, persistenza della spiegazione dopo un aggiornamento della pagina e invalidazione al cambio di ente, navigazione con caricamento della sola scheda aperta e conservazione della bozza e dell'ente, adattatore MongoDB, validazione della copia e percorso della demo sui profili reali, estrazione delle feature, esecuzione dei sette snippet, personalizzazione del codice scaricato, ZIP degli esempi e anteprime nell'interfaccia, configurazione del link Colab, contenuto del pacchetto portabile, struttura del notebook ed esecuzione locale delle sue celle. I test sulla copia locale sono saltati quando questa non è disponibile; l'esecuzione del notebook richiede le dipendenze opzionali.
- Interfaccia verificata nel browser a 1440 e 390 pixel di larghezza: scheda amministrazione, risultati e adattamento mobile; nessun errore applicativo e nessuna eccedenza della larghezza del documento. Tema e stile sono inclusi localmente.
- Avvio verificato in contesti browser nuovi: barra laterale chiusa, intestazione visibile sotto la barra superiore e nessun contenuto della pagina Risultati elaborato all'apertura di Amministrazioni. Su mobile verificati il filtro Istituzione scolastica e il mantenimento dell'ente passando da Risultati e Come funziona e tornando ad Amministrazioni.
- Sezione Codice e riuso verificata nel browser: selezione dell'argomento Feature, anteprima sul profilo reale e download di `04_feature_osservate.py`, compilato senza errori. Gli snippet completi sono stati eseguiti in una cartella temporanea con dati e modello di prova, senza scritture sul database o sui template originali.
- Notebook validato con nbformat: 27 celle, di cui 14 di codice, senza output o dati salvati. Le celle sono state eseguite in locale su un pacchetto portabile di prova, comprese widget, grafico, template, controlli, matrice di 42 feature ed esportazione. Addestramento opzionale e download da Colab lasciati disattivati. Verificati nel browser il collegamento Colab e il download del pacchetto: un solo profilo, senza credenziali, modello pickle o copia integrale del database. Non è stata eseguita una sessione sul runtime cloud Colab né verificata l'autenticazione privata GitHub da Colab.
- `pip check`: nessuna dipendenza incompatibile.
- Server locale avviato e endpoint health verificato: `ok`.

È stato eseguito un export in sola lettura dal database locale `indicatori`, collection `debito_media`: 11.364 record letti, 11.360 validi esportati e 4 scartati per incoerenze annuali. Tutti i profili esportati conservano le spiegazioni originali. I file della copia sono locali e non versionati.
Sono stati aggiunti controlli sull'adattatore, validazione dell'intera copia e verifica della demo sui profili reali. Non sono stati eseguiti importazioni dalle fonti istituzionali, addestramento su dati reali o build Docker. La configurazione Docker è fornita ma non verificata in questo ambiente.
La compatibilità Linux/macOS è prevista dal progetto, ma le esecuzioni riportate sono state effettuate su Windows.

