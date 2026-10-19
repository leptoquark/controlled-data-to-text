# Verifiche eseguite

- Ambiente Python 3.12.14, dipendenze fissate in `requirements-lock.txt`.
- Generazione di 1200 profili sintetici con seed 42.
- Addestramento e confronto di RF, comitato a maggioranza, comitato pesato e baseline a regole.
- Salvataggio di modello, split, metriche, intervalli bootstrap e importanze globali.
- Generazione da CLI su un profilo di esempio.
- 15 test: regole numeriche, determinismo, valori mancanti e zero, tracciabilità, ordine annualità, due percorsi del laboratorio, adattatore MongoDB, validazione della copia e percorso della demo sui profili reali. I due test sulla copia locale sono saltati quando questa non è disponibile.
- `pip check`: nessuna dipendenza incompatibile.
- Server locale avviato e endpoint health verificato: `ok`.

È stato eseguito un export in sola lettura dal database locale `indicatori`, collection `debito_media`: 11.364 record letti, 11.360 validi esportati e 4 scartati per incoerenze annuali. Tutti i profili esportati conservano le spiegazioni originali. I file della copia sono locali e non versionati.
Sono stati aggiunti controlli sull'adattatore, validazione dell'intera copia e verifica della demo sui profili reali. Non sono stati eseguiti importazioni dalle fonti istituzionali, addestramento su dati reali o build Docker. La configurazione Docker è fornita ma non verificata in questo ambiente.
La compatibilità Linux/macOS è prevista dal progetto, ma le esecuzioni riportate sono state effettuate su Windows.
