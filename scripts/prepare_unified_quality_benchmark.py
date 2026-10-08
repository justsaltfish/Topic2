"""Prepare common sequence-quality evaluation from private read-only JSON exports."""
from pathlib import Path
import json,csv,io,itertools,random,hashlib
from collections import Counter
import numpy as np
from scipy.stats import wasserstein_distance
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',required=True)
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1];private=Path(args.source_dir)
ng=next(i for i in json.loads((private/'sources_03.json').read_text()) if i['source_relative_path'].endswith('/data/NG_enhancer_data.csv'))
real=list(dict.fromkeys(r['Sequence'].upper() for r in csv.DictReader(io.StringIO(ng['text'])) if all(c in 'ACGTacgt' for c in r['Sequence'])));assert len(real)==11984
words=[''.join(w) for w in itertools.product('ACGT',repeat=6)]
def count(seq):return Counter(s[j:j+6] for s in seq for j in range(len(s)-5))
def freq(seq):
 c=count(seq);return np.array([c[w] for w in words],float)/sum(c.values())
def records(text):
 out=[];name=None;seq=[]
 for l in text.splitlines():
  if l.startswith('>'):
   if name is not None:out.append((name,''.join(seq).upper()))
   name=l[1:].split()[0];seq=[]
  elif l.strip():seq.append(l.strip())
 if name is not None:out.append((name,''.join(seq).upper()))
 return out
ref=freq(real);gcref=np.array([(s.count('G')+s.count('C'))/160 for s in real]);uvit=json.loads((private/'sources_uvit4_sweep_fasta.json').read_text());uvrows=[];selected_cache={}
for item in uvit:
 rec=records(item['text']);assert len(rec)==9000 and len({r[0] for r in rec})==9000 and all(len(s)==160 and set(s)<=set('ACGT') for _,s in rec)
 indices=sorted(random.Random(42).sample(range(len(rec)),1000));selected=[rec[i] for i in indices];sequences=[s for _,s in selected];v=freq(sequences);epoch=int(Path(item['source_relative_path']).stem.split('_')[-1]);gc=np.array([(s.count('G')+s.count('C'))/160 for s in sequences]);row=dict(model='UViT-v2 config4',epoch=epoch,n_source=9000,n_selected=1000,sixmer_pcc=float(np.corrcoef(v,ref)[0,1]),gc_mean=float(gc.mean()),gc_wasserstein=float(wasserstein_distance(gc,gcref)),source_sha256=item['sha256']);uvrows.append(row);selected_cache[epoch]=(item,selected,indices)
best=max(uvrows,key=lambda r:r['sixmer_pcc']);print('UVIT_BEST_6MER',best)
legacy=json.loads((private/'sources_legacy_all_fasta.json').read_text());candidates=[]
for model,epoch,reason in [('DDPM',1800,'best_6mer_in_40_saved_DDPM_batches'),('DiT',1200,'best_6mer_in_40_saved_DiT_batches'),('DiT',1050,'historical_author_candidate'),('DDPM',900,'historical_DDPM_2022_WD_minimum'),('DDPM',2000,'existing_2026_10_01_guidance_checkpoint')]:
 item=next(i for i in legacy if f'/{"DDPM" if model=="DDPM" else "Dit"}/final/' in i['source_relative_path'] and i['source_relative_path'].endswith(f'/{epoch}.fasta'));rec=records(item['text']);assert len(rec)==1000
 candidates.append(dict(model=model,epoch=epoch,reason=reason,source_relative_path=item['source_relative_path'],source_sha256=item['sha256'],source_n=1000,selected_indices=list(range(1000)),records=rec))
for epoch,reason in [(best['epoch'],'best_6mer_in_40_saved_config4_batches'),(1800,'historical_UViT_v2_config4_2024_WD_minimum')]:
 if any(c['model']=='UViT-v2 config4' and c['epoch']==epoch for c in candidates):continue
 item,rec,indices=selected_cache[epoch];candidates.append(dict(model='UViT-v2 config4',epoch=epoch,reason=reason,source_relative_path=item['source_relative_path'],source_sha256=item['sha256'],source_n=9000,selected_indices=indices,records=rec))
public=[];members=[];obs=[]
for candidate in candidates:
 seqs=[s for _,s in candidate['records']];vec=freq(seqs);gc=np.array([(s.count('G')+s.count('C'))/160 for s in seqs]);candidate['selected_ids']=[name for name,_ in candidate['records']]
 member=[dict(record_index=i,record_id=name,sequence_sha256=hashlib.sha256(seq.encode()).hexdigest()) for i,(name,seq) in zip(candidate['selected_indices'],candidate['records'])]
 h=hashlib.sha256(json.dumps(member,sort_keys=True,separators=(',',':')).encode()).hexdigest();candidate['membership_sha256']=h
 public.append({k:candidate[k] for k in ['model','epoch','reason','source_relative_path','source_sha256','source_n','membership_sha256']}|dict(n=1000,sixmer_pcc=float(np.corrcoef(vec,ref)[0,1]),gc_mean=float(gc.mean()),gc_wasserstein=float(wasserstein_distance(gc,gcref)),unique_fraction=len(set(seqs))/1000,exact_real_matches=sum(s in set(real) for s in seqs)))
 members.extend(dict(model=candidate['model'],epoch=candidate['epoch'],**m) for m in member)
 obs.extend(dict(model=candidate['model'],epoch=candidate['epoch'],record_id=name,gc=float(g)) for (name,_),g in zip(candidate['records'],gc))
print('CANDIDATES',[(r['model'],r['epoch'],r['sixmer_pcc'],r['gc_wasserstein']) for r in public])
for name,rows in [('unified_quality_candidates_pre_fimo.csv',public),('unified_quality_membership.csv',members),('unified_quality_gc_observations.csv',obs),('unified_uvit4_sixmer_sweep.csv',uvrows)]:
 with (repo/'data/verified'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
# Private source records remain outside the public repository.
for c in candidates:c.pop('records')
(private/'unified_candidates.json').write_text(json.dumps(candidates))
protocol=dict(reference_source=ng['source_relative_path'],reference_sha256=ng['sha256'],reference_n=11984,reference_normalized_sequence_set_sha256=hashlib.sha256('\n'.join(sorted(real)).encode()).hexdigest(),sampling='all 1000 legacy records; UViT 1000/9000 uniformly without replacement using Python Random(42); same fixed sample used for every metric',sixmer='forward overlapping 6-mers, complete 4096 vector, aggregate frequencies',gc='empirical per-sequence fraction, 1D WD, fixed full reference',candidate_selection='historical candidates and 6-mer optima of each existing 40-checkpoint sweep; retrospective, not production model selection',reference_is_independent_test=False)
(repo/'data/verified/unified_quality_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
