"""Exploratory equal-weight scores and transparent normalization sensitivity.

Does not select production checkpoints, change metrics or connect to servers.
Ranks and min-max scores use the same four metrics and fixed seven candidates.
"""
from pathlib import Path
import csv,json,itertools,math
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data/verified/unified_quality_comparison.csv').open()))
assert len(rows)==7
metrics=[('sixmer_pcc','higher'),('gc_wasserstein','lower'),('jaspar2024_position_wd','lower'),('motif_hit_density_abs_deviation','lower')]
def ranks(values):
 order=sorted(range(len(values)),key=lambda i:values[i]);result=[None]*len(values);start=0
 while start<len(order):
  end=start+1
  while end<len(order) and values[order[end]]==values[order[start]]:end+=1
  average=((start+1)+end)/2
  for i in order[start:end]:result[i]=average
  start=end
 return result
oriented=[[-float(r[key]) if direction=='higher' else float(r[key]) for key,direction in metrics] for r in rows]
rankcols=[ranks([v[j] for v in oriented]) for j in range(4)]
rank_scores=[[100*(len(rows)-rankcols[j][i])/(len(rows)-1) for j in range(4)] for i in range(len(rows))]
minmax_scores=[]
for i in range(len(rows)):
 s=[]
 for j in range(4):
  lo=min(v[j] for v in oriented);hi=max(v[j] for v in oriented)
  s.append(100*(hi-oriented[i][j])/(hi-lo) if hi>lo else 50.)
 minmax_scores.append(s)
# Near-tie sensitivity, not a biological threshold: PCC rounded to 3 decimals.
rounded_cols=[ranks([round(v[0],3) for v in oriented])]+rankcols[1:]
rounded_scores=[sum(100*(len(rows)-rounded_cols[j][i])/(len(rows)-1) for j in range(4))/4 for i in range(len(rows))]
metric_rows=[];summary=[]
for i,row in enumerate(rows):
 for j,(key,direction) in enumerate(metrics):metric_rows.append(dict(model=row['model'],epoch=row['epoch'],metric=key,raw_value=float(row[key]),direction=direction,rank=rankcols[j][i],rank_score=rank_scores[i][j],minmax_score=minmax_scores[i][j]))
 summary.append(dict(model=row['model'],epoch=row['epoch'],equal_rank_score=sum(rank_scores[i])/4,equal_minmax_score=sum(minmax_scores[i])/4,pcc_three_decimal_tie_rank_score=rounded_scores[i],sequence_group_rank_score=sum(rank_scores[i][:2])/2,motif_group_rank_score=sum(rank_scores[i][2:])/2))
weight_rows=[];unique=[0]*len(rows);shared=[0]*len(rows);cases=0
for a,b,c in itertools.product(range(1,8),repeat=3):
 d=10-a-b-c
 if not 1<=d<=7:continue
 weights=[a/10,b/10,c/10,d/10];scores=[sum(s*w for s,w in zip(rs,weights)) for rs in rank_scores];maximum=max(scores);winners=[i for i,s in enumerate(scores) if abs(s-maximum)<=1e-9];cases+=1
 for i,row in enumerate(rows):
  is_winner=i in winners
  if is_winner:shared[i]+=1
  if is_winner and len(winners)==1:unique[i]+=1
  weight_rows.append(dict(case_id=cases,weight_sixmer=weights[0],weight_gc=weights[1],weight_position=weights[2],weight_quantity=weights[3],model=row['model'],epoch=row['epoch'],rank_composite_score=scores[i],is_co_winner=int(is_winner),is_unique_winner=int(is_winner and len(winners)==1)))
assert cases==84
for i,row in enumerate(summary):row.update(weight_grid_cases=cases,weight_grid_unique_wins=unique[i],weight_grid_co_wins=shared[i])
def write(name,records):
 with (ROOT/'data/verified'/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');writer.writeheader();writer.writerows(records)
write('composite_score_proposal.csv',summary);write('composite_per_metric_scores.csv',metric_rows);write('composite_weight_sensitivity.csv',weight_rows)
def leaders(key):
 maximum=max(float(r[key]) for r in summary);return [dict(model=r['model'],epoch=r['epoch'],score=r[key]) for r in summary if abs(r[key]-maximum)<1e-9]
protocol=dict(status='exploratory_proposal_not_author_frozen',candidate_n=7,metrics=metrics,default_weights=[.25]*4,group_weights={'sequence_composition':.5,'jaspar_motif':.5},rank_formula='s_j = 100*(N-average_rank_j)/(N-1); S = arithmetic mean of four s_j; ties receive average ranks',quantity='absolute difference from real mean hits per sequence, lower is better; not maximize count',alternative='same four metrics and equal weights with candidate-dependent min-max normalization',weight_grid='all 84 combinations in 0.1 steps, each metric weight at least0.1, weights sum1; exact co-winners retained',weight_grid_not_probability=True,rounded_pcc='round PCC to3 decimals solely for near-tie sensitivity; not an acceptance threshold',equal_rank_leaders=leaders('equal_rank_score'),equal_minmax_leaders=leaders('equal_minmax_score'),rounded_pcc_rank_leaders=leaders('pcc_three_decimal_tie_rank_score'),retrospective=True,production_checkpoint_selected=False,limitations=['candidate-dependent normalization and ranks','seven preselected candidates, not a complete120-checkpoint multi-metric scan','ranks ignore numerical effect magnitude','metrics can be correlated','one generated sample per candidate, no uncertainty or independent validation','raw reference originates from training data'])
(ROOT/'data/verified/composite_score_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
for r in sorted(summary,key=lambda r:-r['equal_rank_score']):print(r)
print('ALTERNATIVE_MINMAX_LEADER',leaders('equal_minmax_score'))
print('Exploratory calculations complete; no final metric or weight selected')
