### Architettura
Profilo JSON → validazione → selettore di blocchi → template deterministici → rapporto con evidenze → revisione umana.
La disponibilità dei dati è sempre un vincolo: il modello non può forzare un blocco privo delle evidenze necessarie.
Non si usano modelli linguistici generativi. Gli output non vengono pubblicati automaticamente.

### Corrispondenza e differenze rispetto al paper
Si recupera il generatore storico come modulo `legacy`, isolato da MongoDB. Il nuovo percorso controllato usa 11 blocchi, template esterni e tracciabilità.
I 42 attributi dimostrativi sono 7 attributi strutturali, 15 score, 8 trend e 12 percentili: nomi e formule sono una ricostruzione, non lo schema originale ANAC.
Il generatore sintetico crea enti fittizi con flussi annuali coerenti, scale variabili e dati mancanti. Alcune feature sono variabili di disturbo simulate; score e misure possono essere presenti come segnali latenti anche quando una misura visualizzata è mancante: lo schema dimostrativo non va trasferito senza revisione su dati reali.
Le etichette derivano da una policy editoriale esplicita nel generatore, NON da annotazioni di esperti. L'esperimento misura la capacità di apprenderla. Non dimostra utilità istituzionale, affidabilità su dati reali o superiorità scientifica.

### Selettori e valutazione
RF, Gradient Boosting ed Extra Trees sono addestrati un classificatore per blocco; i blocchi costanti usano un classificatore costante.
Il comitato pesato combina probabilità con pesi logaritmici derivati dall'errore sul validation set, ispirati ad AdaBoost. Non implementa il metodo originale non disponibile, né un ciclo AdaBoost completo.
Il confronto a maggioranza usa il voto binario dei tre membri. La baseline a regole applica soltanto disponibilità e applicabilità dei blocchi; non coincide con la baseline originale del paper.
Split casuale 70/15/15 per enti univoci; nessuna stratificazione multilabel e nessuna cross-validation in questa versione. Sono salvati identificativi e seed.
F1, precision e recall micro/macro sono calcolati sul test. L'intervallo percentile bootstrap ricampiona enti del test (200 repliche predefinite; impostare 1000 per una stima più stabile).
Il margine medio rispetto a 0,5 è un segnale NON calibrato di confidenza sulla selezione: non è probabilità di correttezza fattuale. La soglia dimostrativa 0,6 è configurabile nell'API e non è stata validata sul dominio reale.
L'importanza delle feature è globale, aggregata dai modelli ad albero; per singolo caso si mostrano probabilità dei membri e decisioni.

### Fedeltà numerica e controllo
Il validatore verifica tipi, valori finiti, scale esplicite 0–100 e coerenza rapporto × entrate = variazione per le annualità complete.
I numeri nei template distribuiti sono formattati direttamente dai dati, senza riscrittura libera; il rapporto conserva le evidenze.
Non verifica la veridicità delle fonti, la correttezza economica degli indici a monte o la coerenza di ogni aggregato storico.
Le modifiche ai template richiedono revisione: un template personalizzato può introdurre affermazioni non supportate. Non c'è certificazione di conformità normativa.

### Passaggio ai dati reali
Esportare da MongoDB un profilo o JSONL, mappare esplicitamente territorialità e scale, definire le 42 feature reali e raccogliere etichette indipendenti da esperti. Separare gli enti tra split, fissare il periodo e rivalutare soglie e confidenza.
I profili grezzi dello scheduler si possono provare con il selettore a regole dopo il mapping. Il comitato richiede le feature esplicite e non è qualificato per uso reale.
Prima di un rilascio istituzionale servono validazione umana più ampia, misure di accordo tra annotatori e un processo di revisione e pubblicazione esterno.
