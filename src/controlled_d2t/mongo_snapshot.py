"""Read-only export of an allowlisted dashboard profile to an offline snapshot."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from .legacy import _is_territoriale
from .schema import validate

FIELDS = ['codice_ente','denominazione','categoria','tipologia_put','Codice_Categoria_IPA','Descr_Categoria_IPA',
          'indice_medio_debito_su_entrate','debito_su_entrate_media','entrate_medie','variazione_media',
          'popolazione_media','importo_appalti_media','anticipazioni_medie','indice_efficienza',
          'indice_sostenibilita','indice_rischio','PERSONALE','media_regionale_media',
          'valori_annuali','narrazione_breve_md','narrazione_estesa_md']
NUMERIC = ['indice_medio_debito_su_entrate','entrate_medie','variazione_media','popolazione_media',
           'importo_appalti_media','anticipazioni_medie','indice_efficienza','indice_sostenibilita','indice_rischio','PERSONALE']

def finite(value):
    if value is None or isinstance(value,bool): return None
    try:
        from decimal import Decimal
        if hasattr(value,'to_decimal'): value=value.to_decimal()
        if not isinstance(value,(int,float,Decimal)): return None
        value=float(value)
        return value if math.isfinite(value) else None
    except (TypeError,ValueError,OverflowError): return None

def adapt(source):
    doc={key:source.get(key) for key in ['denominazione','categoria','tipologia_put','narrazione_breve_md','narrazione_estesa_md']}
    doc['codice_ente']=str(source.get('codice_ente') or '')
    for key in NUMERIC: doc[key]=finite(source.get(key))
    if source.get('indice_medio_debito_su_entrate') is None:
        doc['indice_medio_debito_su_entrate']=finite(source.get('debito_su_entrate_media'))
    regional=source.get('media_regionale_media') or {}
    doc['media_regionale_rapporto']=finite(regional.get('debito_su_entrate')) if isinstance(regional,dict) else None
    doc['territoriale']=_is_territoriale(source)
    doc['synthetic']=False
    doc['data_origin']='indicatori.debito_media'
    annual=source.get('valori_annuali') or {}
    if not isinstance(annual,dict): raise ValueError('valori_annuali non è un oggetto')
    doc['valori_annuali']={}
    for year,row in sorted(annual.items(),key=lambda item:str(item[0])):
        if not isinstance(row,dict): raise ValueError('Record annuale non valido')
        doc['valori_annuali'][str(year)]={key:finite(row.get(key)) for key in ['debito_su_entrate','entrate_correnti','variazione_debito','importo_appalti']}
    return doc

def export_snapshot(uri='mongodb://127.0.0.1:27017',database='indicatori',collection='debito_media',output='data/real'):
    from pymongo import MongoClient
    client=MongoClient(uri,serverSelectionTimeoutMS=5000,appname='dashboard-readonly-export')
    try:
        cursor=client[database][collection].find({'rappresentabile':True},{'_id':0,**{key:1 for key in FIELDS}}).sort('codice_ente',1)
        docs=[]; rejected=[]; seen=0
        for source in cursor:
            seen+=1
            try:
                doc=adapt(source); doc['data_origin']=database+'.'+collection
                errors=validate(doc)
                if errors: raise ValueError('; '.join(errors))
                docs.append(doc)
            except (ValueError,TypeError) as exc:
                rejected.append({'codice_ente':str(source.get('codice_ente','')),'reason':str(exc)})
        if not docs: raise ValueError('Nessun profilo valido: snapshot precedente non modificato')
        text=''.join(json.dumps(d,ensure_ascii=False,allow_nan=False)+'\n' for d in docs)
        manifest={'kind':'mongodb_snapshot','source_database':database,'source_collection':collection,
                  'query':{'rappresentabile':True},'exported_at_utc':datetime.now(timezone.utc).isoformat(),
                  'records_read':seen,'records_exported':len(docs),'records_rejected':len(rejected),
                  'profiles_with_original_text':sum(bool(d.get('narrazione_estesa_md')) for d in docs),
                  'sha256':hashlib.sha256(text.encode()).hexdigest(),
                  'normalization':'Non-finite numeric values become null; input zeros preserved; explicit 0–100 indices; no feature or label fabrication.',
                  'years':sorted({year for d in docs for year in d['valori_annuali']})}
        out=Path(output); out.mkdir(parents=True,exist_ok=True)
        temp=out/'profiles.jsonl.tmp'; temp.write_text(text,encoding='utf-8',newline='\n'); temp.replace(out/'profiles.jsonl')
        (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'rejected.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2),encoding='utf-8')
        return manifest
    finally: client.close()

def main():
    p=argparse.ArgumentParser(description='Copia in sola lettura i profili dashboard per uso offline')
    p.add_argument('--uri',default='mongodb://127.0.0.1:27017'); p.add_argument('--database',default='indicatori')
    p.add_argument('--collection',default='debito_media'); p.add_argument('--output',default='data/real')
    a=p.parse_args()
    print(json.dumps(export_snapshot(a.uri,a.database,a.collection,a.output),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
