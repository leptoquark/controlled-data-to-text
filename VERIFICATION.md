# Verifiche eseguite

- Ambiente Python 3.12.14, dipendenze fissate in `requirements-lock.txt`.
- Generazione di 1200 profili sintetici con seed 42.
- Addestramento e confronto di RF, comitato a maggioranza, comitato pesato e baseline a regole.
- Salvataggio di modello, split, metriche, intervalli bootstrap e importanze globali.
- Generazione da CLI su un profilo di esempio.
- 12 test superati: regole numeriche, determinismo, valori mancanti e zero, tracciabilità, ordine annualità e due percorsi della demo.
- `pip check`: nessuna dipendenza incompatibile.
- Server locale avviato e endpoint health verificato: `ok`.

Non sono stati eseguiti accessi ai database di esercizio, importazioni dalle fonti istituzionali, addestramento su dati reali o build Docker. La configurazione Docker è fornita ma non verificata in questo ambiente.
La compatibilità Linux/macOS è prevista dal progetto, ma le esecuzioni riportate sono state effettuate su Windows.
