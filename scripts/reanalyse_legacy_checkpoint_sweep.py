"""Reanalyse private read-only JSON exports; no server connections.
Input files are described in results/00_model_selection/README.md.
"""
from pathlib import Path
import json,csv,io,itertools
from collections import Counter
import numpy as np
from scipy.stats import wasserstein_distance
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];private=Path(args.source_dir)
ng=next(i for i in json.loads((private/'sources_03.json').read_text()) if i['source_relative_path'].endswith('/data/NG_enhancer_data.csv'))
real=list(dict.fromkeys(r['Sequence'].upper() for r in csv.DictReader(io.StringIO(ng['text'])) if all(c in 'ACGTacgt' for c in r['Sequence'])))
words=[''.join(x) for x in itertools.product('ACGT',repeat=6)]
def kmers(seqs):
 c=Counter(s[j:j+6] for s in seqs for j in range(len(s)-5));return np.array([c[w] for w in words],dtype=float)/sum(c.values())
def gc(s):return (s.count('G')+s.count('C'))/160
ref=kmers(real);refgc=np.array([gc(s) for s in real]);realset=set(real)
legacy=json.loads((private/'sources_ppt_legacy.json').read_text());tables={}
for i in legacy:
 if '/final/test/compare_num_distribution/res_' in i['source_relative_path']:
  model='DDPM' if 'res_DDPM' in i['source_relative_path'] else 'DiT';tables[model]={int(r['epoch']):r for r in csv.DictReader(io.StringIO(i['text'])) if r['epoch']!='real'}
rows=[];sources=json.loads((private/'sources_legacy_all_fasta.json').read_text())
for i in sources:
 model='DDPM' if '/DDPM/' in i['source_relative_path'] else 'DiT';epoch=int(Path(i['source_relative_path']).stem)
 seqs=[l.strip().upper() for l in i['text'].splitlines() if l and not l.startswith('>')];assert len(seqs)==1000 and all(len(s)==160 and set(s)<=set('ACGT') for s in seqs)
 v=kmers(seqs);g=np.array([gc(s) for s in seqs]);pcc=float(np.corrcoef(v,ref)[0,1]);hist=tables[model][epoch]
 rows.append(dict(model=model,epoch=epoch,n=1000,sixmer_pcc=pcc,gc_mean=float(g.mean()),gc_wasserstein=float(wasserstein_distance(g,refgc)),unique_fraction=len(set(seqs))/1000,exact_real_matches=sum(s in realset for s in seqs),jaspar_hits=int(hist['num']),jaspar_categories=int(hist['cat']),jaspar_position_wd=float(hist['wd']),jaspar_hits_per_sequence=int(hist['num'])/1000,sequence_sha256=i['sha256']))
for r in rows:
 r['pareto_nondominated']=int(not any(other['sixmer_pcc']>=r['sixmer_pcc'] and other['gc_wasserstein']<=r['gc_wasserstein'] and other['jaspar_position_wd']<=r['jaspar_position_wd'] and (other['sixmer_pcc']>r['sixmer_pcc'] or other['gc_wasserstein']<r['gc_wasserstein'] or other['jaspar_position_wd']<r['jaspar_position_wd']) for other in rows))
for name,records in [('legacy_full_checkpoint_quality.csv',rows),('legacy_full_fasta_sources.csv',[{k:i[k] for k in ['source_relative_path','size','sha256']} for i in sources])]:
 with (root/'data/verified'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
print('FULL_SWEEP',len(rows),'80,000 valid 160 bp sequences; selected',json.dumps([r for r in rows if (r['model'],r['epoch']) in [('DDPM',900),('DDPM',1800),('DDPM',2000),('DiT',1050)]]))
print('PARETO',[(r['model'],r['epoch']) for r in rows if r['pareto_nondominated']]);print('BEST_SIXMER',max(rows,key=lambda r:r['sixmer_pcc']))
# The historical screening tables constitute a distinct evaluation batch.
screen=[]
for i in legacy:
 if '/evaluate_effect/' in i['source_relative_path'] and i['source_relative_path'].endswith('.csv'):
  family='TF' if '/TF/' in i['source_relative_path'] else 'JASPAR';model=Path(i['source_relative_path']).stem.replace('res_','').replace('Dit','DiT')
  for row in csv.DictReader(io.StringIO(i['text'])):
   if row['epoch']=='real':continue
   screen.append(dict(model=model,metric_family=family,epoch=int(row['epoch'].replace('.fasta','')),num_hits=int(row['num']),num_categories=int(row['cat']),position_wd=float(row['wd'])))
with (root/'data/verified/legacy_family_screening.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(screen[0]),lineterminator='\n');w.writeheader();w.writerows(screen)
assert len(screen)==320
for family in ['TF','JASPAR']:
 print('MEDIAN_WD',family,{model:float(np.median([r['position_wd'] for r in screen if r['metric_family']==family and r['model']==model])) for model in ['DDPM','DiT','LDM_80','LDM_160']})
