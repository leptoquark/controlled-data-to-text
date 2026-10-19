import copy
from controlled_d2t.synthetic import make_dataset
from controlled_d2t.engine import generate
from controlled_d2t.legacy import narrazione_cittadina
from controlled_d2t.schema import FEATURES, validate

def profile(): return make_dataset(1,42)[0]
def test_determinism_and_provenance():
    d=profile(); a=generate(d); b=generate(copy.deepcopy(d))
    assert a==b and a['blocks']
    assert all(x['evidence'] and x['template_id'] for x in a['blocks'])
def test_zero_is_preserved():
    d=profile(); d['indice_medio_debito_su_entrate']=0
    result=generate(d)
    block=next(b for b in result['blocks'] if b['id']=='debito')
    assert '0,000' in block['text'] and 'equilibrio' in block['text']
    assert 'non ha un indicatore disponibile' not in narrazione_cittadina(d)['breve']
def test_missing_is_not_zero():
    d=profile(); d['indice_medio_debito_su_entrate']=None
    assert 'debito' not in [b['id'] for b in generate(d)['blocks']]
def test_invalid_arithmetic_blocks_output():
    d=profile(); next(iter(d['valori_annuali'].values()))['variazione_debito']=999999999
    assert generate(d)['status']=='blocked'
def test_nonfinite_and_out_of_range_block():
    for value in [float('nan'),float('inf'),'50',True,101,-1]:
        d=profile(); d['indice_efficienza']=value
        assert generate(d)['status']=='blocked'
def test_model_cannot_force_missing_evidence():
    d=profile(); d['importo_appalti_media']=None
    r=generate(d,{'appalti':True},confidence=.95)
    assert not r['blocks']
def test_schema_and_synthetic_accounting():
    docs=make_dataset(100)
    assert len(FEATURES)==42
    assert all(not validate(d) and d['synthetic'] for d in docs)
def test_annual_order_invariance():
    d=profile(); a=generate(d); d['valori_annuali']=dict(reversed(list(d['valori_annuali'].items())))
    assert generate(d)==a
def test_rules_route_for_human_review():
    assert generate(profile())['human_review_required']
