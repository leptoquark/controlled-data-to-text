"""Shared administration grouping used by both the interface and the recipes."""

def typology(doc):
    value=str(doc.get('tipologia_put') or doc.get('categoria') or 'Tipologia non disponibile').strip()
    known={'COMUNE':'Comune','ENTE STRUMENTALE':'Ente strumentale','UNIONE_COMUNI':'Unione di Comuni','CITTA_METROP':'Città metropolitana','CONSIGLI_REG':'Consiglio regionale'}
    return known.get(value,value.replace('_',' ').capitalize() if value.isupper() else value)

def group_profiles(profiles):
    groups={}
    for i,doc in enumerate(profiles): groups.setdefault(typology(doc),[]).append(i)
    return {kind:sorted(indices,key=lambda i:profiles[i]['denominazione'].casefold()) for kind,indices in groups.items()}
