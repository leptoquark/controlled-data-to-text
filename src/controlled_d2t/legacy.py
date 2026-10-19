"""Funzioni estratte dall'archivio fornito dall'utente: nessuna connessione DB.
Compatibilità storica; non usare come percorso validato. Vedere PROVENANCE.md.
"""
from statistics import mean
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import math

def _sec(x: Optional[float]) -> float:
    # safe to float, NaN -> 0
    return 0.0 if (x is None or (isinstance(x, (int, float)) and math.isnan(x))) else float(x)

def _near_zero(v: Optional[float], eps: float = 1e-6) -> bool:
    return abs(_sec(v)) <= eps

def _fmt_euro(v: Optional[float], dec: int = 0) -> str:
    if v is None:
        return "n.d."
    return f"{v:,.{dec}f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def _fmt_num(v: Optional[float], dec: int = 0) -> str:
    if v is None:
        return "n.d."
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _safe_ratio(num: Optional[float], den: Optional[float]) -> Optional[float]:
    num = _sec(num); den = _sec(den)
    if den == 0:
        return None
    return num / den

def _approx_str(x: Optional[float], dec:int=3) -> str:
    if x is None:
        return "n.d."
    if _near_zero(x, 10**(-dec)):
        return "≈ 0"
    return f"{x:.{dec}f}"

def _seed(doc: Dict[str, Any]) -> int:
    key = (doc.get("codice_ente") or doc.get("cf") or doc.get("denominazione") or "x").encode("utf-8")
    return int(hashlib.sha1(key).hexdigest(), 16)

def _pick(variants: List[str], seed: int, tag: str) -> str:
    # scelta deterministica basata su hash(tag+seed)
    h = int(hashlib.sha1((str(seed)+":"+tag).encode("utf-8")).hexdigest(), 16)
    return variants[h % len(variants)]

SYN_OPENING = [
    "Questa scheda racconta in modo semplice come **{nome}** ha gestito debiti e rimborsi negli ultimi anni.",
    "Di seguito trovi una spiegazione chiara sulla gestione del debito di **{nome}**.",
    "Ecco una lettura sintetica dei dati su debito e rimborsi per **{nome}**."
]

SYN_FRAME = [
    "Immagina il bilancio come il conto di casa: se restituisci più di quanto prendi in prestito, stai rientrando dal debito.",
    "Pensiamo al bilancio come a un salvadanaio: tra soldi presi e restituiti, l’equilibrio indica una gestione prudente.",
    "Un po’ come un mutuo: conta quanti soldi rimborsiamo rispetto a quelli che prendiamo in prestito."
]

SYN_BAL_EQUIL = [
    "**In media il bilancio è in equilibrio** tra nuovi debiti e rimborsi (saldo medio vicino allo zero).",
    "**Nel complesso prevale l’equilibrio**: tra accensioni e rimborsi, il saldo medio tende allo zero.",
    "**Equilibrio medio**: i nuovi debiti e i rimborsi si compensano quasi perfettamente."
]

SYN_INTENSITY_LABELS = {
    "trascurabile": ["trascurabile", "minima", "molto contenuta"],
    "molto contenuta": ["molto contenuta", "bassa"],
    "bassa": ["bassa", "moderata"],
    "media": ["media"],
    "alta": ["alta"],
    "molto alta": ["molto alta"],
    "eccezionalmente alta": ["eccezionalmente alta"]
}

def _var_label(label: str, seed: int) -> str:
    # restituisce una variante sinonimica stabile
    options = SYN_INTENSITY_LABELS.get(label, [label])
    return _pick(options, seed, "int_"+label)

def _article_for(name: str) -> str:
    # Articolo determinativo sensibile a vocale/cons.
    if not name:
        return "l’ente"
    n = name.strip().upper()
    if n.startswith(("A","E","I","O","U")):
        return "l’ente"
    # casi particolari noti
    if "AUTORIT" in n:
        return "l’Autorità"
    if "COMUNE" in n:
        return "il Comune"
    return "l’ente"

TERR_KEYWORDS = {
    "territoriali": [
        "COMUNE", "PROVINCIA", "REGIONE", "CITTA", "CITTÀ METROPOLITANA",
        "UNIONE", "COMUNITA", "COMUNITÀ", "CONSORZIO TRA COMUNI"
    ],
    "autorita": ["AUT_INDIP", "AUTORITA", "AUTORITÀ", "AUTORITA'"],
}

def _is_territoriale(doc: Dict[str, Any]) -> bool:
    """
    Determina se l’ente è 'territoriale' (Comune, Provincia, Regione, Unione, Comunità, Città Metropolitana, ecc.)
    oppure un ente non territoriale (Autorità, Ministeri, enti strumentali, società, fondazioni, scuole, sanità, università…).

    Logica multilivello:
    1. Usa categoria IPA se presente.
    2. Usa categoria PUT/tipologia_put.
    3. Analizza la denominazione.
    4. Come fallback, considera la popolazione > 0 ma solo se non contraddetta.
    """

    # --- 1. Lettura valori utili ---
    categoria = (doc.get("categoria") or "").upper()
    tipologia_put = (doc.get("tipologia_put") or "").upper()
    ipa_cat = (doc.get("Codice_Categoria_IPA") or "").upper()
    ipa_desc = (doc.get("Descr_Categoria_IPA") or "").upper()
    name = (doc.get("denominazione") or "").upper()
    pop = _sec(doc.get("popolazione_media"))

    text = " ".join([categoria, tipologia_put, ipa_cat, ipa_desc, name])

    # --- 2. Categorie IPA territoriali esplicite ---
    IPA_TERR = [
        "COMUNE", "REGIONE", "PROVINCIA", "CITTA METROPOLITANA", "CITTÀ METROPOLITANA",
        "UNIONE DI COMUNI", "COMUNITA MONTANA", "COMUNITÀ MONTANA",
        "CONSORZIO TRA COMUNI"
    ]

    # Categorie IPA chiaramente non territoriali
    IPA_NON_TERR = [
        "AUTORITA", "AUTORITÀ", "ASL", "AZIENDA SANITARIA", "MINISTERO",
        "UNIVERSITA", "UNIVERSITÀ", "INPS", "INAIL", "AGENZIA", "CAMERA DI COMMERCIO",
        "ENTE PUBBLICO NON ECONOMICO", "ENTE STRUMENTALE", "ISTITUTO", "SCUOLA"
    ]

    # --- Regola 1: se categoria IPA è nota completamente ---
    if any(k in text for k in IPA_TERR):
        return True
    if any(k in text for k in IPA_NON_TERR):
        return False

    # --- 3. Tipologia PUT ---
    PUT_TERR = [
        "COMUNE", "PROVINCIA", "REGIONE",
        "UNIONE DI COMUNI", "COMUNITA", "CITTÀ METROPOLITANA"
    ]

    PUT_NON_TERR = [
        "AZIENDA", "FONDAZIONE", "UNIVERSITA", "ASL", "OSPEDALE", "CONSORZIO",
        "SOCIETA", "AUTORITA", "AUTORITÀ", "ENTE STRUMENTALE"
    ]

    if any(x in tipologia_put for x in PUT_TERR):
        return True
    if any(x in tipologia_put for x in PUT_NON_TERR):
        return False

    # --- 4. Analisi sul nome dell’ente ---
    NAME_TERR = ["COMUNE DI", "COMUNE", "REGIONE", "PROVINCIA", "CITTÀ METROPOLITANA"]
    NAME_NON_TERR = ["AUTORITA", "ASL", "AZIENDA", "FONDAZIONE", "UNIVERSITA", "UNIVERSITÀ",
                     "S.R.L", "SPA", "ISTITUTO", "SCUOLA"]

    if any(k in name for k in NAME_TERR):
        return True
    if any(k in name for k in NAME_NON_TERR):
        return False

    # --- 5. Fallback basato sulla popolazione ---
    # Popolazione > 0 = quasi certamente territoriale, ma evito se altri campi suggeriscono azienda/autorità
    if pop > 0:
        if not any(x in text for x in ["AUTORITA", "ASL", "UNIVERSITA", "AZIENDA", "S.R.L", "SPA"]):
            return True

    # --- 6. Default: non territoriale ---
    return False

def _attore_label(doc: Dict[str, Any], territoriale: bool) -> str:
    """
    Restituisce il soggetto giusto per la narrazione (il Comune, la Regione, l’Autorità, l’ente…)
    """

    cat = (doc.get("categoria") or "").upper()
    nome = (doc.get("denominazione") or "").upper()

    # CASO 1 — TERRITORIALI
    if territoriale:
        if "COMUNE" in cat or "COMUNE" in nome:
            return "il Comune"
        if any(k in cat for k in ["REGIONE", "PROVINCIA", "CITTÀ METROPOLITANA"]):
            return "l’amministrazione"
        return "l’ente"

    # CASO 2 — NON TERRITORIALI
    # Autorità indipendenti
    if any(k in nome for k in ["AUTORITA", "AUTORITÀ", "AUT_INDIP"]):
        return "l’Autorità"

    # Sanità
    if "ASL" in nome or "AZIENDA SANITARIA" in nome:
        return "l’azienda sanitaria"

    # Università
    if "UNIVERSITA" in nome or "UNIVERSITÀ" in nome:
        return "l’Università"

    # Società pubbliche
    if any(k in nome for k in ["S.R.L", "SRL", "S.P.A", "SPA"]):
        return "la società"

    # Enti di ricerca, fondazioni, enti strumentali
    if any(k in nome for k in ["FONDAZIONE", "ISTITUTO", "ENTE"]):
        return "l’ente"

    # fallback
    return "l’ente"

def _intensita_label(val: Optional[float]) -> str:
    """Intensità in base al valore assoluto del rapporto debito/entrate."""
    if val is None or _near_zero(val):
        return "trascurabile"
    v = abs(_sec(val))
    if v < 0.05:  return "molto contenuta"
    if v < 0.15:  return "bassa"
    if v < 0.30:  return "media"
    if v < 0.60:  return "alta"
    if v < 1.00:  return "molto alta"
    return "eccezionalmente alta"

def _segno_spiegazione(val: Optional[float], attore: str) -> str:
    """Spiega il segno del rapporto in parole semplici, con soggetto dinamico."""
    x = _sec(val)
    if x < -1e-9:
        return f"{attore} ha **restituito più debiti di quanti ne abbia accesi** (rientro netto)"
    if x >  1e-9:
        return f"{attore} ha **fatto più ricorso al debito** di quanto abbia rimborsato (ricorso netto)"
    return f"{attore} è stato **in equilibrio** tra nuovi debiti e rimborsi"

def _per_100_euro(val: Optional[float], attore: str) -> str:
    """Traduce il rapporto in 'per 100€ di entrate' con tono cittadino (+ soggetto dinamico)."""
    if val is None:
        return "Manca un dato utile per il raffronto su 100 € di entrate."
    if _near_zero(val):
        return f"Per ogni **100 €** incassati, il conto è stato **in equilibrio**: nuovi debiti e rimborsi si sono compensati."
    v = abs(val) * 100
    v = round(v, 1)
    if _sec(val) < 0:
        return f"Per ogni **100 €** incassati, {attore} ne ha usati **circa {v} € per ridurre il debito**."
    else:
        return f"Per ogni **100 €** incassati, {attore} ha **preso in prestito netto** circa **{v} €**."

def _trend_sintetico(serie: List[float]) -> str:
    """Confronta media inizio vs fine periodo: verso lo 0 = miglioramento per il cittadino."""
    if len(serie) < 3:
        return "L’andamento nel tempo **non è valutabile** con pochi anni disponibili."
    head = serie[:2] if len(serie) >= 4 else serie[:1]
    tail = serie[-2:]
    m1, m2 = mean(head), mean(tail)
    if abs(m2) < abs(m1) - 1e-9:
        return "Nel tempo, la situazione **è migliorata**: ci si è avvicinati all’equilibrio (rapporto → 0)."
    if abs(m2) > abs(m1) + 1e-9:
        return "Nel tempo, la situazione **è peggiorata**: ci si è allontanati dallo zero."
    return "Nel complesso, la situazione è rimasta **abbastanza stabile**."

def _best_worst(ann: Dict[str, Any]) -> Dict[str, Optional[str]]:
    pairs = []
    for y, v in ann.items():
        r = v.get("debito_su_entrate")
        if r is not None:
            pairs.append((y, r))
    if not pairs:
        return {"best": None, "worst": None}
    # vicino allo zero = "best"
    best = min(pairs, key=lambda kv: abs(kv[1]))
    worst = max(pairs, key=lambda kv: abs(kv[1]))
    best_str  = f"Anno più vicino all’equilibrio: **{best[0]}** (rapporto debito/entrate { _approx_str(best[1]) })."
    worst_str = f"Anno con scostamento maggiore: **{worst[0]}** (rapporto debito/entrate {worst[1]:.3f})."
    return {"best": best_str, "worst": worst_str}

def _anni_significativi(ann: Dict[str, Any]) -> List[str]:
    """
    Elenca fino a 3 anni 'parlanti':
    - anni con saldo (variazione_debito) quasi zero -> 'in equilibrio'
    - anni con scostamenti marcati (per modulo)
    """
    if not ann:
        return []
    try:
        years = sorted((int(y) for y in ann.keys()))
    except Exception:
        years = list(ann.keys())
    scored = []
    for y in years:
        key = str(y)
        va = ann.get(key, {})
        var = _sec(va.get("variazione_debito"))
        ent = _sec(va.get("entrate_correnti"))
        ratio = abs(var) / ent if ent > 0 else abs(var)
        scored.append((key, var, ent, ratio))

    scored.sort(key=lambda t: t[3], reverse=True)

    pick = []
    pick.extend(scored[:2])
    if scored:
        pick.append(min(scored, key=lambda t: abs(t[1])))

    seen = set()
    comp = []
    for y, var, ent, _ in pick:
        if y in seen:
            continue
        seen.add(y)
        if _near_zero(var):
            comp.append(f"- **{y}**: saldo **in equilibrio** (nessuno scostamento rilevante).")
        else:
            verso = "rientro (riduzione del debito)" if var < 0 else "ricorso al debito"
            comp.append(f"- **{y}**: saldo **{_fmt_euro(var, 0)}** → {verso}.")
    return comp[:3]

def _norm01_100(v: Optional[float]) -> Optional[float]:
    """Riporta in scala 0..100 anche se arriva come 0..1; None se non valido."""
    if v is None:
        return None
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return None
        if x < 0:
            x = 0.0
        if x <= 1.0:
            x *= 100.0
        return min(100.0, x)
    except Exception:
        return None

def _label_index(score: Optional[float]) -> str:
    s = _norm01_100(score)
    if s is None:
        return "n.d."
    if s < 20:  return "molto bassa"
    if s < 40:  return "bassa"
    if s < 60:  return "media"
    if s < 80:  return "alta"
    return "molto alta"

def _sent_index(name: str, score: Optional[float]) -> str:
    lab = _label_index(score)
    if name == "eff":
        return f"**Efficienza**: {lab} (stima dell’impiego delle risorse rispetto ai costi di personale; se il personale è assente, si usa un proxy sugli appalti)."
    if name == "sost":
        return f"**Sostenibilità**: {lab} (equilibrio tra debito e entrate)."
    if name == "rsk":
        if lab == "molto alta": desc = "molto elevato"
        elif lab == "alta":     desc = "elevato"
        elif lab == "media":    desc = "moderato"
        elif lab == "bassa":    desc = "basso"
        elif lab == "molto bassa": desc = "molto basso"
        else: desc = "n.d."
        return f"**Rischio**: {desc}."
    return "n.d."

def _overall_diagnosis(eff: Optional[float], sost: Optional[float], rsk: Optional[float]) -> str:
    E = _norm01_100(eff); S = _norm01_100(sost); R = _norm01_100(rsk)
    fav = 0
    if E is not None and E >= 60: fav += 1
    if S is not None and S >= 60: fav += 1
    if R is not None and R <= 40: fav += 1

    if (R is not None and R >= 80) or ((E is not None and E < 40) and (S is not None and S < 40)):
        return "Profilo **critico**: rischio elevato e/o debolezza su efficienza e sostenibilità."
    if (R is not None and R >= 60) or (E is not None and E < 40):
        return "Profilo **da monitorare**: vulnerabilità non trascurabili."

    if fav == 3:
        return "Profilo **solido e performante**: buona efficienza, equilibrio e rischio contenuto."
    if fav == 2:
        return "Profilo **complessivamente buono**: prevalgono aspetti positivi, con margini di miglioramento."
    return "Profilo **in equilibrio**: quadro non critico ma con elementi da seguire."

def _pop_sentence(doc: Dict[str, Any], territoriale: bool, seed: int) -> Optional[str]:
    """
    Restituisce una frase SOLO per enti territoriali.
    Gli enti non territoriali (Autorità, ASL, Università, Società, Enti nazionali…)
    non devono avere alcuna frase sulla popolazione.
    """

    pop_med = doc.get("popolazione_media")
    if pop_med is None or _sec(pop_med) <= 0:
        return None

    # SOLO enti territoriali mostrano la popolazione
    if not territoriale:
        return None

    nome = doc.get("denominazione") or ""
    variants = [
        f"La **popolazione media** è di **{_fmt_num(pop_med)} abitanti**.",
        f"In media, il territorio amministrato conta **{_fmt_num(pop_med)} residenti**.",
        f"Il bacino demografico di riferimento è pari a **{_fmt_num(pop_med)} abitanti**."
    ]
    return _pick(variants, seed, "pop_terr")

def _appalti_section(doc: Dict[str, Any], seed:int) -> Optional[List[str]]:
    """
    Restituisce una sezione testuale sugli appalti se disponibili:
    - importo_appalti_media (valore medio)
    - rapporto su 100 € di entrate
    - nota se esiste un delta forte vs entrate
    """
    anni = (doc.get("valori_annuali") or {}) if isinstance(doc.get("valori_annuali"), dict) else {}
    imp_med = doc.get("importo_appalti_media")  # già persistito se presente
    ent_med = doc.get("entrate_medie")
    if imp_med is None or _sec(imp_med) <= 0:
        return None

    lines = []
    lines.append("**Appalti (lettura sintetica)**")
    lines.append(f"- Valore medio annuo degli appalti: **{_fmt_euro(imp_med, 0)}**.")

    ratio = None
    if ent_med and _sec(ent_med) > 0:
        ratio = (imp_med / ent_med) * 100.0
        lines.append(f"- Su **100 € di entrate**, gli appalti pesano in media **{_fmt_num(ratio,1)} €**.")

        # leggere dinamica anni se ci sono importi annui
        # cerco v.importo_appalti in anni
        vals = []
        for y, v in sorted(anni.items(), key=lambda item: str(item[0])):
            ia = v.get("importo_appalti")
            if ia is not None and _sec(ia) > 0:
                vals.append(ia)
        if len(vals) >= 3:
            h = mean(vals[:max(1, len(vals)//3)])
            t = mean(vals[-max(1, len(vals)//3):])
            if t > h * 1.2:
                lines.append("- Negli ultimi anni si osserva una **crescita** del volume di appalti.")
            elif t < h * 0.8:
                lines.append("- Negli ultimi anni si osserva una **riduzione** del volume di appalti.")
            else:
                lines.append("- Il volume degli appalti è rimasto **abbastanza stabile**.")
    else:
        lines.append("- Manca un dato di entrata per stimare il peso per 100 €.")

    return lines

def _eff_fallback_note(doc: Dict[str, Any]) -> Optional[str]:
    """
    Se il personale è 0 o mancante e l'efficienza è quindi stimata via proxy (appalti),
    spiega la scelta metodologica.
    """
    personale   = doc.get("PERSONALE") or doc.get("dipendenti_totali")
    eff         = doc.get("indice_efficienza")
    imp_med     = doc.get("importo_appalti_media")
    if personale is None or _sec(personale) == 0:
        if eff is not None and (imp_med is not None and _sec(imp_med) >= 0):
            return ("*Nota metodologica*: l’**efficienza** è stata stimata con un "
                    "indicatore **di proxy sugli appalti** (quando il personale non è disponibile), "
                    "per rendere il confronto più leggibile.")
    return None

def _ultimi_n_anni(ann: Dict[str, Any], n: int = 5) -> Dict[str, Any]:
    """Restituisce solo le annualità più recenti ordinabili come interi."""
    if not isinstance(ann, dict) or len(ann) <= n:
        return ann if isinstance(ann, dict) else {}
    try:
        ultimi = sorted(ann.keys(), key=lambda y: int(y))[-n:]
        return {y: ann[y] for y in ultimi}
    except Exception:
        return ann

def narrazione_cittadina(doc: Dict[str, Any]) -> Dict[str, str]:
    seed = _seed(doc)
    nome = doc.get("denominazione") or "l’Ente"
    istat = doc.get("codice_istat") or doc.get("cod_istat") or "n.d."
    pop_med = doc.get("popolazione_media")
    idx_m   = doc.get("indice_medio_debito_su_entrate") if doc.get("indice_medio_debito_su_entrate") is not None else doc.get("debito_su_entrate_media")
    var_m   = doc.get("variazione_media")
    ent_m   = doc.get("entrate_medie")
    var_pc  = doc.get("variazione_pro_capite_media")
    ent_pc  = doc.get("entrate_pro_capite_medie")
    ann     = _ultimi_n_anni(doc.get("valori_annuali", {}) or {}, n=5)
    ant_med   = doc.get("anticipazioni_medie")
    rim_ant_m = doc.get("rimborso_anticipazioni_medio")
    q7e_m     = doc.get("quota7_entrate_media")
    q7u_m     = doc.get("quota7_uscite_media")

    territoriale = _is_territoriale(doc)
    attore = _attore_label(doc, territoriale)

    # Serie ordinata per il trend (rapporto debito/entrate)
    try:
        years = sorted(ann.keys(), key=lambda y: int(y))
    except Exception:
        years = list(ann.keys())
    serie_ratio = [ann[y].get("debito_su_entrate") for y in years if ann[y].get("debito_su_entrate") is not None]

    # Blocchi esplicativi
    intensita_base = _intensita_label(idx_m)
    intensita = _var_label(intensita_base, seed)
    segno_txt = _segno_spiegazione(idx_m, attore)
    per100    = _per_100_euro(idx_m, attore)
    trend_txt = _trend_sintetico(serie_ratio)
    bw        = _best_worst(ann)
    anni_sig  = _anni_significativi(ann)

    # Aperture variate
    intro = _pick(SYN_OPENING, seed, "opening").format(nome=nome)
    frame = _pick(SYN_FRAME, seed, "frame")

    # --- Narrazione breve ---
    breve = []
    breve.append(intro)

    if idx_m is None:
        breve.append(f"In media, {attore} **non ha un indicatore disponibile** per il rapporto debito/entrate.")
    elif _near_zero(idx_m):
        breve.append(_pick(SYN_BAL_EQUIL, seed, "equil"))
    else:
        breve.append(f"In media, {segno_txt}. L’intensità è **{intensita}**.")

    if ent_m is not None:
        breve.append(f"Le **entrate correnti** valgono in media **{_fmt_euro(ent_m)}**.")
    breve.append(per100)

    # Popolazione (frase diversa per territoriali / non territoriali)
    pop_sent = _pop_sentence(doc, territoriale, seed)
    if pop_sent:
        if territoriale and var_pc is not None:
            # se territoriale, aggiungi nota pro capite solo se significativa
            if _near_zero(var_pc, eps=0.5):
                breve.append(pop_sent + " L’effetto medio per abitante è **trascurabile**.")
            else:
                breve.append(pop_sent + f" L’effetto medio è **{_fmt_num(var_pc)} € per abitante**.")
        else:
            breve.append(pop_sent)

    breve.append(trend_txt)

    # Nota appalti (brevi cenni)
    appalti = _appalti_section(doc, seed)
    if appalti:
        breve.append("")
        breve.extend(appalti[:2])  # nella breve: prime 2 righe (valore medio + peso su 100€)

    # --- Narrazione estesa ---
    lunga = []
    lunga.append(f"### {nome} (ISTAT {istat})")
    lunga.append("")
    lunga.append(intro)
    lunga.append(frame)
    lunga.append("")

    # Stato medio e chiarezza sull'indice
    if var_m is None and idx_m is None:
        lunga.append("Non è disponibile un riassunto affidabile dei **flussi medi annui**.")
    else:
        if idx_m is not None and _near_zero(idx_m):
            lunga.append(_pick(SYN_BAL_EQUIL, seed, "equil"))
        else:
            if var_m is not None and not _near_zero(var_m, eps=1.0):
                if _sec(idx_m) < 0:
                    lunga.append(f"**In media si è ridotto il debito**: saldo annuo (accensioni − rimborsi) **{_fmt_euro(var_m)}**.")
                elif _sec(idx_m) > 0:
                    lunga.append(f"**In media si è aumentato il debito**: saldo annuo (accensioni − rimborsi) **{_fmt_euro(var_m)}**.")
                else:
                    lunga.append("**In media il bilancio è vicino all’equilibrio**.")
            else:
                lunga.append("Il saldo medio annuo risulta **trascurabile** (nessuno scostamento significativo).")

    lunga.append(f"L’**indice** usato in questa sezione è il **rapporto debito/entrate medio** (segno ±).")
    lunga.append(f"L’intensità del fenomeno è **{intensita}**. {per100}")

    # Entrate e popolazione
    if ent_m is not None:
        lunga.append(f"Le **entrate correnti medie** ammontano a **{_fmt_euro(ent_m)}**.")

    pop_sent_est = _pop_sentence(doc, territoriale, seed)
    if pop_sent_est:
        if territoriale and _sec(pop_med) > 0:
            if var_pc is None:
                lunga.append(pop_sent_est + "; il dato pro capite non è disponibile per tutti gli anni.")
            elif _near_zero(var_pc, eps=0.5):
                lunga.append(pop_sent_est + "; l’effetto medio per abitante è **trascurabile**.")
            else:
                lunga.append(pop_sent_est + f"; ciò equivale, in media, a **{_fmt_num(var_pc)} € per abitante**.")
        else:
            lunga.append(pop_sent_est)

    # Anticipazioni/tesoreria (se presenti)
    if any(x is not None for x in [ant_med, rim_ant_m, q7e_m, q7u_m]):
        lunga.append("")
        lunga.append("**Operazioni di tesoreria (anticipazioni)**")
        if ant_med is not None or rim_ant_m is not None:
            a = _fmt_euro(ant_med) if ant_med is not None else "n.d."
            r = _fmt_euro(rim_ant_m) if rim_ant_m is not None else "n.d."
            if _near_zero(_sec(ant_med)) and not _near_zero(_sec(rim_ant_m)):
                lunga.append(f"- Non si registrano nuove anticipazioni; **rimborsi**: {r}.")
            elif _near_zero(_sec(rim_ant_m)) and not _near_zero(_sec(ant_med)):
                lunga.append(f"- **Anticipazioni**: {a}; non risultano rimborsi di rilievo.")
            else:
                lunga.append(f"- In media, **anticipazioni**: {a}; **rimborsi anticipazioni**: {r}.")
        if q7e_m is not None and q7e_m > 0:
            lunga.append(f"- Peso medio delle anticipazioni sulle **entrate**: **{_fmt_num(q7e_m*100,1)}%**.")
        if q7u_m is not None and q7u_m > 0:
            lunga.append(f"- Peso medio delle anticipazioni sulle **uscite**: **{_fmt_num(q7u_m*100,1)}%**.")

    # Andamento e anni parlanti
    lunga.append("")
    lunga.append("**Come è cambiata la situazione nel tempo?**")
    if len(serie_ratio) >= 1:
        lunga.append(trend_txt)
        if bw["best"]:
            lunga.append(f"- {bw['best']}")
        if bw["worst"] and len(serie_ratio) > 1:
            lunga.append(f"- {bw['worst']}")
        if anni_sig:
            lunga.append("")
            lunga.append("**Anni significativi**")
            lunga.extend(anni_sig)
    else:
        lunga.append("Non sono disponibili rapporti annuali validi: non si può descrivere un andamento.")

    # Sezione appalti (estesa)
    appalti_est = _appalti_section(doc, seed)
    if appalti_est:
        lunga.append("")
        lunga.extend(appalti_est)

    # Nota efficienza (fallback metodologico)
    eff_note = _eff_fallback_note(doc)
    if eff_note:
        lunga.append("")
        lunga.append(eff_note)

    # Confronti territoriali
    prov = doc.get("media_provinciale_media", {}) or {}
    reg  = doc.get("media_regionale_media", {}) or {}
    idx_prov = prov.get("debito_su_entrate")
    idx_reg  = reg.get("debito_su_entrate")
    if territoriale and (idx_prov is not None or idx_reg is not None):
        lunga.append("")
        lunga.append("**Confronti con il territorio (rapporto debito/entrate medio)**")
        if idx_prov is not None and idx_m is not None:
            comp = "più intensa" if abs(_sec(idx_m)) > abs(_sec(idx_prov)) else "meno intensa"
            val_prov = _approx_str(idx_prov)
            val_ente = _approx_str(idx_m)
            lunga.append(f"- Rispetto alla **media provinciale**, la situazione è **{comp}** ({attore}: {val_ente} vs provincia: {val_prov}).")
        if idx_reg is not None and idx_m is not None:
            comp = "più intensa" if abs(_sec(idx_m)) > abs(_sec(idx_reg)) else "meno intensa"
            val_reg  = _approx_str(idx_reg)
            val_ente = _approx_str(idx_m)
            lunga.append(f"- Rispetto alla **media regionale**, la situazione è **{comp}** ({attore}: {val_ente} vs regione: {val_reg}).")

    # Chiusura con note
    lunga.append("")
    lunga.append("**Da ricordare**")
    lunga.append("- I numeri descrivono **flussi annui** (quanto si è preso o restituito), non il debito residuo complessivo.")
    lunga.append("- Valori molto alti o molto bassi possono dipendere da operazioni straordinarie in singoli anni.")
    lunga.append("- L’obiettivo di lungo periodo è avvicinarsi allo **zero**: equilibrio tra nuovi debiti e rimborsi.")

    # ======== Lettura indici sintetici (Efficienza, Sostenibilità, Rischio) ========
    eff = doc.get("indice_efficienza")
    sost = doc.get("indice_sostenibilita")
    rsk = doc.get("indice_rischio")

    eff_s = _sent_index("eff", eff)
    sost_s = _sent_index("sost", sost)
    rsk_s = _sent_index("rsk", rsk)
    combo = _overall_diagnosis(eff, sost, rsk)

    # Nota sintetica (breve)
    breve.append("")
    breve.append("**Lettura sintetica degli indici**")
    breve.append(f"- {eff_s}")
    breve.append(f"- {sost_s}")
    breve.append(f"- {rsk_s}")
    breve.append(combo)

    # Sezione estesa
    lunga.append("")
    lunga.append("### Indici sintetici: come leggere il quadro complessivo")
    lunga.append(f"- {eff_s}")
    lunga.append(f"- {sost_s}")
    lunga.append(f"- {rsk_s}")
    chiose = [
        "Insieme, questi tre numeri offrono un’istantanea della gestione.",
        "La combinazione aiuta a capire se l’ente è efficiente, in equilibrio e poco esposto a rischi.",
        "Gli indici vanno letti insieme: efficienza, equilibrio e rischio descrivono aspetti diversi ma collegati."
    ]
    lunga.append(_pick(chiose, seed, "chiose"))
    lunga.append(combo)

    return {"breve": "\n".join(breve), "lunga": "\n".join(lunga)}