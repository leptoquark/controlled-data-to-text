"""Profili fittizi; etichette da policy simulata, mai da esperti."""
import json
from pathlib import Path
import numpy as np
from .schema import FEATURES, INDICATORS, BLOCKS

def entity_name(index, territorial):
    roots=["Borgo", "Monte", "Valle", "Poggio", "Colle", "Castel", "Piano", "Fonte", "Rocca", "Prato", "Bosco", "Lago", "Rio", "Campo", "Ponte", "Porto"]
    endings=["chiaro", "sereno", "verde", "fiorito", "dorato", "alto", "bello", "largo", "nuovo", "antico", "quieto", "rotondo", "bianco", "lungo", "santo", "vivo", "ombroso", "aperto", "profondo", "azzurro"]
    districts=["del Piano", "sul Rio", "dei Colli", "della Valle", "al Monte", "delle Fonti", "del Bosco", "sul Lago"]
    place=roots[index%len(roots)]+endings[(index//len(roots))%len(endings)]+" "+districts[(index//(len(roots)*len(endings)))%len(districts)]
    kind="Comune di" if territorial else ["Agenzia territoriale per i servizi di", "Consorzio per lo sviluppo di", "Ente per il patrimonio di", "Azienda per i servizi ambientali di"][(index//3)%4]
    return kind+" "+place

def make_dataset(n=1200, seed=42):
    rng=np.random.default_rng(seed)
    docs=[]
    for i in range(n):
        territorial=bool(rng.random()<0.75)
        pop=int(np.clip(rng.lognormal(9,1.4),500,2000000)) if territorial else None
        income=float(round(pop*rng.uniform(900,2200) if territorial else np.clip(rng.lognormal(16.5,1.1),2000000,800000000),2))
        annual={}
        initial=rng.uniform(-0.25,0.35); drift=rng.normal(0,0.04)
        for j in range(int(rng.integers(1,7))):
            e=round(income*rng.uniform(0.8,1.2),2)
            ratio=float(initial+j*drift+rng.normal(0,0.025))
            annual[str(2019+j)]={"debito_su_entrate":ratio,"entrate_correnti":e,"variazione_debito":ratio*e}
        ratios=[v["debito_su_entrate"] for v in annual.values()]
        ratio=float(np.mean(ratios)); eff=float(rng.uniform(0,100))
        sust=float(np.clip(100-abs(ratio)*200,0,100)); risk=float(np.clip(abs(ratio)*180+rng.normal(10,8),0,100))
        income=float(np.mean([v["entrate_correnti"] for v in annual.values()]))
        procurement=float(round(income*rng.uniform(0.08,0.45),2)) if rng.random()<0.85 else None
        staff=max(3,int(round(pop*rng.uniform(0.004,0.009) if territorial else income*rng.uniform(0.15,0.35)/rng.uniform(50000,75000)))) if rng.random()<0.9 else None
        d={"codice_ente":f"SYN-{i:06d}","denominazione":entity_name(i,territorial),"categoria":"COMUNE" if territorial else "ENTE STRUMENTALE", "synthetic":True,"territoriale":territorial,
            "popolazione_media":pop,"entrate_medie":income,"indice_medio_debito_su_entrate":ratio,
            "variazione_media":float(np.mean([v["variazione_debito"] for v in annual.values()])),
            "valori_annuali":annual,"importo_appalti_media":procurement,"PERSONALE":staff,
            "anticipazioni_medie":float(income*rng.uniform(0,0.1)) if rng.random()<0.4 else None,
            "indice_efficienza":eff,"indice_sostenibilita":sust,"indice_rischio":risk,
            "media_regionale_rapporto":float(rng.uniform(-0.1,0.2)) if territorial else None}
        # Realistic missingness; do not substitute zero for missing measurements.
        if rng.random()<0.12: d["indice_medio_debito_su_entrate"]=None
        if rng.random()<0.08: d["indice_efficienza"]=None
        missing=sum(d.get(k) is None for k in ["indice_medio_debito_su_entrate","indice_efficienza","importo_appalti_media","popolazione_media"])/4
        vals=[float(territorial),float(np.log1p(pop or 0)),float(np.log1p(income)),len(annual),missing,float(staff is not None),float(procurement is not None)]
        scores=rng.uniform(0,100,15); scores[:3]=[eff,sust,risk]
        trends=np.clip(rng.normal(drift*100,8,8),-100,100)
        percentiles=rng.uniform(0,100,12)
        d["features"]={k:float(v) for k,v in zip(FEATURES,vals+list(scores)+list(trends)+list(percentiles))}
        # A hypothetical editorial policy: this is NOT human ground truth.
        labels=[True, missing<0.55 and (risk>35 or eff<65),True,
                d["indice_medio_debito_su_entrate"] is not None,True,
                territorial and pop is not None,len(annual)>=3 and (abs(drift)>0.012 or sust<60),
                len(annual)>=2 and (risk>35 or abs(ratio)>0.12),
                procurement is not None and (procurement/income>0.15 or eff<50),
                d["anticipazioni_medie"] is not None,territorial and abs(ratio-d["media_regionale_rapporto"])>0.06]
        d["labels"]={k:int(v) for k,v in zip(BLOCKS,labels)}
        d["label_source"]="synthetic_policy_v1"
        docs.append(d)
    return docs

def save(docs,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(''.join(json.dumps(d,ensure_ascii=False,allow_nan=False)+'\n' for d in docs),encoding='utf-8')
def load(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
