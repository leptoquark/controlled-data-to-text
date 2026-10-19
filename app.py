import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from controlled_d2t.engine import generate
from controlled_d2t.synthetic import load
from controlled_d2t.schema import BLOCKS, validate
ROOT=Path(__file__).parent
st.set_page_config(page_title="Data-to-text controllato",layout="wide")
st.title("Data-to-text controllato")
st.caption("Framework dimostrativo • testi da template • selezione dei blocchi ispezionabile")
@st.cache_data
def examples(dataset_path,dataset_version): return load(dataset_path)

real_path=ROOT/'data/real/profiles.jsonl'
sources=(['Dati dashboard (copia locale)'] if real_path.exists() else [])+['Laboratorio dimostrativo']
source=st.sidebar.selectbox('Origine dei profili',sources,key='data_source')
is_real=source=='Dati dashboard (copia locale)'
dataset_path=real_path if is_real else ROOT/'data/synthetic.jsonl'
if is_real:
    manifest_path=real_path.with_name('manifest.json')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    st.caption(f"Copia locale di {manifest['source_database']}.{manifest['source_collection']} • {manifest['records_exported']:,} amministrazioni • aggiornamento {manifest['exported_at_utc'][:10]} • nessuna connessione al database")
    with st.sidebar.expander('Dettagli della copia locale'): st.json(manifest)
else:
    st.warning('Profili dimostrativi e policy simulate. Le metriche del laboratorio non valutano i dati della dashboard.')
tab1,tab2,tab3=st.tabs(['Genera e ispeziona','Risultati','Metodo e riuso'])
with tab1:
    docs=examples(str(dataset_path),dataset_path.stat().st_mtime_ns)
    chosen=st.selectbox('Amministrazione',sorted(range(len(docs)),key=lambda i:docs[i]['denominazione'].casefold()),format_func=lambda i:docs[i]['denominazione']+' · '+docs[i]['codice_ente'],key='administration')
    uploaded=st.file_uploader('Oppure carica un profilo JSON',type=['json'])
    try:
        doc=json.loads(uploaded.getvalue()) if uploaded else docs[chosen]
        if not uploaded and is_real:
            with st.expander('Spiegazioni originali della dashboard',expanded=True):
                st.markdown(doc.get('narrazione_breve_md') or 'Testo breve non disponibile.')
            with st.expander('Spiegazione originale estesa'):
                st.markdown(doc.get('narrazione_estesa_md') or 'Testo esteso non disponibile.')
        edited=st.text_area('Profilo di ingresso (modificabile)',value=json.dumps(doc,ensure_ascii=False,indent=2),height=260)
        profile=json.loads(edited)
        options=['Regole di disponibilità']
        if profile.get('synthetic') is True and 'features' in profile: options.append('Comitato ML dimostrativo')
        mode=st.radio('Selettore',options,horizontal=True)
        if profile.get('synthetic') is not True: st.caption('Generazione dai dati disponibili. Il modello dimostrativo non è applicato ai profili della dashboard.')
        if st.button('Genera spiegazione',type='primary'):
            errors=validate(profile)
            if errors: st.error('; '.join(errors))
            else:
                selected=None; confidence=None; diagnostics=None
                if mode.startswith('Comitato'):
                    from controlled_d2t.experiment import predict,probabilities,matrix
                    # Only bundled local models. Never deserialize uploaded pickle files.
                    with (ROOT/'results/latest/model.local.pkl').open('rb') as f: bundle=pickle.load(f)
                    p=predict(bundle,[profile])[0]
                    selected=dict(zip(BLOCKS,p>=0.5)); confidence=float(np.mean(abs(p-0.5)*2))
                    votes=np.array([probabilities(m,matrix([profile]))[0] for m in bundle['members']])
                    diagnostics=pd.DataFrame({'blocco':BLOCKS,'RF':votes[0],'GB':votes[1],'ET':votes[2],'comitato':p})
                result=generate(profile,selected,confidence)
                st.info('Stato: '+result['status']+' — nessuna pubblicazione automatica')
                if profile.get('synthetic') is True: st.caption('Profilo dichiarato sintetico')
                elif not uploaded and is_real: st.caption('Profilo esportato dalla dashboard; verifiche strutturali e numeriche applicate alla nuova spiegazione.')
                else: st.caption('Profilo caricato dall’utente: origine non verificata')
                st.text(result['text'])
                if diagnostics is not None: st.dataframe(diagnostics,hide_index=True)
                st.subheader('Decisioni sui blocchi'); st.dataframe(result['decisions'],hide_index=True)
                st.subheader('Tracciabilità delle affermazioni'); st.json(result['blocks'])
                st.download_button('Scarica testo',result['text'],'spiegazione.txt')
                st.download_button('Scarica rapporto completo',json.dumps(result,ensure_ascii=False,indent=2),'spiegazione.json','application/json')
    except (ValueError,KeyError,TypeError,OSError) as exc: st.error(str(exc))
with tab2:
    st.subheader('Risultati pubblicati nel paper')
    paper=json.loads((ROOT/'results/paper_reported.json').read_text(encoding='utf-8'))
    st.caption(paper['notice']); st.dataframe(pd.DataFrame(paper['ablation']),hide_index=True)
    st.markdown('[Paper originale](https://claudiobiancalana.it/assets/publications/biancalana-sbicca-ital-ia-2026.pdf)')
    st.subheader('Esperimento locale su dati sintetici')
    path=ROOT/'results/latest/metrics.json'
    if path.exists():
        report=json.loads(path.read_text(encoding='utf-8')); st.warning(report['warning'])
        st.dataframe(pd.DataFrame(report['metrics']).T)
        st.bar_chart(pd.Series(report['per_block_f1'],name='F1 sintetico'))
        st.json({k:v for k,v in report.items() if k not in ['metrics','per_block_f1']})
        st.caption('Importanza globale delle feature: non è una spiegazione causale o del singolo caso.')
        st.bar_chart(pd.Series(json.loads((ROOT/'results/latest/feature_importance.json').read_text())).sort_values(ascending=False).head(15))
    else: st.info('Eseguire d2t experiment per produrre risultati locali.')
with tab3:
    st.markdown((ROOT/'docs/METHOD.md').read_text(encoding='utf-8'))
