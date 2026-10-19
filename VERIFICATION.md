# Verifiche eseguite

- Ambiente Python 3.12.14, dipendenze fissate in `requirements-lock.txt`.
- Generazione di 1200 profili sintetici con seed 42.
- Addestramento e confronto di RF, comitato a maggioranza, comitato pesato e baseline a regole.
- Salvataggio di modello, split, metriche, intervalli bootstrap e importanze globali.
- Generazione da CLI su un profilo di esempio.
- 23 test superati: regole numeriche, determinismo, valori mancanti e zero, tracciabilità, ordine annualità, due percorsi del laboratorio, filtro tipologia/amministrazione con aggiornamento della selezione, persistenza della spiegazione dopo un aggiornamento della pagina e invalidazione al cambio di ente, navigazione con caricamento della sola scheda aperta e conservazione della bozza e dell'ente, adattatore MongoDB, validazione della copia e percorso della demo sui profili reali, estrazione delle feature, esecuzione dei sette snippet, personalizzazione del codice scaricato, ZIP degli esempi e anteprime nell'interfaccia. I due test sulla copia locale sono saltati quando questa non è disponibile.
- Interfaccia verificata nel browser a 1440 e 390 pixel di larghezza: scheda amministrazione, risultati e adattamento mobile; nessun errore applicativo e nessuna eccedenza della larghezza del documento. Tema e stile sono inclusi localmente.
- Avvio verificato in contesti browser nuovi: barra laterale chiusa, intestazione visibile sotto la barra superiore e nessun contenuto della pagina Risultati elaborato all'apertura di Amministrazioni. Su mobile verificati il filtro Istituzione scolastica e il mantenimento dell'ente passando da Risultati e Come funziona e tornando ad Amministrazioni.
- Sezione Codice e riuso verificata nel browser: selezione dell'argomento Feature, anteprima sul profilo reale e download di `04_feature_osservate.py`, compilato senza errori. Gli snippet completi sono stati eseguiti in una cartella temporanea con dati e modello di prova, senza scritture sul database o sui template originali.
- `pip check`: nessuna dipendenza incompatibile.
- Server locale avviato e endpoint health verificato: `ok`.

È stato eseguito un export in sola lettura dal database locale `indicatori`, collection `debito_media`: 11.364 record letti, 11.360 validi esportati e 4 scartati per incoerenze annuali. Tutti i profili esportati conservano le spiegazioni originali. I file della copia sono locali e non versionati.
Sono stati aggiunti controlli sull'adattatore, validazione dell'intera copia e verifica della demo sui profili reali. Non sono stati eseguiti importazioni dalle fonti istituzionali, addestramento su dati reali o build Docker. La configurazione Docker è fornita ma non verificata in questo ambiente.
La compatibilità Linux/macOS è prevista dal progetto, ma le esecuzioni riportate sono state effettuate su Windows.
