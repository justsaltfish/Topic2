"""Publication figures from verified historical CSVs; no server calls."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/model_selection';OUT.mkdir(exist_ok=True)
COLORS={'DDPM':'#0077BB','DiT':'#EE7733','LDM_80':'#009988','LDM_160':'#CC3311'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'svg.fonttype':'none','savefig.dpi':450})
def read(name):return list(csv.DictReader((ROOT/'data/verified'/name).open()))
def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=450,bbox_inches='tight',facecolor='white')
 fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',facecolor='white');plt.close(fig)
def screening():
 rows=read('legacy_family_screening.csv');fig,axs=plt.subplots(1,2,figsize=(7.2,3.2),layout='constrained')
 for panel,(ax,family) in enumerate(zip(axs,['TF','JASPAR'])):
  for index,model in enumerate(COLORS):
   y=np.asarray([float(r['position_wd']) for r in rows if r['model']==model and r['metric_family']==family]);assert len(y)==40
   bp=ax.boxplot([y],positions=[index],widths=.48,patch_artist=True,showfliers=False,medianprops={'color':'black','linewidth':1.2})
   bp['boxes'][0].set(facecolor=COLORS[model],alpha=.22,edgecolor=COLORS[model])
   # Deterministic visual spread, not statistical resampling.
   ax.scatter(index+np.linspace(-.13,.13,len(y)),y,s=10,color=COLORS[model],alpha=.65,linewidths=0)
   ax.annotate(f'{np.median(y):.3f}',(index,float(y.max())),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7)
  ax.set_xticks(range(4),['DDPM','DiT','LDM-80','LDM-160']);ax.set_ylabel('Motif-position WD (bp)');ax.set_title(f'{chr(65+panel)}  {family} motif panel',loc='left',fontweight='bold');ax.set_ylim(bottom=0,top=ax.get_ylim()[1]*1.12);ax.grid(axis='y',alpha=.18)
 fig.suptitle('Historical model-family screening',fontsize=11,fontweight='bold')
 save(fig,'figure_model_family_screening')
def checkpoints():
 rows=read('legacy_full_checkpoint_quality.csv');fig,axs=plt.subplots(2,3,figsize=(9.2,5.6),layout='constrained')
 settings=[('sixmer_pcc','6-mer frequency PCC','Higher is better'),('gc_wasserstein','GC-distribution WD','Lower is better'),('jaspar_position_wd','JASPAR motif-position WD (bp)','Lower is better')]
 selected=[('DDPM',900),('DDPM',1800),('DDPM',2000),('DiT',1050)];labels=['DDPM 900','DDPM 1800','DDPM 2000','DiT 1050']
 for col,(key,label,goal) in enumerate(settings):
  ax=axs[0,col]
  for model in ['DDPM','DiT']:
   rr=sorted([r for r in rows if r['model']==model],key=lambda r:int(r['epoch']))
   ax.plot([int(r['epoch']) for r in rr],[float(r[key]) for r in rr],color=COLORS[model],lw=1.2,label=model)
  r=next(r for r in rows if r['model']=='DDPM' and int(r['epoch'])==1800)
  ax.scatter([1800],[float(r[key])],s=65,marker='*',color=COLORS['DDPM'],edgecolor='white',linewidth=.5,zorder=5)
  ax.axvline(1800,color=COLORS['DDPM'],alpha=.3,ls=':',lw=.8)
  ax.set_title(f'{chr(65+col)}  {label}',loc='left',fontweight='bold');ax.set_xlabel('Training epoch');ax.set_ylabel(goal);ax.grid(alpha=.18)
  if key=='sixmer_pcc':ax.set_ylim(0,1.04)
  if col==0:ax.legend(fontsize=7,loc='lower right')
  bottom=axs[1,col];bottom.axhspan(.5,1.5,color='#0077BB',alpha=.08,zorder=0)
  vals=[]
  for index,(model,epoch) in enumerate(selected):
   rr=next(r for r in rows if r['model']==model and int(r['epoch'])==epoch);value=float(rr[key]);vals.append(value)
   bottom.scatter(value,index,s=36,color=COLORS[model],marker='D' if epoch==1800 else 'o',zorder=3)
   bottom.annotate(f'{value:.4f}',(value,index),xytext=(5,0),textcoords='offset points',va='center',fontsize=7)
  bottom.set_yticks(range(4),labels);bottom.invert_yaxis();bottom.set_xlabel(label);bottom.set_title(f'{chr(68+col)}  Candidate checkpoints',loc='left',fontweight='bold');bottom.grid(axis='x',alpha=.18)
  if key=='sixmer_pcc':bottom.set_xlim(.90,1.01)
  else:bottom.set_xlim(0,max(vals)*1.25)
 fig.suptitle('DDPM and DiT checkpoint comparison | 1,000 sequences per checkpoint',fontsize=11,fontweight='bold')
 save(fig,'figure_checkpoint_selection')
if __name__=='__main__':screening();checkpoints();print('Saved two figures, PNG 450 DPI + SVG')
