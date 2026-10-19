# Lettura dell'esperimento incluso

Seed 42, 1200 profili sintetici: 840 train, 180 validation, 180 test.

| Selettore | Micro F1 | Macro F1 |
|---|---:|---:|
| Comitato pesato | 0,9547 | 0,8899 |
| Random Forest | 0,9529 | 0,8931 |
| Maggioranza | 0,9531 | 0,8907 |
| Regole di disponibilità | 0,9491 | 0,9417 |

Il comitato prevale di poco sul Micro F1, ma non sul Macro F1. L'intervallo bootstrap del Micro F1 è circa [0,9482; 0,9609], con 200 ricampionamenti di enti del test.
Non è stata verificata la significatività delle differenze tra modelli. Quattro blocchi hanno etichette costanti o molto semplici; il Micro F1 alto non implica prestazioni uniformi.

Il blocco tesoreria raggiunge F1 circa 0,058 nel comitato: la presenza delle anticipazioni nel profilo non ha una feature dedicata nello schema dimostrativo. La baseline a regole può leggerla direttamente, mentre il modello dispone delle sole 42 feature. Questo rende il confronto anche una verifica dei limiti della rappresentazione, non un confronto a parità di informazione.
Per rendere il confronto scientificamente equo va definita una rappresentazione reale condivisa e una policy indipendente, con annotazioni di esperti. Non modificare il simulatore soltanto per ottenere valori simili a quelli del paper.

Il valore 0,901 del paper riguarda un altro dataset e un altro protocollo: non è confrontabile direttamente con 0,9547 su questi dati sintetici.

I valori completi e i metadati riproducibili sono in `latest/metrics.json`.
