"""One four-panel figure from a common reference, sample size and FIMO protocol."""
from pathlib import Path
import csv,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'data/verified/unified_quality_comparison.csv').open()))
primary={'DDPM':1800,'DiT':1200,'UViT-v2 config4':1900}
ordered=[next(r for r in rows if r['model']==m and int(r['epoch'])==e) for m,e in primary.items()]
full = '--all-candidates' in sys.argv
if full:
 ordered += [r for r in rows if r not in ordered]
else:
 ordered += [r for r in rows if ((r['model']=='DiT' and int(r['epoch'])==1050) or (r['model']=='UViT-v2 config4' and int(r['epoch'])==1800)) and r not in ordered]
colors={'DDPM':'#0077BB','DiT':'#EE7733','UViT-v2 config4':'#009988'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','savefig.dpi':450})
fig,grid=plt.subplots(2,2,figsize=(9.2,7.3 if full else 6.4),sharey=True,layout='constrained')
axes=grid.ravel()
settings=[('sixmer_pcc','A  6-mer frequency PCC','Higher is better'),('gc_wasserstein','B  GC-distribution WD','Lower is better'),('jaspar2024_position_wd','C  Motif-position WD (bp)','Lower is better'),('jaspar2024_hits_per_sequence','D  Motif hits per sequence','Closer to real is better')]
labels=[f"{'UViT-v2 cfg4' if r['model']=='UViT-v2 config4' else r['model']} / {r['epoch']}" for r in ordered]
for ax,(key,title,goal) in zip(axes,settings):
 values=[float(r[key]) for r in ordered]
 for i,(row,value) in enumerate(zip(ordered,values)):
  ax.scatter(value,i,s=48,color=colors[row['model']],alpha=1,zorder=3)
  ax.annotate((f'{value:.3f}' if key=='jaspar2024_hits_per_sequence' else f'{value:.5f}'),(value,i),xytext=(6,0),textcoords='offset points',va='center',fontsize=8,zorder=4,bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':.3})
 ax.set_title(title,loc='left',fontweight='bold',fontsize=10)
 ax.set_xlabel(goal);ax.set_yticks(range(len(ordered)),labels);ax.grid(axis='x',alpha=.18)
 ax.axhline(2.5,color='#888888',ls=':',lw=.8)
 if key=='sixmer_pcc':ax.set_xlim(0,1.13)
 elif key=='jaspar2024_hits_per_sequence':
  reference=float(rows[0]['real_jaspar2024_hits_per_sequence'])
  ax.axvline(reference,color='#666666',ls='--',lw=1,label=f'Real: {reference:.3f}')
  ax.set_xlim(0,max(reference,max(values))*1.25);ax.legend(loc='lower left',fontsize=8)
 else:ax.set_xlim(0,max(values)*1.28)
axes[0].invert_yaxis();axes[0].set_ylabel('Model / training epoch')
fig.suptitle('Sequence quality of existing generator checkpoints',fontweight='bold',fontsize=12)
fig.supxlabel(('Top three: best 6-mer batches in each saved sweep. Lower rows: historical and metric-specific candidates.' if full else 'First three: best 6-mer batches in each saved sweep. Extra rows: historical DiT and UViT motif-WD candidates.')+'\n1,000 fixed sequences per candidate; common real reference and JASPAR2024 scan; point estimates.',fontsize=8)
out=ROOT/'figures/model_selection'
for suffix in ['png','svg']:
 name='figure_unified_quality_all_candidates' if full else 'figure_unified_quality_comparison'
 fig.savefig(out/f'{name}.{suffix}',dpi=450,bbox_inches='tight',facecolor='white')
plt.close(fig)
print('Saved unified four-panel PNG + SVG')
