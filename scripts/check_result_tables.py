#!/usr/bin/env python3
"""Recompute numeric summaries from public observation tables, without SSH."""
from collections import defaultdict
import csv
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/verified"
THRESHOLDS={"35S_subset_max":(11.161853790283203,6.437514305114746),
            "credible_relaxed":(10,6.5),"credible_strict":(10,7),
            "original_61_reference":(12.479280471801758,9.175949096679688)}


def read(name):
    with (DATA/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def close(a,b):
    assert math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10),(a,b)


def pcc(a,b):
    ma,mb=statistics.mean(a),statistics.mean(b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))


def check():
    quality=defaultdict(list)
    for r in read("sequence_quality_observations.csv"):
        quality[r["group"]].append(r)
    assert sum(map(len,quality.values()))==27000
    for row in read("sequence_quality_summary.csv"):
        records=quality[row["group"]]
        close(row["n"],len(records))
        g=[float(x["gc_fraction"]) for x in records]
        close(row["gc_mean"],statistics.mean(g))
        close(row["gc_sd_sequences"],statistics.stdev(g))
        for length in (10,20):
            close(row[f"homopolymer_ge{length}"],sum(int(x["max_homopolymer"])>=length for x in records))
        close(row["exact_matches_full_dataset"],sum(int(x["exact_match_full_dataset"]) for x in records))
    frequencies=defaultdict(dict)
    for r in read("kmer_frequencies.csv"):
        frequencies[(r["group"],r["k"])][r["kmer"]]=float(r["frequency"])
    for row in read("kmer_correlations.csv"):
        a=frequencies[(row["reference"],row["k"])];b=frequencies[(row["group"],row["k"])]
        keys=sorted(a);assert keys==sorted(b) and len(keys)==4**int(row["k"])
        close(row["pcc"],pcc([a[k] for k in keys],[b[k] for k in keys]))
        close(sum(a.values()),1);close(sum(b.values()),1)
    weights=defaultdict(list)
    for r in read("motif_position_weights.csv"):
        weights[r["group"]].append(int(r["weight_including_pseudocount"]))
    reference=weights["real_9000"]
    for row in read("motif_position_wd.csv"):
        current=weights[row["group"]]
        difference=0;distance=0
        for a,b in zip(reference[:-1],current[:-1]):
            difference+=a/sum(reference)-b/sum(current)
            distance+=abs(difference)
        close(row["motif_position_wasserstein"],distance)
    groups=defaultdict(list)
    for row in read("maize_guided_observations.csv"):
        assert all(math.isfinite(float(row[k])) for k in ("up_prediction","down_prediction","gc_fraction"))
        groups[(row["epoch"],row["mode"])].append(row)
    assert len(groups)==120 and sum(map(len,groups.values()))==60000
    for row in read("maize_guided_sweep_recomputed.csv"):
        records=groups[(row["epoch"],row["mode"])]
        assert len(records)==500 and len({r["sequence_id"] for r in records})==500
        up=[float(r["up_prediction"]) for r in records];down=[float(r["down_prediction"]) for r in records]
        close(row["up_mean"],statistics.mean(up));close(row["down_mean"],statistics.mean(down))
        close(row["up_max"],max(up));close(row["down_max"],max(down))
        for label,(tu,td) in THRESHOLDS.items():
            close(row[label+"_above_up"],sum(u>tu for u in up))
            close(row[label+"_above_down"],sum(d>td for d in down))
            close(row[label+"_above_both"],sum(u>tu and d>td for u,d in zip(up,down)))
    for row in read("homopolymer_sensitivity.csv"):
        all_records=groups[(row["epoch"],row["mode"])]
        records=[r for r in all_records if int(r["max_homopolymer"])<int(row["max_homopolymer_below"])]
        passed=sum(float(r["up_prediction"])>10 and float(r["down_prediction"])>7 for r in records)
        close(row["retained_n"],len(records));close(row["strict_both_retained"],passed)
        close(row["fraction_of_all_generated"],passed/500)
        if records:close(row["fraction_of_retained"],passed/len(records))
    methods=defaultdict(list)
    for row in read("ara_guidance_paired_scores.csv"):
        close(row["delta"],float(row["guided_score"])-float(row["unguided_score"]))
        methods[row["method"]].append(row)
    assert len(methods)==5
    for row in read("ara_guidance_methods_recomputed.csv"):
        records=methods[row["method"]];assert len(records)==100
        close(row["unguided_mean"],statistics.mean(float(r["unguided_score"]) for r in records))
        close(row["guided_mean"],statistics.mean(float(r["guided_score"]) for r in records))
        close(row["delta_mean"],statistics.mean(float(r["delta"]) for r in records))
        close(row["improved_count"],sum(float(r["delta"])>0 for r in records))
    print("PASS: public quality, k-mer, position-WD, 60,000 sweep observations and 500 method pairs")


if __name__=="__main__":
    check()
