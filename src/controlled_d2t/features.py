"""Observed features only; this is not the 42-column laboratory model schema."""
import math
from .schema import number, validate

def extract_observed_features(profile):
    errors=validate(profile)
    if errors: raise ValueError('; '.join(errors))
    def log_value(key):
        value=number(profile.get(key))
        return math.log1p(value) if value is not None and value>=0 else None
    keys=['indice_medio_debito_su_entrate','indice_efficienza','importo_appalti_media','popolazione_media']
    annual=profile.get('valori_annuali',{})
    features={
        'territoriale':float(profile['territoriale']) if isinstance(profile.get('territoriale'),bool) else None,
        'pop_log':log_value('popolazione_media'),
        'entrate_log':log_value('entrate_medie'),
        'anni_disponibili':float(len(annual)),
        'quota_mancanti':sum(number(profile.get(key)) is None for key in keys)/len(keys),
        'personale_presente':float(number(profile.get('PERSONALE')) is not None),
        'appalti_presenti':float(number(profile.get('importo_appalti_media')) is not None),
        'score_efficienza':number(profile.get('indice_efficienza')),
        'score_sostenibilita':number(profile.get('indice_sostenibilita')),
        'score_rischio':number(profile.get('indice_rischio')),
    }
    last=max((int(year) for year in annual),default=None)
    for lag in range(1,9):
        # Only adjacent calendar years: never bridge gaps or invent missing trends.
        year=last-lag+1 if last is not None else None
        recent=number(annual.get(str(year),{}).get('debito_su_entrate'))
        previous=number(annual.get(str(year-1),{}).get('debito_su_entrate')) if year is not None else None
        features[f'trend_debito_pp_{lag}']=(recent-previous)*100 if recent is not None and previous is not None else None
    return features
