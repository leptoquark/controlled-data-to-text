# Feature osservate e feature del laboratorio

`extract_observed_features(profile)` estrae 18 valori dai campi del profilo. Non modifica il profilo, non aggiunge etichette e non completa lo schema del modello.

| Feature | Definizione |
|---|---|
| `territoriale` | 1 o 0 dal flag esplicito, null se non disponibile |
| `pop_log` | log naturale di 1 + popolazione media; null se manca |
| `entrate_log` | log naturale di 1 + entrate medie; null se manca |
| `anni_disponibili` | Numero delle annualità nel profilo, incluse quelle con indicatori mancanti |
| `quota_mancanti` | Quota di mancanti tra rapporto medio debito/entrate, efficienza, appalti e popolazione; non equivale a un indice generale di qualità |
| `personale_presente` | Presenza di un dato numerico finito sul personale, incluso zero |
| `appalti_presenti` | Presenza di un dato numerico finito sugli appalti, incluso zero |
| `score_efficienza` | Indice di efficienza originale, scala esplicita 0–100 |
| `score_sostenibilita` | Indice di sostenibilità originale, scala esplicita 0–100 |
| `score_rischio` | Indice di rischio originale, scala esplicita 0–100 |
| `trend_debito_pp_1` … `trend_debito_pp_8` | Differenza del rapporto debito/entrate tra due anni consecutivi, moltiplicata per 100: punti percentuali. Il primo confronto riguarda l'ultima annualità presente e la precedente, il secondo le due annualità immediatamente precedenti e così via. Se manca un estremo, il risultato è null. |

La popolazione può non essere applicabile agli enti non territoriali: la quota mancanti segue una convenzione dichiarata e non va usata per confrontare automaticamente la qualità di enti di natura diversa. Non si interpolano gli anni assenti e non si sostituisce null con zero.

Lo schema dimostrativo di `schema.FEATURES` contiene invece 42 colonne e richiede il relativo modello e il suo protocollo. Otto suoi trend e dodici percentili derivano dal generatore del laboratorio, non dall'estrattore osservato. Per evitare equivalenze scorrette, i trend osservati hanno nomi distinti.
Gli esempi 05 e 06 mostrano la generazione e l'uso di quello schema; l'esempio 04 e la pipeline 07 usano l'estrazione osservata. Prima di addestrare un modello reale occorre definire e validare uno schema coerente con le annotazioni reali.
