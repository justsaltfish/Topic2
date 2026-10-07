#!/usr/bin/env python3
"""Plot verified archive summaries. No synthetic data or model execution."""
from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/verified"
OUT = ROOT / "figures/results"
COLORS = ["#0077BB", "#EE7733", "#009988", "#CC3311", "#AA4499"]
GROUPS = ["real_9000", "Ara_directory_epoch2000", "Maize_directory_epoch2000"]
LABELS = ["Real reference", "Ara directory, e2000", "Maize directory, e2000"]
GROUP_COLORS = ["#444444", COLORS[0], COLORS[1]]


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def setup():
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":8,
                         "axes.labelsize":8,"axes.titlesize":9,"legend.fontsize":6.5,
                         "axes.spines.top":False,"axes.spines.right":False,
                         "svg.fonttype":"none","savefig.dpi":450})


def title(ax, letter, text):
    ax.set_title(text, loc="left", pad=12)
    ax.text(-.18, 1.08, letter, transform=ax.transAxes, fontsize=12, fontweight="bold")


def save(fig, name):
    OUT.mkdir(parents=True,exist_ok=True)
    for suffix in ("png","svg"):
        path=OUT/f"{name}.{suffix}"
        fig.savefig(path,dpi=450,bbox_inches="tight")
        if suffix=="svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    plt.close(fig)


def fig1():
    fig,axes=plt.subplots(3,2,figsize=(7,8.5),layout="constrained")
    ax=axes[0,0]
    rows=read("gc_histograms.csv")
    for group,label,color in zip(GROUPS,LABELS,GROUP_COLORS):
        r=[x for x in rows if x["group"]==group]
        ax.plot([int(x["gc_bases"])/160 for x in r],[int(x["sequence_count"])/90 for x in r],label=label,color=color,lw=1)
    ax.set(xlabel="GC fraction",ylabel="Sequences (%)",xlim=(0, .8))
    ax.legend();title(ax,"A","GC composition (n = 9,000/group)")

    ax=axes[0,1];rows=read("kmer_correlations.csv")
    for group,label,color in zip(GROUPS[1:],LABELS[1:],GROUP_COLORS[1:]):
        r=[x for x in rows if x["group"]==group]
        ax.plot([int(x["k"]) for x in r],[float(x["pcc"]) for x in r],"o-",color=color,label=label,markersize=4)
    ax.set(xlabel="k",ylabel="Frequency PCC versus real",xticks=[3,4,5,6],ylim=(.8,1))
    ax.legend();title(ax,"B","k-mer composition")

    ax=axes[1,0];rows=read("kmer_frequencies.csv")
    freq={g:{x["kmer"]:float(x["frequency"]) for x in rows if x["group"]==g and x["k"]=="6"} for g in GROUPS}
    keys=sorted(freq[GROUPS[0]])
    maximum=max(max(f.values()) for f in freq.values())
    for group,label,color in zip(GROUPS[1:],LABELS[1:],GROUP_COLORS[1:]):
        ax.scatter([freq[GROUPS[0]][k] for k in keys],[freq[group][k] for k in keys],s=4,alpha=.3,color=color,label=label,rasterized=True)
    ax.plot([0,maximum],[0,maximum],"--",color="#777777",lw=.8)
    ax.set(xlabel="Real 6-mer frequency",ylabel="Generated 6-mer frequency")
    ax.ticklabel_format(axis="both",style="sci",scilimits=(0,0))
    ax.legend(markerscale=2);title(ax,"C","6-mer frequencies (4,096 words)")

    ax=axes[1,1];rows=read("motif_position_weights.csv")
    for group,label,color in zip(["real_9000","Ara_2000","Maize_2000"],LABELS,GROUP_COLORS):
        r=[x for x in rows if x["group"]==group]
        weights=np.array([int(x["weight_including_pseudocount"]) for x in r])
        ax.plot([int(x["legacy_midpoint_index"]) for x in r],weights/weights.sum(),color=color,lw=1,label=label)
    ax.set(xlabel="Motif midpoint index (legacy convention)",ylabel="Normalized position weight")
    ax.legend();title(ax,"D","Motif hit positions")

    ax=axes[2,0];rows=read("internal_diversity.csv")
    for i,(group,color) in enumerate(zip(GROUPS,GROUP_COLORS)):
        r=next(x for x in rows if x["group"]==group)
        mean,lo,hi=map(float,[r["mean"],r["q05"],r["q95"]])
        ax.errorbar(mean,i,xerr=[[mean-lo],[hi-mean]],fmt="o",color=color,capsize=3)
    ax.set(yticks=range(3),yticklabels=["Real","Ara e2000","Maize e2000"],xlabel="Aligned Hamming identity",xlim=(.15,.4))
    title(ax,"E","Within-set diversity (100,000 pairs)")

    ax=axes[2,1];rows=read("sequence_quality_summary.csv")
    x=np.arange(3)
    for shift,key,label,color in [(-.18,"homopolymer_ge10","Run >=10 bp",COLORS[0]),(.18,"homopolymer_ge20","Run >=20 bp",COLORS[1])]:
        values=[100*int(next(r for r in rows if r["group"]==g)[key])/9000 for g in GROUPS]
        ax.bar(x+shift,values,width=.35,label=label,color=color)
    ax.set(xticks=x,xticklabels=["Real","Ara e2000","Maize e2000"],ylabel="Sequences (%)")
    ax.legend();title(ax,"F","Homopolymer profile")
    save(fig,"figure1_sequence_quality")


def fig2():
    fig,axes=plt.subplots(3,2,figsize=(7,8.5),layout="constrained")
    ax=axes[0,0];r=read("ara_guidance_methods_recomputed.csv")
    names=["Maximize","x0","Adam","Sine","Post-step"]
    ax.bar(range(5),[float(x["delta_mean"]) for x in r],color=COLORS)
    ax.axhline(0,color="#777777",lw=.8)
    ax.set(xticks=range(5),xticklabels=names,ylabel="Mean predicted-score change")
    ax.tick_params(axis="x",labelsize=7)
    title(ax,"A","Ara DOWN: method comparison (n = 100)")

    ax=axes[0,1];r=[x for x in read("ara_guidance_paired_scores.csv") if x["method"]=="exp06_poststep"]
    u=np.array([float(x["unguided_score"]) for x in r]);g=np.array([float(x["guided_score"]) for x in r])
    lo,hi=min(u.min(),g.min()),max(u.max(),g.max())
    ax.scatter(u,g,s=10,alpha=.7,color=COLORS[0])
    ax.plot([lo,hi],[lo,hi],"--",color="#777777",lw=.8)
    ax.set(xlabel="Unguided predicted score",ylabel="Post-step predicted score")
    ax.text(.04,.04,"88/100 increased",va="bottom",transform=ax.transAxes)
    title(ax,"B","Ara DOWN: common initial noise")

    ax=axes[1,0];sweep=read("maize_guided_sweep_recomputed.csv")
    r=[x for x in sweep if x["mode"]=="both"]
    for name,label,color in zip(["35S_subset_max","credible_relaxed","credible_strict"],["35S subset","Relaxed (10, 6.5)","Strict (10, 7)"],COLORS[:3]):
        ax.plot([int(x["epoch"]) for x in r],[int(x[name+"_above_both"])/5 for x in r],color=color,label=label,lw=1)
    sens=[x for x in read("homopolymer_sensitivity.csv") if x["mode"]=="both" and x["max_homopolymer_below"]=="20"]
    ax.plot([int(x["epoch"]) for x in sens],[100*float(x["fraction_of_all_generated"]) for x in sens],color="#444444",ls="--",label="Strict + run <20 bp",lw=1)
    ax.set(xlabel="Checkpoint epoch",ylabel="Both-pass fraction of all generated (%)",ylim=(0,100))
    ax.legend(fontsize=6);title(ax,"C","Maize BOTH: threshold sensitivity")

    ax=axes[1,1];obs=read("maize_guided_observations.csv")
    for mode,color in zip(["up","down","both"],COLORS[:3]):
        r=[x for x in obs if x["epoch"]=="1500" and x["mode"]==mode]
        ax.scatter([float(x["up_prediction"]) for x in r],[float(x["down_prediction"]) for x in r],s=3,alpha=.35,color=color,label=mode.upper(),rasterized=True)
    ax.axvline(10,ls="--",color="#777777",lw=.8);ax.axhline(7,ls="--",color="#777777",lw=.8)
    ax.set(xlabel="UP predicted score",ylabel="DOWN predicted score")
    ax.legend(markerscale=3);title(ax,"D","Maize e1500 (n = 500/mode)")

    ax=axes[2,0];modes=["up","down","both"]
    r=[next(x for x in sweep if x["epoch"]=="1500" and x["mode"]==m) for m in modes]
    x=np.arange(3)
    ax.bar(x-.18,[float(v["up_mean"]) for v in r],width=.35,color=COLORS[0],label="UP score")
    ax.bar(x+.18,[float(v["down_mean"]) for v in r],width=.35,color=COLORS[1],label="DOWN score")
    ax.set(xticks=x,xticklabels=[m.upper() for m in modes],ylabel="Mean predicted score")
    ax.legend();title(ax,"E","Maize e1500: directional trade-off")

    ax=axes[2,1]
    ax.bar(x-.18,[int(v["homopolymer_ge10"])/5 for v in r],width=.35,color=COLORS[0],label="Run >=10 bp")
    ax.bar(x+.18,[int(v["homopolymer_ge20"])/5 for v in r],width=.35,color=COLORS[1],label="Run >=20 bp")
    ax.set(xticks=x,xticklabels=[m.upper() for m in modes],ylabel="Sequences (%)",ylim=(0,110))
    ax.legend();title(ax,"F","Maize e1500: homopolymer burden")
    save(fig,"figure2_guided_generation")


if __name__ == "__main__":
    setup();fig1();fig2()
    print("Exported two figures as 450 DPI PNG and SVG")
