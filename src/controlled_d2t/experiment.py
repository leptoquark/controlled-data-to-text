import hashlib
import json
import platform
from pathlib import Path
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from .schema import FEATURES, BLOCKS, validate

def matrix(docs):
    for d in docs:
        errors=validate(d)
        if errors: raise ValueError('; '.join(errors))
        if 'features' not in d: raise ValueError('Il selettore ML richiede le 42 feature esplicite; usare regole per profili senza feature.')
    return np.array([[d['features'][k] for k in FEATURES] for d in docs])
def metrics(y,p):
    return {f'{avg}_{name}':float(fun(y,p,average=avg,zero_division=0)) for avg in ['micro','macro'] for name,fun in [('f1',f1_score),('precision',precision_score),('recall',recall_score)]}
def fit_member(kind,x,y,seed):
    models=[]
    for j in range(y.shape[1]):
        if len(np.unique(y[:,j]))<2: model=DummyClassifier(strategy='most_frequent')
        elif kind=='rf': model=RandomForestClassifier(n_estimators=80,max_depth=9,random_state=seed,n_jobs=-1)
        elif kind=='et': model=ExtraTreesClassifier(n_estimators=80,max_depth=10,random_state=seed,n_jobs=-1)
        else: model=GradientBoostingClassifier(n_estimators=50,max_depth=2,random_state=seed)
        models.append(model.fit(x,y[:,j]))
    return models
def probabilities(models,x):
    cols=[]
    for m in models:
        p=m.predict_proba(x)
        cols.append(p[:,list(m.classes_).index(1)] if 1 in m.classes_ else np.zeros(len(x)))
    return np.array(cols).T
def predict(bundle,docs):
    ps=np.array([probabilities(m,matrix(docs)) for m in bundle['members']])
    return np.average(ps,axis=0,weights=bundle['weights'])
def run(docs,out,seed=42,bootstrap=200):
    import pickle
    x=matrix(docs); y=np.array([[d['labels'][b] for b in BLOCKS] for d in docs])
    # Entity-level random split. Not the unavailable paper's multilabel-stratified split.
    if len({d['codice_ente'] for d in docs})!=len(docs): raise ValueError('Identificativi duplicati: possibile leakage tra split')
    train,rest=train_test_split(np.arange(len(docs)),test_size=0.3,random_state=seed)
    val,test=train_test_split(rest,test_size=0.5,random_state=seed)
    members=[fit_member(k,x[train],y[train],seed) for k in ['rf','gb','et']]
    pv=np.array([probabilities(m,x[val]) for m in members])
    # AdaBoost-inspired member weights from validation error; not a claim of exact paper replication.
    err=np.mean((pv>=0.5)!=y[val],axis=(1,2))
    weights=np.maximum(0.01,np.log((1-np.clip(err,1e-6,1-1e-6))/np.clip(err,1e-6,1-1e-6)))
    bundle={'members':members,'weights':weights,'features':FEATURES,'blocks':BLOCKS,'seed':seed,'sklearn':sklearn.__version__}
    pt=np.array([probabilities(m,x[test]) for m in members])
    full=np.average(pt,axis=0,weights=weights)
    from .engine import generate
    baseline=np.array([[int(t['included']) for t in generate(docs[i])['decisions']] for i in test])
    predictions={'weighted_committee':full>=0.5,'random_forest':pt[0]>=0.5,'majority_committee':np.sum(pt>=0.5,axis=0)>=2,'rule_only':baseline}
    rng=np.random.default_rng(seed)
    boot=[f1_score(y[test][ix],predictions['weighted_committee'][ix],average='micro',zero_division=0) for ix in [rng.integers(0,len(test),len(test)) for _ in range(bootstrap)]]
    report={'data_kind':'SYNTHETIC','label_source':'synthetic_policy_v1','warning':'Queste metriche misurano apprendimento di una policy simulata, non validazione su enti reali o replica del paper.', 'seed':seed,'dataset_sha256':hashlib.sha256(json.dumps(docs,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'split':{'train':len(train),'validation':len(val),'test':len(test)},'split_method':'entity_unique_random_70_15_15','metrics':{k:metrics(y[test],v) for k,v in predictions.items()},'micro_f1_ci95':np.quantile(boot,[0.025,0.975]).tolist(),'bootstrap_repetitions':bootstrap,'per_block_f1':dict(zip(BLOCKS,f1_score(y[test],predictions['weighted_committee'],average=None,zero_division=0).tolist())),'weights':dict(zip(['rf','gb','et'],weights.tolist())),'reliability':{'kind':'uncalibrated_selection_margin','review_threshold':0.6,'mean_test_margin':float(np.mean(abs(full-0.5)*2))},'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,'numpy':np.__version__}}
    p=Path(out); p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (p/'splits.json').write_text(json.dumps({name:[docs[i]['codice_ente'] for i in ix] for name,ix in [('train',train),('validation',val),('test',test)]},indent=2),encoding='utf-8')
    with (p/'model.local.pkl').open('wb') as f: pickle.dump(bundle,f)
    # Explicit feature importances: tree model global importance, not causal or local explanations.
    importance=np.mean([m.feature_importances_ for member in members for m in member if hasattr(m,'feature_importances_')],axis=0)
    (p/'feature_importance.json').write_text(json.dumps(dict(zip(FEATURES,importance.tolist())),indent=2),encoding='utf-8')
    return report
