# Lettura dell'esperimento incluso

Seed 42, 1200 profili: 840 train, 180 validation, 180 test. Denominazioni verosimili e misure economiche proporzionate alla dimensione dell'ente; vedere la scheda del dataset.

| Selettore | Micro F1 | Macro F1 |
|---|---:|---:|
| Comitato pesato | 0.9525 | 0.8923 |
| Random Forest | 0.9494 | 0.8927 |
| Maggioranza | 0.9526 | 0.8962 |
| Regole di disponibilità | 0.9485 | 0.9437 |

Intervallo bootstrap del Micro F1 del comitato pesato: [0.9446; 0.9582], con 200 ricampionamenti di enti del test.
Il comitato a maggioranza ha il Micro F1 maggiore; la baseline a regole ha il Macro F1 maggiore. Non è stata verificata la significatività delle differenze.
Alcuni blocchi hanno etichette costanti o molto semplici; il Micro F1 alto non implica prestazioni uniformi.

Il blocco tesoreria ha F1 0.075 nel comitato pesato: manca una feature dedicata alla disponibilità delle anticipazioni. La baseline a regole legge direttamente il profilo, mentre il modello usa le 42 feature. Il confronto evidenzia anche un limite di rappresentazione e non è a parità di informazione.

Le etichette sono create da una policy simulata, non da esperti. I valori del paper derivano da un altro dataset e protocollo e non sono direttamente confrontabili.
Per una valutazione scientifica servono dati reali, feature condivise e annotazioni indipendenti. I dettagli riproducibili sono in `latest/metrics.json`.
