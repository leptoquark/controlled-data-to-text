import hashlib
import html
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from controlled_d2t.engine import generate
from controlled_d2t.synthetic import load
from controlled_d2t.schema import BLOCKS, validate, number

ROOT=Path(__file__).parent
LABELS={'introduzione':'Presentazione','diagnosi':'Quadro complessivo','indici':'Indici sintetici','debito':'Debito e rimborsi','entrate':'Entrate correnti','popolazione':'Popolazione','trend':'Andamento nel tempo','anni_significativi':'Anni significativi','appalti':'Appalti','tesoreria':'Tesoreria','confronti':'Confronto territoriale'}
MODELS={'weighted_committee':'Comitato pesato','random_forest':'Random Forest','majority_committee':'Comitato a maggioranza','rule_only':'Regole di disponibilità'}

def italian(value, decimals=0):
    if number(value) is None: return 'Non disponibile'
    return f'{value:,.{decimals}f}'.replace(',','_').replace('.',',').replace('_','.')

def money(value):
    if number(value) is None: return 'Non disponibile'
    if abs(value)>=1e9: return italian(value/1e9,2)+' mld €'
    if abs(value)>=1e6: return italian(value/1e6,2)+' mln €'
    return italian(value)+' €'

def section(kicker,title,description=None):
    st.markdown(f'<div class="section-kicker">{html.escape(kicker)}</div>',unsafe_allow_html=True)
    st.subheader(title)
    if description: st.caption(description)

def typology(doc):
    value=str(doc.get('tipologia_put') or doc.get('categoria') or 'Tipologia non disponibile').strip()
    known={'COMUNE':'Comune','ENTE STRUMENTALE':'Ente strumentale','UNIONE_COMUNI':'Unione di Comuni','CITTA_METROP':'Città metropolitana','CONSIGLI_REG':'Consiglio regionale'}
    return known.get(value,value.replace('_',' ').capitalize() if value.isupper() else value)

st.set_page_config(page_title='Trasparenza · Dati e spiegazioni',page_icon='◈',layout='wide')
st.markdown('<style>'+ (ROOT/'assets/style.css').read_text(encoding='utf-8')+'</style>',unsafe_allow_html=True)

@st.cache_data
def examples(dataset_path,dataset_version): return load(dataset_path)

with st.sidebar:
    st.markdown('<div class="brand">Trasparenza.</div><div class="brand-note">Dai dati alle spiegazioni.<br>Una lettura chiara delle amministrazioni.</div>',unsafe_allow_html=True)
    real_path=ROOT/'data/real/profiles.jsonl'
    sources=(['Dati dashboard (copia locale)'] if real_path.exists() else [])+['Laboratorio dimostrativo']
    source=st.selectbox('Dati da consultare',sources,key='data_source')
    st.markdown('<div class="sidebar-label">IL PERCORSO</div><div class="sidebar-step"><span>1</span>Scegli un’amministrazione</div><div class="sidebar-step"><span>2</span>Leggi dati e spiegazioni</div><div class="sidebar-step"><span>3</span>Esplora le evidenze</div>',unsafe_allow_html=True)

is_real=source=='Dati dashboard (copia locale)'
dataset_path=real_path if is_real else ROOT/'data/synthetic.jsonl'
docs=examples(str(dataset_path),dataset_path.stat().st_mtime_ns)
manifest=json.loads(real_path.with_name('manifest.json').read_text(encoding='utf-8')) if is_real else None
st.markdown(f'<div class="intro"><div><div class="eyebrow">Dati pubblici · Spiegazioni verificabili</div><h1>I numeri diventano<br>informazioni comprensibili.</h1><p>Esplora il profilo di un’amministrazione, leggi le spiegazioni e scopri quali dati sostengono ogni affermazione.</p></div><div class="intro-stat"><strong>{italian(len(docs))}</strong><span>amministrazioni consultabili</span></div></div>',unsafe_allow_html=True)
if is_real:
    st.markdown(f'<div class="context-line"><span class="pill pill-accent">● Dati della dashboard</span><span class="pill">Copia locale · {html.escape(manifest["exported_at_utc"][:10])}</span><span class="pill">Disponibile senza connessione al database</span></div>',unsafe_allow_html=True)
    with st.sidebar.expander('Origine e aggiornamento'): st.json(manifest)
else:
    st.info('Stai esplorando il laboratorio: profili ed etichette sono simulati. Le sue metriche non valutano i dati della dashboard.')

tab1,tab2,tab3=st.tabs(['Amministrazioni','Risultati e confronti','Come funziona'])
with tab1:
    section('01 · Esplora','Scegli l’amministrazione','Seleziona prima la tipologia, poi cerca l’amministrazione per nome o codice nell’elenco filtrato.')
    groups={}
    for i,doc in enumerate(docs): groups.setdefault(typology(doc),[]).append(i)
    types=sorted(groups,key=str.casefold)
    default_type=max([kind for kind in types if kind.startswith('Comune')] or types,key=lambda kind:len(groups[kind]))
    if st.session_state.get('administration_type') not in groups:
        st.session_state['administration_type']=default_type
    type_column,entity_column=st.columns([1,2])
    with type_column:
        selected_type=st.selectbox('1. Tipologia di amministrazione',types,format_func=lambda kind:f'{kind} ({italian(len(groups[kind]))})',key='administration_type')
    ordered=sorted(groups[selected_type],key=lambda i:docs[i]['denominazione'].casefold())
    if st.session_state.get('administration') not in ordered:
        st.session_state['administration']=ordered[0]
    with entity_column:
        chosen=st.selectbox('2. Amministrazione · cerca per nome o codice',ordered,format_func=lambda i:docs[i]['denominazione']+' · '+docs[i]['codice_ente'],key='administration')
    st.caption(f'{italian(len(ordered))} amministrazioni nella tipologia selezionata.')
    try:
        with st.expander('Usa un altro profilo o modifica i dati'):
            st.caption('Opzione avanzata: carica un file JSON o modifica il profilo per una nuova generazione. I testi originali restano riferiti alla copia della dashboard.')
            uploaded=st.file_uploader('Carica un profilo JSON',type=['json'])
            doc=json.loads(uploaded.getvalue()) if uploaded else docs[chosen]
            edited=st.text_area('Profilo di ingresso',value=json.dumps(doc,ensure_ascii=False,indent=2),height=280)
        profile=json.loads(edited)
        errors=validate(profile)
        if errors:
            st.error('Controlla il profilo: '+'; '.join(errors))
        else:
            kind=profile.get('tipologia_put') or ('Comune' if profile.get('categoria')=='COMUNE' else 'Amministrazione')
            if kind=='Altro': kind='Amministrazione'
            st.markdown(f'<div class="entity-name">{html.escape(profile["denominazione"])}</div><div class="entity-meta">{html.escape(str(kind))} · Codice {html.escape(profile["codice_ente"])}</div>',unsafe_allow_html=True)
            annual=profile.get('valori_annuali',{})
            years=sorted(annual,key=int)
            ratio=number(profile.get('indice_medio_debito_su_entrate'))
            cols=st.columns(4)
            cols[0].metric('Entrate correnti medie',money(profile.get('entrate_medie')),help='Media delle entrate correnti nelle annualità disponibili.')
            cols[1].metric('Popolazione media',italian(profile.get('popolazione_media')) if profile.get('territoriale') else 'Non applicabile',help='Numero medio di residenti; disponibile per gli enti territoriali.')
            cols[2].metric('Flusso netto / entrate',italian(ratio*100,2)+'%' if ratio is not None else 'Non disponibile',help='Rapporto medio: un valore negativo indica rientro netto, uno positivo ricorso netto. Non è lo stock di debito.')
            cols[3].metric('Periodo disponibile',f'{years[0]}–{years[-1]}' if len(years)>1 else years[0] if years else 'Non disponibile',help=f'{len(years)} annualità nel profilo; eventuali lacune sono visibili nel grafico.')
            st.caption('Gli importi descrivono flussi e medie del periodo disponibile. Il rapporto non misura il debito residuo complessivo.')

            left,right=st.columns([1.65,1],gap='large')
            with left:
                section('02 · Comprendi','La spiegazione della dashboard','Il testo già disponibile nella fonte, conservato insieme ai dati del profilo.')
                with st.container(border=True):
                    if not uploaded and is_real:
                        st.markdown(doc.get('narrazione_breve_md') or 'La fonte non contiene una spiegazione breve.')
                    else:
                        st.markdown('Per questo profilo puoi creare una spiegazione nella sezione **Genera una nuova lettura**, qui sotto.')
                if not uploaded and is_real:
                    with st.expander('Leggi la spiegazione originale completa'):
                        st.markdown(doc.get('narrazione_estesa_md') or 'La fonte non contiene una spiegazione estesa.')
            with right:
                section('Il profilo in sintesi','Tre indici, tre prospettive','Scala 0–100. Il rischio si legge in senso opposto a efficienza e sostenibilità.')
                with st.container(border=True):
                    for name,key,note in [('Efficienza','indice_efficienza','Impiego delle risorse'),('Sostenibilità','indice_sostenibilita','Equilibrio tra debito ed entrate'),('Rischio','indice_rischio','Un valore maggiore indica più rischio')]:
                        score=number(profile.get(key))
                        st.markdown(f'**{name}** · {italian(score,1)}'+(' / 100' if score is not None else ''))
                        if score is not None: st.progress(score/100)
                        st.caption(note)
                st.caption('Le definizioni e le formule degli indici provengono dalla pipeline dei dati. Questa vista non certifica la qualità della gestione.')

            section('03 · Osserva','Come cambia il rapporto nel tempo','Valori percentuali per annualità. La linea dello zero separa rientro netto e ricorso netto al debito.')
            rows=[{'Anno':int(y),'Rapporto (%)':number(v.get('debito_su_entrate'))*100 if number(v.get('debito_su_entrate')) is not None else None} for y,v in annual.items()]
            if rows and any(r['Rapporto (%)'] is not None for r in rows):
                import altair as alt
                frame=pd.DataFrame(rows).sort_values('Anno')
                # Fill calendar gaps with nulls: do not interpolate missing years.
                frame=frame.set_index('Anno').reindex(range(min(frame['Anno']),max(frame['Anno'])+1)).rename_axis('Anno').reset_index()
                chart=alt.Chart(frame).mark_line(point=True,color='#087e83',strokeWidth=3).encode(x=alt.X('Anno:O',title='Anno'),y=alt.Y('Rapporto (%):Q',title='Flusso netto di debito / entrate (%)'),tooltip=[alt.Tooltip('Anno:O'),alt.Tooltip('Rapporto (%):Q',format='.2f')])
                zero=alt.Chart(pd.DataFrame({'zero':[0]})).mark_rule(color='#879ea9',strokeDash=[5,5]).encode(y='zero:Q')
                st.altair_chart((chart+zero).properties(height=250),width='stretch')
            else: st.info('Non sono disponibili rapporti annuali per questo profilo.')

            section('04 · Approfondisci','Genera una nuova lettura','Il testo viene composto da regole e template. Ogni blocco resta collegato alle informazioni che lo sostengono.')
            options=['Regole di disponibilità']
            if profile.get('synthetic') is True and 'features' in profile: options.append('Comitato ML dimostrativo')
            mode=st.radio('Modalità di selezione dei contenuti',options,horizontal=True)
            if profile.get('synthetic') is not True: st.caption('Per i profili della dashboard sono utilizzate le regole. Il modello del laboratorio non viene applicato a questi dati.')
            fingerprint=hashlib.sha256((json.dumps(profile,sort_keys=True,ensure_ascii=False)+mode).encode()).hexdigest()
            if st.button('Genera spiegazione',type='primary'):
                selected=None; confidence=None; diagnostics=None
                if mode.startswith('Comitato'):
                    from controlled_d2t.experiment import predict,probabilities,matrix
                    with (ROOT/'results/latest/model.local.pkl').open('rb') as f: bundle=pickle.load(f)
                    probabilities_by_block=predict(bundle,[profile])[0]
                    selected=dict(zip(BLOCKS,probabilities_by_block>=0.5))
                    confidence=float(np.mean(abs(probabilities_by_block-0.5)*2))
                    votes=np.array([probabilities(m,matrix([profile]))[0] for m in bundle['members']])
                    diagnostics=pd.DataFrame({'Contenuto':[LABELS[b] for b in BLOCKS],'Random Forest':votes[0],'Gradient Boosting':votes[1],'Extra Trees':votes[2],'Comitato':probabilities_by_block})
                result=generate(profile,selected,confidence)
                st.session_state['generated_reading']={'fingerprint':fingerprint,'result':result,'diagnostics':diagnostics}
            cached=st.session_state.get('generated_reading',{})
            if cached.get('fingerprint')==fingerprint:
                result=cached['result']
                if result['status']=='blocked': st.error('Generazione bloccata: '+'; '.join(result['errors']))
                else:
                    st.info('Bozza da revisionare prima della pubblicazione.' if result['human_review_required'] else 'Controlli automatici completati. La bozza non viene pubblicata automaticamente.')
                    with st.container(border=True):
                        for block in result['blocks']:
                            st.markdown('#### '+LABELS[block['id']])
                            st.markdown(block['text'])
                    c1,c2=st.columns(2)
                    c1.download_button('Scarica la spiegazione',result['text'],'spiegazione.txt',width='stretch')
                    c2.download_button('Scarica testo ed evidenze',json.dumps(result,ensure_ascii=False,indent=2),'spiegazione.json','application/json',width='stretch')
                    with st.expander('Perché questi contenuti?'):
                        decisions=pd.DataFrame([{'Contenuto':LABELS[d['block']],'Esito':'Incluso' if d['included'] else 'Escluso','Motivo':{'included':'Dati disponibili e contenuto selezionato','missing_data_or_inapplicable':'Dati mancanti o contenuto non applicabile','selector_omitted':'Non selezionato dal modello'}[d['reason']]} for d in result['decisions']])
                        st.dataframe(decisions,hide_index=True,width='stretch')
                        if cached['diagnostics'] is not None: st.dataframe(cached['diagnostics'],hide_index=True)
                    with st.expander('Dati e regole a sostegno delle frasi'):
                        st.caption('Per ciascun blocco sono conservati identificativo del template, regola e dati utilizzati.')
                        st.json(result['blocks'])
            else:
                st.markdown('<div class="empty-state">La nuova spiegazione apparirà qui.<br>Scegli la modalità e premi <strong>Genera spiegazione</strong>.</div>',unsafe_allow_html=True)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        st.error('Impossibile elaborare il profilo: '+str(exc))

with tab2:
    section('Valutazione','Risultati, con il loro contesto','I risultati pubblicati e quelli del laboratorio si riferiscono a dataset e protocolli diversi. Non sono un confronto diretto.')
    paper=json.loads((ROOT/'results/paper_reported.json').read_text(encoding='utf-8'))
    with st.container(border=True):
        st.subheader('Lo studio pubblicato')
        c1,c2,c3=st.columns(3)
        c1.metric('Amministrazioni nello studio',italian(paper['administrations']))
        c2.metric('Micro F1 · comitato completo','0,901',help='Equilibrio tra precisione e richiamo aggregando le decisioni sui blocchi. Più è vicino a 1, meglio è.')
        c3.metric('Testi valutati da esperti',str(paper['human_evaluation']['texts']))
        st.caption(paper['notice'])
        frame=pd.DataFrame(paper['ablation']).rename(columns={'configurazione':'Configurazione','micro_f1':'Micro F1','macro_f1':'Macro F1','micro_precision':'Precisione micro','micro_recall':'Richiamo micro'})
        st.dataframe(frame,hide_index=True,width='stretch')
        st.markdown('[Leggi il paper originale ↗](https://claudiobiancalana.it/assets/publications/biancalana-sbicca-ital-ia-2026.pdf)')
    section('Laboratorio','Gli esperimenti riproducibili','Questa sezione verifica il funzionamento della pipeline su profili e policy simulati, separati dalla copia della dashboard.')
    path=ROOT/'results/latest/metrics.json'
    if path.exists():
        report=json.loads(path.read_text(encoding='utf-8'))
        st.info(report['warning'])
        cols=st.columns(3)
        for col,key,label in zip(cols,['train','validation','test'],['Profili di addestramento','Profili di validazione','Profili di test']): col.metric(label,italian(report['split'][key]))
        st.caption('Micro F1 aggrega tutte le decisioni. Macro F1 attribuisce lo stesso peso a ciascun blocco, facendo emergere anche i contenuti più difficili.')
        table=pd.DataFrame([{'Configurazione':MODELS[k],'Micro F1':v['micro_f1'],'Macro F1':v['macro_f1'],'Precisione':v['micro_precision'],'Richiamo':v['micro_recall']} for k,v in report['metrics'].items()])
        st.dataframe(table,hide_index=True,width='stretch')
        st.subheader('Quanto funziona per ciascun contenuto?')
        st.caption('F1 va da 0 a 1. Una media alta può nascondere prestazioni deboli su singoli blocchi.')
        block_frame=pd.DataFrame({'Contenuto':[LABELS[b] for b in report['per_block_f1']],'F1':list(report['per_block_f1'].values())})
        import altair as alt
        st.altair_chart(alt.Chart(block_frame).mark_bar(color='#087e83',cornerRadiusEnd=4).encode(x=alt.X('F1:Q',scale=alt.Scale(domain=[0,1])),y=alt.Y('Contenuto:N',sort='-x',title=None),tooltip=['Contenuto',alt.Tooltip('F1:Q',format='.3f')]).properties(height=330),width='stretch')
        with st.expander('Dettagli dell’esperimento e importanza delle variabili'):
            st.caption('L’importanza delle variabili descrive il comportamento globale dei modelli. Non è una spiegazione causale o del singolo caso.')
            importance=json.loads((ROOT/'results/latest/feature_importance.json').read_text())
            st.bar_chart(pd.Series(importance).sort_values(ascending=False).head(15),color='#087e83')
            st.json({k:v for k,v in report.items() if k not in ['metrics','per_block_f1']})
    else: st.info('Nessun esperimento locale disponibile. La guida descrive come eseguirlo.')

with tab3:
    section('Il metodo','Dai dati al testo, un passaggio alla volta','Le spiegazioni sono costruite con regole esplicite. Puoi controllare cosa è stato usato e perché.')
    steps=[('01','Leggi il profilo','Gli indicatori e le serie annuali descrivono l’amministrazione nel periodo disponibile.'),('02','Seleziona i contenuti','Le regole verificano quali argomenti possono essere sostenuti dai dati.'),('03','Componi e controlla','I template producono il testo; i controlli verificano struttura e coerenza numerica.'),('04','Rivedi e condividi','La bozza e le evidenze possono essere esportate per la revisione umana.')]
    for col,(n,title,body) in zip(st.columns(4),steps):
        col.markdown(f'<div class="process-card"><small>PASSAGGIO {n}</small><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>',unsafe_allow_html=True)
    st.subheader('Tre cose da sapere')
    st.markdown('- **Stessi dati, stesso testo:** la selezione delle varianti è deterministica.\n- **Ogni frase ha una base:** le evidenze restano collegate al blocco narrativo.\n- **Il controllo umano resta centrale:** l’applicazione non pubblica automaticamente le bozze.')
    with st.expander('Metodologia completa, limiti e riuso'):
        st.markdown((ROOT/'docs/METHOD.md').read_text(encoding='utf-8'))
    with st.expander('Come aggiornare la copia locale dei dati'):
        st.markdown((ROOT/'docs/OFFLINE_DATA.md').read_text(encoding='utf-8'))

st.markdown('<div class="footer">Trasparenza · Dati, spiegazioni e provenienza in un unico spazio. La consultazione usa i file locali inclusi nell’applicazione.</div>',unsafe_allow_html=True)
