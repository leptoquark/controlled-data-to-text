# Copia offline dei profili della dashboard

Fonte: database locale `indicatori`, collection `debito_media`, filtro `rappresentabile=true`. L'esportatore usa soltanto letture: non modifica collection, indici o testi.

La lista dei campi ammessi è `mongo_snapshot.FIELDS`. Si conservano denominazione, codice ente, categoria, indicatori economici, serie annuali essenziali e narrazioni Markdown già presenti nella dashboard.
Le informazioni fiscali e di contatto non sono necessarie all'applicazione e non sono incluse.

Il riconoscimento della territorialità riutilizza la funzione del generatore fornito. Gli indici sono letti sulla scala 0–100, senza riscalare automaticamente i valori tra 0 e 1. La media regionale è mappata dal campo originale. Non si ricostruiscono feature o etichette mancanti.

Il dataset reale non è associato al modello dimostrativo. Senza annotazioni dei blocchi non si possono calcolare F1 o precision sui dati reali. Per questi profili sono consultabili i testi originali ed è disponibile la generazione deterministica a regole con evidenze.

La presenza nel database non certifica la correttezza economica o istituzionale dei testi storici; l'applicazione li mostra come originali. La nuova generazione applica i controlli numerici del framework. I record incoerenti sono registrati nel rapporto locale degli scarti.

La directory `data/real` è copiata nell'immagine Docker e non è versionata su GitHub. Per aggiornare i dati ripetere l'export e ricostruire l'immagine. Non servono connessioni MongoDB o porte DB nel container.
