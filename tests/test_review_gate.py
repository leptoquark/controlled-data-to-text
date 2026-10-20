"""Invalid confidence must never bypass the demonstrator's review routing."""
import pytest
from controlled_d2t.engine import generate
from controlled_d2t.synthetic import make_dataset

@pytest.mark.parametrize('key', ['confidence', 'threshold'])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), -0.01, 1.01, True, '0.9'])
def test_invalid_gate_inputs_block_output(key, value):
    result=generate(make_dataset(1)[0], **{key:value})
    assert result['status']=='blocked'
    assert not result['text'] and result['human_review_required']
    assert result['publication_authorized'] is False

@pytest.mark.parametrize('confidence,threshold,review', [(None,.6,True),(0,0,False),(.59,.6,True),(.6,.6,False),(1,1,False)])
def test_gate_boundaries_and_publication_scope(confidence,threshold,review):
    result=generate(make_dataset(1)[0],confidence=confidence,threshold=threshold)
    assert result['human_review_required'] is review
    assert result['publication_authorized'] is False
    assert result['validation_scope']['source_truth_verified'] is False
    assert result['validation_scope']['historical_aggregates_reconciled'] is False
    assert result['status']==('review_required' if review else 'automated_checks_passed_draft')

@pytest.mark.parametrize('value', ['false','true',0,1])
def test_territoriality_is_not_coerced(value):
    profile=make_dataset(1)[0];profile['territoriale']=value
    assert generate(profile)['status']=='blocked'

def test_aggregate_reconciliation_is_explicitly_out_of_scope():
    profile=make_dataset(1)[0];profile['indice_medio_debito_su_entrate']=999
    result=generate(profile)
    assert result['validation_scope']['historical_aggregates_reconciled'] is False
    assert result['publication_authorized'] is False
