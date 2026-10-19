# Dataset sintetico v1

1200 enti fittizi, un record per ente, seed 42; nessun ente reale o identificativo fiscale.
Le denominazioni hanno forma verosimile per comuni, agenzie, consorzi e aziende di servizi. Sono costruite combinando toponimi e non identificano fonti amministrative reali; eventuali omonimie sono casuali.

Le serie contengono da 1 a 6 annualità a partire dal 2019. Entrate e popolazione seguono distribuzioni con ordini di grandezza variabili. Il flusso netto di debito è costruito come rapporto × entrate; il rapporto può essere negativo. Il dato non rappresenta lo stock di debito.
I valori medi si riferiscono alle annualità disponibili per ciascun ente: non tutti gli enti hanno lo stesso periodo di osservazione.
La media dei rapporti non equivale necessariamente al rapporto delle medie.

Per i comuni le entrate di base sono proporzionate ai residenti (900–2200 euro per abitante prima delle variazioni annuali) e il personale a circa 4–9 addetti per mille residenti, con minimo 3 addetti. Per gli altri enti le entrate di base variano tra 2 e 800 milioni e il personale è stimato da una quota di budget del 15–35%, con costo annuo convenzionale di 50–75 mila euro per addetto. Gli appalti rappresentano l'8–45% delle entrate medie disponibili. Questi intervalli sono assunzioni del generatore, non benchmark ufficiali.
Le distribuzioni sono scelte progettuali plausibili, non stime statistiche della popolazione amministrativa italiana. Non vanno usate per conclusioni su enti, territori o rischio effettivo.
Gli indici sintetici e le soglie non sono indicatori ufficiali. I percentili sono variabili simulate, non ranghi ricalcolati su gruppi territoriali.

`labels` contiene 11 decisioni binarie create da `synthetic_policy_v1` nel codice. Non è un'annotazione umana. Il confronto tra modelli valuta una policy costruita usando alcune variabili presenti nelle feature e alcune condizioni disponibili soltanto nel profilo: l'errore residuo può dipendere anche da questa rappresentazione.

Schema delle feature:
- 7 strutturali: territorialità, log-popolazione, log-entrate, annualità, quota di campi mancanti, presenza personale, presenza appalti;
- 15 score 0–100, di cui efficienza/sostenibilità/rischio derivati dal profilo simulato;
- 8 trend simulati in scala −100..100;
- 12 percentili simulati 0–100.

Per una valutazione reale, sostituire dataset, definizioni delle feature e annotazioni, mantenendo separati train/validation/test per amministrazione.
