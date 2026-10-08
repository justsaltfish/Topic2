"""Exploratory rank score and its normalization sensitivity, not a final selection."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures/model_selection'
summary=list(csv.DictReader((ROOT/'data/verified/composite_score_proposal.csv').open()))
summary.sort(key=lambda r:(-round(float(r['equal_rank_score']),10),r['model'],int(r['epoch'])))
per=list(csv.DictReader((ROOT/'data/verified/composite_per_metric_scores.csv').open()))
keys=['sixmer_pcc','gc_wasserstein','jaspar2024_position_wd','motif_hit_density_abs_deviation']
labels=[f"{'UViT-v2 cfg4' if r['model']=='UViT-v2 config4' else r['model']} / {r['epoch']}" for r in summary]
colors={'DDPM':'#0077BB','DiT':'#EE7733','UViT-v2 config4':'#009988'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def save(fig,name):
 for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=450,bbox_inches='tight',facecolor='white')
 plt.close(fig)
fig,(ax,bar)=plt.subplots(1,2,figsize=(10,4.5),layout='constrained',gridspec_kw={'width_ratios':[1.1,1]})
values=np.array([[float(next(p for p in per if p['model']==r['model'] and p['epoch']==r['epoch'] and p['metric']==key)['rank_score']) for key in keys] for r in summary])
im=ax.imshow(values,vmin=0,vmax=100,cmap='viridis',aspect='auto')
ax.set_yticks(range(len(labels)),labels);ax.set_xticks(range(4),['6-mer','GC','Position','Quantity']);ax.set_title('A  Per-metric rank scores',loc='left',fontweight='bold')
for i in range(len(labels)):
 for j in range(4):ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',color='white' if values[i,j]<50 else '#222222',fontsize=8)
fig.colorbar(im,ax=ax,shrink=.6,label='Relative rank score (0–100)')
score=[float(r['equal_rank_score']) for r in summary];bar.barh(range(len(labels)),score,color=[colors[r['model']] for r in summary],height=.65)
bar.set_yticks(range(len(labels)),labels);bar.invert_yaxis();bar.set_xlim(0,100);bar.grid(axis='x',alpha=.18);bar.set_axisbelow(True);bar.set_xlabel('Equal-weight mean of four rank scores');bar.set_title('B  Exploratory composite',loc='left',fontweight='bold')
for i,value in enumerate(score):bar.text(value+1,i,f'{value:.2f}',va='center',fontsize=8)
fig.suptitle('Four-metric equal-rank score | exploratory proposal',fontweight='bold',fontsize=12)
fig.supxlabel('Four equal weights: 6-mer, GC distribution, JASPAR position, and hit-density match.\nRelative to these seven fixed candidates; no independent validation.',fontsize=8)
save(fig,'figure_composite_rank_proposal')
fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained',sharey=True)
for ax,(key,title) in zip(axes,[('equal_rank_score','A  Equal-rank normalization'),('equal_minmax_score','B  Equal min–max normalization')]):
 vals=[float(r[key]) for r in summary]
 ax.barh(range(len(labels)),vals,color=[colors[r['model']] for r in summary],height=.65);ax.set_yticks(range(len(labels)),labels);ax.set_xlim(0,100);ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True);ax.set_title(title,loc='left',fontweight='bold');ax.set_xlabel('Composite score (same four equal weights)')
 for i,v in enumerate(vals):ax.text(v+1,i,f'{v:.2f}',va='center',fontsize=8)
axes[0].invert_yaxis();fig.suptitle('Normalization changes the leading candidate',fontweight='bold',fontsize=12)
fig.supxlabel('Same metrics, directions, candidate set and weights. Only normalization changes.\nThis sensitivity must accompany any retrospective composite claim.',fontsize=8)
save(fig,'figure_composite_normalization_sensitivity')
print('Saved composite proposal and normalization sensitivity, PNG + SVG')
