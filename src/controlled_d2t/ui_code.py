"""Lazy code library: static executable recipes, live previews, actual source."""
import inspect
import io
import json
import string
import zipfile
from pathlib import Path
from .features import extract_observed_features
from .selection import group_profiles
from .engine import generate, DEFAULT_TEMPLATES

RECIPES=[
    ('Selezioni','Amministrazioni per tipologia','01_selezione_amministrazione.py',False,'Filtra gli enti con la stessa funzione utilizzata dall’interfaccia.'),
    ('Selezioni','Blocchi narrativi e regole','02_selezione_blocchi.py',False,'Verifica i blocchi disponibili e applica una selezione esplicita dei contenuti.'),
    ('Selezioni','Comitato di classificatori','06_selezione_ml.py',True,'Usa il modello incluso, esclusivamente con i profili del laboratorio.'),
    ('Template','Varianti e template personalizzati','03_template_personalizzati.py',False,'Crea una copia dei template, modifica l’apertura e genera il testo senza cambiare gli originali.'),
    ('Feature','Feature dai dati disponibili','04_feature_osservate.py',False,'Estrai 18 feature osservabili: dati strutturali, tre indici e otto variazioni annuali. I dati mancanti restano null.'),
    ('Feature','Schema del modello: 42 colonne','05_schema_feature_modello.py',True,'Genera le feature del laboratorio e ordinale nella matrice attesa dai classificatori.'),
    ('Pipeline completa','Dal profilo al rapporto esportato','07_pipeline_completa.py',False,'Unisci estrazione delle feature, generazione a regole, testo ed evidenze in file locali.'),
]

def recipe_code(root,filename,profile=None,dataset=None):
    code=(Path(root)/'examples/snippets'/filename).read_text(encoding='utf-8')
    if profile is not None and dataset is not None:
        code=code.replace('DATASET = None', 'DATASET = '+repr(str(dataset)),1)
        code=code.replace('TARGET_CODE = None','TARGET_CODE = '+repr(profile['codice_ente']),1)
    return code

def recipe_bundle(root,profile,dataset):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
        for _,_,filename,demo,_ in RECIPES:
            archive.writestr('examples/snippets/'+filename,recipe_code(root,filename,None if demo else profile,None if demo else dataset))
        archive.writestr('examples/snippets/README.md',(Path(root)/'examples/snippets/README.md').read_text(encoding='utf-8'))
    return buffer.getvalue()

def render_code_library(root,profile,dataset_path):
    import streamlit as st
    root=Path(root)
    relative=Path(dataset_path).relative_to(root).as_posix()
    st.subheader('Codice da leggere, copiare e riutilizzare')
    st.caption('Esempi Python eseguibili dalla cartella del progetto, usando il pacchetto installato. Il pulsante nell’angolo di ciascun riquadro copia il codice.')
    from .colab import NOTEBOOK_PATH, notebook_url, colab_bundle
    with st.container(border=True):
        st.subheader('Esplora il framework in un notebook')
        st.markdown('Un percorso guidato con codice modificabile, selettori interattivi, grafici, esperimenti sui dati mancanti e confronto dei template. Puoi seguirlo in Google Colab oppure in Jupyter.')
        a,b=st.columns(2)
        try:
            a.link_button('Apri il notebook in Colab',notebook_url(),width='stretch')
        except ValueError as exc:
            a.error(str(exc))
        b.download_button('Scarica il notebook .ipynb',(root/NOTEBOOK_PATH).read_bytes(),'controlled_data_to_text.ipynb','application/x-ipynb+json',key='download_notebook',width='stretch')
        st.download_button('Scarica il pacchetto per Colab',colab_bundle(root,profile),'pacchetto-colab.zip','application/zip',key='download_colab_package',width='stretch')
        st.caption('Il pacchetto contiene il codice necessario e una copia del profilo selezionato, non l’intero database. Il download è locale; il caricamento in Colab avviene solo quando lo scegli tu nel notebook.')
        with st.expander('Primo avvio, repository privato e link personalizzato'):
            st.markdown('1. Apri il notebook in Colab. Se il repository privato non è accessibile, scarica il file `.ipynb` e usa **File → Carica notebook** in Colab.\n2. Scarica il pacchetto per Colab dall’applicazione.\n3. Esegui la prima cella del notebook e carica lo ZIP quando richiesto. Le celle successive guidano selezioni, template, feature ed esportazione.')
            st.markdown('[Apri Colab per caricare il notebook](https://colab.research.google.com/)')
            st.caption('Puoi collegare una tua copia salvata su Drive tramite la variabile D2T_COLAB_NOTEBOOK_URL, usando un URL https://colab.research.google.com/drive/… . Il link non modifica i permessi del file.')
            st.code('D2T_COLAB_NOTEBOOK_URL=https://colab.research.google.com/drive/ID_DEL_NOTEBOOK',language='bash')
    st.info('Profilo di riferimento: '+profile['denominazione']+' · '+profile['codice_ente'])
    left,right=st.columns([1,2])
    with left:
        topic=st.selectbox('Argomento',['Selezioni','Template','Feature','Pipeline completa'],key='recipe_topic')
    choices=[row for row in RECIPES if row[0]==topic]
    with right:
        chosen=st.selectbox('Esempio',range(len(choices)),format_func=lambda i:choices[i][1],key='recipe_choice_'+topic)
    _,title,filename,demo,description=choices[chosen]
    st.subheader(title)
    st.markdown(description)
    if demo:
        st.caption('Questo esempio usa il laboratorio e non il profilo della dashboard selezionato. Le 42 feature e il modello non costituiscono una ricostruzione delle feature originali del paper.')
    else:
        st.caption('Lo snippet e il file scaricato includono il codice dell’amministrazione selezionata e il percorso della copia locale. I dati non sono incorporati nel codice.')
    code=recipe_code(root,filename,None if demo else profile,None if demo else relative)
    st.code(code,language='python',line_numbers=True,wrap_lines=True)
    c1,c2=st.columns(2)
    c1.download_button('Scarica questo snippet',code,filename,'text/x-python',key='download_recipe',width='stretch')
    c2.download_button('Scarica tutti gli esempi',recipe_bundle(root,profile,relative),'esempi-data-to-text.zip','application/zip',key='download_recipes',width='stretch')
    with st.expander('Come eseguire lo snippet'):
        st.markdown('Apri un terminale nella cartella principale del progetto e usa l’ambiente Python dell’applicazione.')
        st.code('python -m pip install -e .\npython examples/snippets/'+filename,language='bash')
        st.caption('Salva il file scaricato nella cartella examples/snippets. Gli esempi personalizzati richiedono la stessa copia locale dei dati; gli esempi del laboratorio richiedono i suoi dati e il modello incluso.')

    st.subheader('Cosa produce sul profilo corrente')
    if filename=='04_feature_osservate.py':
        features=extract_observed_features(profile)
        st.dataframe([{'Feature':key,'Valore':str(value) if value is not None else 'Non disponibile'} for key,value in features.items()],hide_index=True,width='stretch')
        st.caption('Quota mancanti: rapporto sui quattro campi dichiarati nell’estrattore. Presenza personale/appalti significa presenza del dato, incluso zero. I trend sono differenze tra anni di calendario consecutivi, in punti percentuali; nessuna interpolazione dei mancanti.')
    elif topic=='Template':
        templates=json.loads(DEFAULT_TEMPLATES.read_text(encoding='utf-8'))
        selected=st.selectbox('Blocco del catalogo template',list(templates),key='template_catalog_block')
        variants=templates[selected]
        st.code(json.dumps({selected:variants},ensure_ascii=False,indent=2),language='json')
        fields=sorted({name for variant in variants for _,name,_,_ in string.Formatter().parse(variant) if name})
        st.caption('Segnaposto utilizzati: '+', '.join(fields))
        result=generate(profile)
        rendered=next((b for b in result['blocks'] if b['id']==selected),None)
        if rendered:
            st.markdown(rendered['text'])
            st.caption('Variante selezionata: '+rendered['template_id'])
        else: st.info('Questo blocco non è applicabile al profilo corrente o non dispone dei dati necessari.')
    elif filename=='02_selezione_blocchi.py':
        st.dataframe(generate(profile)['decisions'],hide_index=True,width='stretch')
    elif filename=='01_selezione_amministrazione.py':
        st.caption('La stessa funzione group_profiles alimenta i due selettori dell’applicazione. Lo snippet elenca i primi dieci enti della tipologia e individua quello scelto per codice.')
    elif demo:
        from .schema import FEATURES
        st.caption('Schema di ingresso del laboratorio: 7 attributi strutturali, 15 score, 8 trend e 12 percentili. I profili reali non vengono completati con numeri inventati.')
        st.code('\n'.join(f'{i+1:02d}  {name}' for i,name in enumerate(FEATURES)),language='text')
    else:
        st.caption('La pipeline salva spiegazione.txt e rapporto.json in work/snippets. Il rapporto contiene feature osservate e provenienza di ogni blocco.')

    if topic=='Feature':
        with st.expander('Definizioni, unità e dati mancanti'):
            st.markdown((root/'docs/FEATURES.md').read_text(encoding='utf-8'))

    with st.expander('Implementazione effettiva del framework'):
        function=extract_observed_features if filename=='04_feature_osservate.py' else group_profiles if filename=='01_selezione_amministrazione.py' else generate
        if filename=='05_schema_feature_modello.py':
            from .synthetic import make_dataset
            function=make_dataset
        elif filename=='06_selezione_ml.py':
            from .experiment import predict
            function=predict
        st.caption('Sorgente letto direttamente dalla funzione installata: '+function.__module__+'.'+function.__name__)
        st.code(inspect.getsource(function),language='python',line_numbers=True,wrap_lines=True)
