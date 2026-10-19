import math

INDICATORS = ["efficienza", "sostenibilita", "rischio", "debito", "entrate", "appalti", "personale", "tesoreria", "popolazione", "copertura", "regolarita", "autonomia", "liquidita", "investimenti", "trasparenza"]
FEATURES = (["territoriale", "pop_log", "entrate_log", "anni_disponibili", "quota_mancanti", "personale_presente", "appalti_presenti"]
            + ["score_"+x for x in INDICATORS] + ["trend_"+str(i) for i in range(8)] + ["percentile_"+str(i) for i in range(12)])
BLOCKS = ["introduzione", "diagnosi", "indici", "debito", "entrate", "popolazione", "trend", "anni_significativi", "appalti", "tesoreria", "confronti"]
def number(value):
    if isinstance(value, bool) or not isinstance(value, (int,float)):
        return None
    return float(value) if math.isfinite(value) else None
def validate(doc):
    errors=[]
    if not isinstance(doc,dict): return ["Il profilo deve essere un oggetto JSON."]
    if not isinstance(doc.get("codice_ente"),str) or not doc["codice_ente"].strip(): errors.append("codice_ente obbligatorio")
    if not isinstance(doc.get("denominazione"),str) or not doc["denominazione"].strip(): errors.append("denominazione obbligatoria")
    numeric=["indice_medio_debito_su_entrate","entrate_medie","variazione_media","popolazione_media","importo_appalti_media","anticipazioni_medie","indice_efficienza","indice_sostenibilita","indice_rischio","media_regionale_rapporto"]
    for key in numeric:
        v=doc.get(key)
        if v is not None and number(v) is None: errors.append(key+": numero finito richiesto")
        if number(v) is not None and key in {"entrate_medie","popolazione_media","importo_appalti_media","anticipazioni_medie"} and v<0: errors.append(key+": valore negativo")
        if number(v) is not None and key.startswith("indice_") and key!="indice_medio_debito_su_entrate" and not 0<=v<=100: errors.append(key+": scala esplicita 0–100 richiesta")
    annual=doc.get("valori_annuali",{})
    if not isinstance(annual,dict): errors.append("valori_annuali deve essere un oggetto")
    else:
        for year,row in annual.items():
            if not str(year).isdigit() or not isinstance(row,dict): errors.append("Annualità non valida"); continue
            for field in ("debito_su_entrate","entrate_correnti","variazione_debito"):
                if row.get(field) is not None and number(row[field]) is None: errors.append(f"{year}.{field}: numero non valido")
            r,e,v=(number(row.get(k)) for k in ("debito_su_entrate","entrate_correnti","variazione_debito"))
            if e is not None and e<0: errors.append(f"{year}: entrate negative")
            if r is not None and e is not None and v is not None and not math.isclose(r*e,v,rel_tol=1e-6,abs_tol=0.01): errors.append(f"{year}: rapporto e flussi incoerenti")
    f=doc.get("features")
    if f is not None:
        if not isinstance(f,dict) or set(f)!=set(FEATURES): errors.append("Sono richieste le 42 feature dello schema dimostrativo")
        elif any(number(v) is None for v in f.values()): errors.append("Feature non finite")
    return errors
