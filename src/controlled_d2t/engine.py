import hashlib
import json
from pathlib import Path
from .schema import BLOCKS, validate, number

DEFAULT_TEMPLATES=Path(__file__).with_name("templates.json")
def fmt(v):
    return "non disponibile" if number(v) is None else f"{v:,.3f}".replace(",","_").replace(".",",").replace("_",".")
def generate(doc, selected=None, confidence=None, threshold=0.6, template_path=None):
    errors=validate(doc)
    if errors: return {"status":"blocked","errors":errors,"text":"","blocks":[],"decisions":[]}
    templates=json.loads(Path(template_path or DEFAULT_TEMPLATES).read_text(encoding="utf-8"))
    ratio=number(doc.get("indice_medio_debito_su_entrate"))
    annual=sorted([(str(y),number(v.get("debito_su_entrate"))) for y,v in doc.get("valori_annuali",{}).items() if number(v.get("debito_su_entrate")) is not None],key=lambda pair:int(pair[0]))
    peak=max(annual,key=lambda pair:abs(pair[1])) if annual else (None,None)
    fields={"introduzione":["denominazione"],"diagnosi":["indice_efficienza","indice_sostenibilita","indice_rischio"],"indici":["indice_efficienza","indice_sostenibilita","indice_rischio"],"debito":["indice_medio_debito_su_entrate"],"entrate":["entrate_medie"],"popolazione":["popolazione_media","territoriale"],"trend":["valori_annuali"],"anni_significativi":["valori_annuali"],"appalti":["importo_appalti_media"],"tesoreria":["anticipazioni_medie"],"confronti":["indice_medio_debito_su_entrate","media_regionale_rapporto","territoriale"]}
    available={b:all(doc.get(k) is not None for k in fields[b]) for b in BLOCKS}
    available.update(introduzione=True,indici=any(number(doc.get(k)) is not None for k in fields["indici"]),popolazione=bool(doc.get("territoriale")) and number(doc.get("popolazione_media")) is not None,trend=len(annual)>=3,anni_significativi=len(annual)>=2,confronti=bool(doc.get("territoriale")) and ratio is not None and number(doc.get("media_regionale_rapporto")) is not None)
    args=dict(nome=doc["denominazione"],eff=fmt(doc.get("indice_efficienza")),sost=fmt(doc.get("indice_sostenibilita")),risk=fmt(doc.get("indice_rischio")),ratio=fmt(ratio),direction="equilibrio" if ratio==0 else ("rientro netto" if ratio is not None and ratio<0 else "ricorso netto"),income=fmt(doc.get("entrate_medie")),population=fmt(doc.get("popolazione_media")),procurement=fmt(doc.get("importo_appalti_media")),treasury=fmt(doc.get("anticipazioni_medie")),regional=fmt(doc.get("media_regionale_rapporto")),first=fmt(annual[0][1]) if annual else "n.d.",last=fmt(annual[-1][1]) if annual else "n.d.",first_year=annual[0][0] if annual else "n.d.",last_year=annual[-1][0] if annual else "n.d.",peak_year=peak[0],peak=fmt(peak[1]))
    blocks=[]; decisions=[]
    for b in BLOCKS:
        requested=selected is None or bool(selected.get(b,False))
        include=available[b] and requested
        decisions.append({"block":b,"requested":requested,"available":available[b],"included":include,"reason":"included" if include else "missing_data_or_inapplicable" if not available[b] else "selector_omitted"})
        if not include: continue
        variants=templates[b]
        index=int(hashlib.sha256((doc["codice_ente"]+":"+b).encode()).hexdigest(),16)%len(variants)
        text=variants[index].format(**args)
        blocks.append({"id":b,"template_id":f"{b}.v{index+1}","rule_id":b+".availability.v1","text":text,"evidence":{k:doc.get(k) for k in fields[b]}})
    canonical=json.dumps(doc,sort_keys=True,ensure_ascii=False,allow_nan=False)
    # This score is a conservative model agreement measure, NOT a calibrated probability of factuality.
    review=confidence is None or confidence<threshold
    return {"status":"review_required" if review else "validated_draft","errors":[],"confidence":confidence,"confidence_kind":"uncalibrated_selection_margin" if confidence is not None else "unavailable", "human_review_required":review,"validation":"typed_values_and_annual_arithmetic; surface_numbers_formatted_from_evidence","input_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"templates_sha256":hashlib.sha256(json.dumps(templates,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),"blocks":blocks,"decisions":decisions,"text":"\n\n".join(b["text"] for b in blocks)}
