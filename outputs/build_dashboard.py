"""Rebuild the offline judge dashboard from the notebook's LEAD cell model."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
L = pd.read_csv(ROOT / 'data/raw/lead/VA FPL Counties 2022.csv').rename(columns={
    'HINCP*UNITS':'inc_x','ELEP*UNITS':'el_x','GASP*UNITS':'gas_x','FULP*UNITS':'ful_x',
    'HINCP UNITS':'inc_u','ELEP UNITS':'el_u','GASP UNITS':'gas_u','FULP UNITS':'ful_u',
    'FPL150':'fpl','TEN-HFL':'fuel'})
for k in ['inc','el','gas','ful']:
    L[k] = np.where(L[k+'_u']>0,L[k+'_x']/L[k+'_u'],np.nan)
    for keys in (['FIP','fpl','TEN'],['fpl']):
        g=L.groupby(keys)
        L[k]=L[k].fillna(g[k+'_x'].transform('sum')/g[k+'_u'].transform('sum'))
L=L[L.UNITS>0].copy()
f=(97720/81310)**(4/5)
L['income']=L.inc.clip(lower=0)*f
L['kwh']=L.el/.1334
L['cost']=L.kwh*.1683+(L.gas+L.ful)*f
L['fuel']=L.fuel.str.replace('^(OWNER|RENTER) ','',regex=True)
bands=['0-100%','100-150%','150-200%','200-400%','400%+']
fuels=sorted(L.fuel.unique().tolist())
names=L.groupby('FIP').NAME.first().to_dict()
rows=[[int(r.FIP),bands.index(r.fpl),fuels.index(r.fuel),r.UNITS,r.income,r.kwh,r.cost] for r in L.itertuples()]
assert np.isfinite(np.array(rows,dtype=float)).all()
for surcharge,expected in [(0,749.2499402442835),(14,826.0978209597216),(37,954.5829706553144)]:
    li=L.fpl.isin(bands[:2])
    gap=(np.maximum(0,L.cost+L.kwh*surcharge/1000-.06*L.income)*L.UNITS)[li].sum()/1e6
    assert abs(gap-expected)<.00001,(gap,expected)
data=json.dumps(dict(rows=rows,bands=bands,fuels=fuels,names=names),separators=(',',':'),allow_nan=False)
template=(ROOT/'outputs/dashboard.template.html').read_text(encoding='utf8')
(ROOT/'outputs/interactive_presentation_graphs.html').write_text(template.replace('__DATA__',data),encoding='utf8')
print(f'Built dashboard: {len(rows):,} cells; 2026 and both 2040 gap benchmarks match notebook.')
