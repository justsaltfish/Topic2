"""Reanalyse private read-only JSON exports; no server connections.
Input files are described in results/00_model_selection/README.md.
"""
import json,csv,io,hashlib,itertools
from pathlib import Path
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
assert len(real)==11984
sources=json.loads((private/'sources_selection_sequences.json').read_text());groups=[('Real reference',None,real)]
for item in sources:
 seqs=[l.strip().upper() for l in item['text'].splitlines() if l and not l.startswith('>')];assert len(seqs)==1000 and all(len(s)==160 and set(s)<=set('ACGT') for s in seqs)
 model='DDPM' if '/DDPM/' in item['source_relative_path'] else 'DiT';epoch=int(Path(item['source_relative_path']).stem);groups.append((model,epoch,seqs))
def gc(s):return (s.count('G')+s.count('C'))/len(s)
def runs(s,period):
 longest=current=period
 for j in range(period,len(s)):
  current=current+1 if s[j]==s[j-period] else period
  longest=max(longest,current)
 return longest
words=[''.join(x) for x in itertools.product('ACGT',repeat=6)]
def kmers(seqs):
 count=Counter(s[j:j+6] for s in seqs for j in range(len(s)-5));return np.asarray([count[w] for w in words],dtype=np.float64)/sum(count.values())
realvec=kmers(real);realgc=np.array([gc(s) for s in real]);realset=set(real)
summary=[];observations=[];vectors=[]
for model,epoch,seqs in groups:
 v=kmers(seqs);g=np.asarray([gc(s) for s in seqs]);pcc=float(np.corrcoef(v,realvec)[0,1]);hom=np.array([runs(s,1) for s in seqs]);repeat=np.array([runs(s,2) for s in seqs]);unique=len(set(seqs))
 arr=np.asarray([[ord(c) for c in s] for s in seqs],dtype=np.uint8);realarr=np.asarray([[ord(c) for c in s] for s in real],dtype=np.uint8)
 rng=np.random.RandomState(42);a=rng.randint(len(seqs),size=10000);b=rng.randint(len(seqs)-1,size=10000);b+=b>=a
 within=np.mean(arr[a]!=arr[b],axis=1);a2=rng.randint(len(seqs),size=10000);b2=rng.randint(len(real),size=10000);outer=np.mean(arr[a2]!=realarr[b2],axis=1)
 row=dict(model=model,epoch='' if epoch is None else epoch,n=len(seqs),sixmer_pcc=pcc,gc_mean=float(g.mean()),gc_wasserstein=float(wasserstein_distance(g,realgc)),unique_fraction=unique/len(seqs),exact_real_matches=sum(s in realset for s in seqs),homopolymer_ge20_fraction=float(np.mean(hom>=20)),period2_repeat_ge20_fraction=float(np.mean(repeat>=20)),within_hamming_mean=float(within.mean()),to_real_hamming_mean=float(outer.mean()));summary.append(row)
 for i,(gg,h,r) in enumerate(zip(g,hom,repeat)):observations.append(dict(model=model,epoch=row['epoch'],record_index=i,gc=float(gg),max_homopolymer=int(h),max_period2_repeat=int(r)))
 for w,f in zip(words,v):vectors.append(dict(model=model,epoch=row['epoch'],kmer=w,frequency=float(f)))
for name,rows in [('legacy_selection_quality.csv',summary),('legacy_selection_observations.csv',observations),('legacy_selection_sixmer.csv',vectors)]:
 with (root/'data/verified'/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
(root/'data/verified/legacy_selection_quality_protocol.json').write_text(json.dumps(dict(reference_source_relative_path=ng['source_relative_path'],reference_sha256=ng['sha256'],n_real=len(real),sources=[{k:i[k] for k in ['source_relative_path','size','sha256']} for i in sources],sixmer='forward strand, overlapping windows, complete 4096-word vector',gc_wd='empirical per-sequence GC-fraction Wasserstein distance',hamming='positionwise mismatches/160; 10000 sampled pairs, RandomState42; interval not biological replicates',repeat20='retrospective descriptive threshold, no declared acceptance rule',reference_status='full current valid NG source, not independent held-out test set'),indent=2)+'\n')
print(json.dumps(summary,indent=2))
