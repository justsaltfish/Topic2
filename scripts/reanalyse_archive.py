#!/usr/bin/env python3
"""Reanalyse read-only archive exports; no SSH, model loading or sampling.

Input: sources_*.json with source_relative_path/text/sha256/size, plus
file_inventory_and_fimo.json containing read-only FASTA and FIMO checks.
Raw inputs remain outside the public repository; exported tables omit DNA.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
from itertools import product, groupby
import json
import math
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET

import numpy as np
from scipy.stats import wasserstein_distance

ROOT = Path(__file__).resolve().parents[1]
ARA = "topic_new26/topic_enhancer/every_species/Ara/35s/down/"
MAIZE = "topic_new26/topic_enhancer/every_species/Maize/35s/down/"
SWEEP = "topic_new26_aiCode/2026/08/04/maize_guided_epoch_sweep/"
V3 = "topic_new26/topic_enhancer/guide_generation/v3/DDPM/"
THRESHOLDS = {
    "35S_subset_max": (11.161853790283203, 6.437514305114746),
    "credible_relaxed": (10.0, 6.5),
    "credible_strict": (10.0, 7.0),
    "original_61_reference": (12.479280471801758, 9.175949096679688),
}


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def fasta(text):
    result, name, sequence = [], None, ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(">"):
            if name is not None:
                result.append((name, sequence))
            name, sequence = line[1:].split()[0], ""
        else:
            sequence += line.upper()
    if name is not None:
        result.append((name, sequence))
    return result


def quality(sequence):
    assert len(sequence) == 160 and set(sequence) <= set("ACGT")
    counts = Counter(sequence)
    gc = (counts["G"] + counts["C"]) / 160
    longest = max(sum(1 for _ in run) for _, run in groupby(sequence))
    entropy = -sum((n / 160) * math.log2(n / 160) for n in counts.values()) / 2
    return gc, longest, entropy


def write_csv(path, data):
    assert data, path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def analyse(source_dir):
    sources = {}
    for path in sorted(source_dir.glob("sources_*.json")):
        for source in json.loads(path.read_text(encoding="utf-8")):
            if "text" in source:
                assert hashlib.sha256(source["text"].encode("utf-8")).hexdigest() == source["sha256"]
                sources[source["source_relative_path"]] = source
    inventory = json.loads((source_dir / "file_inventory_and_fimo.json").read_text())
    out = ROOT / "data/verified"
    out.mkdir(parents=True, exist_ok=True)
    raw = rows(sources["topic_all/topic2_Diffusion/data/NG_enhancer_data.csv"]["text"])
    valid = {r["Sequence"].upper() for r in raw if set(r["Sequence"].upper()) <= set("ACGT")}
    assert len(raw) == 11985 and len(valid) == 11984
    registry = []
    for rel, source in sorted(sources.items()):
        registry.append({"source_relative_path": rel, "size": source["size"],
                         "sha256": source["sha256"], "status": "source_bytes_read"})
    for source in inventory["generated_files"] + inventory["checkpoint_files"]:
        rel = source["source_relative_path"]
        if rel not in sources:
            registry.append({"source_relative_path": rel, "size": source.get("size", ""),
                             "sha256": source["sha256"], "status": "file_hash_checked"})
    for source in inventory["fimo_stats"] + [inventory["motif_database"]]:
        registry.append({"source_relative_path": source["source_relative_path"],
                         "size": source["size"], "sha256": source["sha256"],
                         "status": "fimo_raw_recounted" if "hit_count" in source else "file_hash_checked"})
    registry = list({x["source_relative_path"]: x for x in registry}.values())
    write_csv(out / "source_manifest.csv", registry)
    write_csv(out / "generated_file_inventory.csv", inventory["generated_files"])
    write_csv(out / "checkpoint_inventory.csv", inventory["checkpoint_files"])

    groups = {
        "real_9000": fasta(sources[ARA + "wd_equal_real_work/real_9000.fasta"]["text"]),
        "Ara_directory_epoch2000": fasta(sources[ARA + "DDPM/v1/gen_file/2000.fasta"]["text"]),
        "Maize_directory_epoch2000": fasta(sources[MAIZE + "DDPM/v1/gen_file/2000.fasta"]["text"]),
    }
    observations, summaries, histograms, diversity = [], [], [], []
    for group, records in groups.items():
        assert len(records) == 9000 and len({i for i, _ in records}) == 9000
        metrics = [quality(s) for _, s in records]
        gc, poly, ent = map(list, zip(*metrics))
        for (ident, sequence), (g, p, h) in zip(records, metrics):
            observations.append({"group": group, "sequence_id": ident, "gc_fraction": g,
                                 "max_homopolymer": p, "normalized_base_entropy": h,
                                 "exact_match_full_dataset": int(sequence in valid)})
        summaries.append({"group": group, "n": len(records), "unique_sequences": len({s for _, s in records}),
                          "gc_mean": statistics.mean(gc), "gc_sd_sequences": statistics.stdev(gc),
                          "gc_median": statistics.median(gc), "homopolymer_ge10": sum(p >= 10 for p in poly),
                          "homopolymer_ge20": sum(p >= 20 for p in poly), "max_homopolymer": max(poly),
                          "base_entropy_mean": statistics.mean(ent),
                          "exact_matches_full_dataset": sum(s in valid for _, s in records)})
        counts = Counter(round(g * 160) for g in gc)
        histograms.extend({"group": group, "gc_bases": i, "sequence_count": counts[i]} for i in range(161))
        # Descriptive within-population diversity, not independent biological replicates.
        array = np.array([list(s.encode("ascii")) for _, s in records], dtype=np.uint8)
        rng = np.random.default_rng(42)
        i = rng.integers(0, len(records), 100000)
        j = rng.integers(0, len(records) - 1, 100000)
        j += j >= i
        identity = np.mean(array[i] == array[j], axis=1)
        diversity.append({"group": group, "metric": "aligned_Hamming_identity", "sampled_pairs": len(i),
                          "pair_sampling_seed": 42, "mean": float(np.mean(identity)),
                          "median": float(np.median(identity)), "q05": float(np.quantile(identity, .05)),
                          "q95": float(np.quantile(identity, .95)), "independent_runs": 1})
    write_csv(out / "sequence_quality_observations.csv", observations)
    write_csv(out / "sequence_quality_summary.csv", summaries)
    write_csv(out / "gc_histograms.csv", histograms)
    write_csv(out / "internal_diversity.csv", diversity)

    kmer_rows, correlations = [], []
    for k in (3, 4, 5, 6):
        vocabulary = ["".join(x) for x in product("ACGT", repeat=k)]
        frequencies = {}
        for group, records in groups.items():
            counts = Counter(s[i:i+k] for _, s in records for i in range(161-k))
            denominator = len(records) * (161-k)
            f = np.array([counts[m] / denominator for m in vocabulary])
            frequencies[group] = f
            kmer_rows.extend({"group": group, "k": k, "kmer": m, "count": counts[m],
                              "frequency": counts[m] / denominator} for m in vocabulary)
        for group in groups:
            if group == "real_9000":
                continue
            correlations.append({"group": group, "reference": "real_9000", "k": k,
                                 "pcc": float(np.corrcoef(frequencies[group], frequencies["real_9000"])[0,1]),
                                 "vocabulary_size": 4**k, "strand_rule": "forward_only", "n_per_group": 9000})
    write_csv(out / "kmer_frequencies.csv", kmer_rows)
    write_csv(out / "kmer_correlations.csv", correlations)

    fimo = {x["name"]: x for x in inventory["fimo_stats"]}
    motif_rows, position_rows, wd_rows = [], [], []
    for name, source in fimo.items():
        motif_rows.extend({"group": name, "motif_id": motif, "hit_count": count}
                          for motif, count in sorted(source["motif_id_counts"].items()))
        position_rows.extend({"group": name, "legacy_midpoint_index": i, "weight_including_pseudocount": n}
                             for i, n in enumerate(source["position_weights"]))
        distance = wasserstein_distance(range(160), range(160), fimo["real_9000"]["position_weights"], source["position_weights"])
        wd_rows.append({"group": name, "reference": "real_9000", "n_sequences": 9000,
                        "motif_hits": source["hit_count"], "alt_id_categories": source["category_count"],
                        "motif_position_wasserstein": distance, "unit": "bp", "pseudocount_per_position": 1})
    write_csv(out / "motif_counts.csv", motif_rows)
    write_csv(out / "motif_position_weights.csv", position_rows)
    write_csv(out / "motif_position_wd.csv", wd_rows)
    motif_keys = sorted(set().union(*(set(fimo[g]["motif_id_counts"])
                                    for g in ("real_9000", "Ara_2000", "Maize_2000"))))
    motif_reference = [fimo["real_9000"]["motif_id_counts"].get(k,0) for k in motif_keys]
    profiles=[]
    for group in ("Ara_2000", "Maize_2000"):
        profile=[fimo[group]["motif_id_counts"].get(k,0) for k in motif_keys]
        profiles.append({"group":group,"reference":"real_9000","motif_id_union_n":len(motif_keys),
                         "hit_count_profile_pcc":float(np.corrcoef(motif_reference,profile)[0,1]),
                         "basis":"union_of_hit_motif_IDs_zero_filled"})
    write_csv(out / "motif_profile_correlations.csv",profiles)
    scans=[]
    for rel, source in sources.items():
        if not rel.endswith("/fimo.xml"):
            continue
        xml=ET.fromstring(source["text"])
        settings={x.get("name"):x.text for x in xml.findall("./settings/setting")}
        scans.append({"source_relative_path":rel,"fimo_version":xml.get("version"),
                      "p_value_threshold":settings["output threshold"],
                      "scan_both_strands":settings["scan both strands"],
                      "matrix_pseudocount":settings["pseudocount"],
                      "background_source":settings["background file name"],
                      "motif_database_file":Path(settings["MEME file name"]).name})
    assert len(scans)==4 and len({tuple(row[k] for k in row if k!='source_relative_path') for row in scans})==1
    write_csv(out/"fimo_scan_metadata.csv",scans)
    original_wd = rows(sources[ARA + "wd_equal_real_results.csv"]["text"])
    for group, epoch in (("Ara_500", "500"), ("Ara_2000", "2000")):
        expected = next(float(r["wd"]) for r in original_wd if r["model"] == "DDPM" and r["file_id"] == epoch)
        observed = next(r["motif_position_wasserstein"] for r in wd_rows if r["group"] == group)
        assert abs(expected - observed) < 1e-10
    archive_wd = [{k: row[k] for k in ("model", "file_id", "n_sequences", "num_motifs", "num_categories", "wd")}
                  for row in original_wd if row["model"] == "DDPM"]
    write_csv(out / "ara_ddpm_wd_archive.csv", archive_wd)

    observation_rows, sweep_rows, sensitivity_rows = [], [], []
    aggregation = {(int(r["epoch"]), r["mode"]): r for r in rows(sources[SWEEP + "guided_epoch_scores.csv"]["text"])}
    credible = {(int(r["epoch"]), r["mode"]): r for r in rows(sources["topic_new26_aiCode/2026/08/04/credible_threshold/credible_threshold_comparison.csv"]["text"])}
    for epoch in range(50, 2001, 50):
        for mode in ("up", "down", "both"):
            data = rows(sources[SWEEP + f"e{epoch}/{mode}/classifier_guidance_{mode}/predictions.csv"]["text"])
            assert len(data) == 500 and len({r["seq_id"] for r in data}) == 500
            up, down, polies = [], [], []
            for row in data:
                u, d = float(row["maize_35s_up_pred"]), float(row["maize_35s_down_pred"])
                assert math.isfinite(u) and math.isfinite(d)
                gc, poly, entropy = quality(row["sequence"])
                up.append(u); down.append(d); polies.append(poly)
                observation_rows.append({"epoch": epoch, "mode": mode, "sequence_id": row["seq_id"],
                                         "up_prediction": u, "down_prediction": d, "gc_fraction": gc,
                                         "max_homopolymer": poly, "normalized_base_entropy": entropy})
            result = {"epoch": epoch, "mode": mode, "n": 500,
                      "up_mean": statistics.mean(up), "down_mean": statistics.mean(down),
                      "up_max": max(up), "down_max": max(down),
                      "homopolymer_ge10": sum(p>=10 for p in polies), "homopolymer_ge20": sum(p>=20 for p in polies)}
            for label, (tu, td) in THRESHOLDS.items():
                result[label + "_above_up"] = sum(x>tu for x in up)
                result[label + "_above_down"] = sum(x>td for x in down)
                result[label + "_above_both"] = sum(u>tu and d>td for u,d in zip(up,down))
                if label != "original_61_reference":
                    for suffix in ("_above_up", "_above_down", "_above_both"):
                        assert result[label+suffix] == int(credible[(epoch,mode)][label+suffix])
            for key in ("up_mean", "down_mean", "up_max", "down_max"):
                assert abs(result[key] - float(aggregation[(epoch, mode)][key])) < 1e-6
            sweep_rows.append(result)
            for cutoff in (10, 20):
                indices = [i for i,p in enumerate(polies) if p < cutoff]
                strict = sum(up[i] > 10 and down[i] > 7 for i in indices)
                sensitivity_rows.append({"epoch":epoch,"mode":mode,"max_homopolymer_below":cutoff,
                                         "total_n":500,"retained_n":len(indices),"strict_both_retained":strict,
                                         "fraction_of_all_generated":strict/500,
                                         "fraction_of_retained":strict/len(indices) if indices else "",
                                         "scope":"descriptive_sensitivity_not_final_quality_gate"})
    write_csv(out / "maize_guided_observations.csv", observation_rows)
    write_csv(out / "maize_guided_sweep_recomputed.csv", sweep_rows)
    write_csv(out / "homopolymer_sensitivity.csv", sensitivity_rows)

    paired, method_summary = [], []
    methods = ("exp02_maximize", "exp03_x0pred", "exp04_adam", "exp05_sine", "exp06_poststep")
    for method in methods:
        prefix = V3 + method + "/outputs/"
        u = rows(sources[prefix + "unguided_scores.csv"]["text"])
        g = rows(sources[prefix + "guided_scores.csv"]["text"])
        us, gs = fasta(sources[prefix + "unguided.fasta"]["text"]), fasta(sources[prefix + "guided.fasta"]["text"])
        assert len(u) == len(g) == len(us) == len(gs) == 100
        diffs, up, gp, uscores, gscores = [], [], [], [], []
        for a,b,asequence,bsequence in zip(u,g,us,gs):
            assert a["name"] == b["name"] == asequence[0] == bsequence[0]
            av,bv = float(a["pred_score"]),float(b["pred_score"])
            aq,bq = quality(asequence[1]),quality(bsequence[1])
            diffs.append(bv-av); up.append(aq[1]); gp.append(bq[1]); uscores.append(av); gscores.append(bv)
            paired.append({"method":method,"sequence_id":a["name"],"unguided_score":av,"guided_score":bv,
                           "delta":bv-av,"unguided_gc":aq[0],"guided_gc":bq[0],
                           "unguided_max_homopolymer":aq[1],"guided_max_homopolymer":bq[1]})
        method_summary.append({"method":method,"n":100,"unguided_mean":statistics.mean(uscores),
                               "guided_mean":statistics.mean(gscores),"delta_mean":statistics.mean(diffs),
                               "improved_count":sum(d>0 for d in diffs),"improved_fraction":sum(d>0 for d in diffs)/100,
                               "unguided_poly_ge10":sum(p>=10 for p in up),"guided_poly_ge10":sum(p>=10 for p in gp),
                               "unguided_poly_ge20":sum(p>=20 for p in up),"guided_poly_ge20":sum(p>=20 for p in gp)})
    write_csv(out / "ara_guidance_paired_scores.csv", paired)
    write_csv(out / "ara_guidance_methods_recomputed.csv", method_summary)

    conflict = []
    july = "topic_new26_aiCode/2026/07/08/guided_generation_maize_35s_three_directions/"
    tu, td = THRESHOLDS["35S_subset_max"]
    for mode in ("up", "down", "both"):
        prefix = july + f"output_{mode}/classifier_guidance_{mode}/"
        data = rows(sources[prefix+"predictions.csv"]["text"])
        summary = json.loads(sources[prefix+"summary.json"]["text"])
        u = [float(r["maize_35s_up_pred"]) for r in data]; d = [float(r["maize_35s_down_pred"]) for r in data]
        current = sum(a>tu and b>td for a,b in zip(u,d))
        conflict.append({"mode":mode,"current_n":len(data),"current_up_mean":statistics.mean(u),
                         "current_down_mean":statistics.mean(d),"current_both_pass":current,
                         "historical_summary_both_pass":summary["above_both"],"status":"version_conflict_excluded_from_main_claims"})
    write_csv(out / "july08_version_conflict.csv", conflict)
    archived = rows(sources[july+"summary_classification/above_both.csv"]["text"])
    assert len(archived)==602 and len({r["sequence"] for r in archived})==602
    assert all(float(r["maize_35s_up_pred"])>tu and float(r["maize_35s_down_pred"])>td for r in archived)
    archived_counts=Counter(r["source"] for r in archived)
    assert archived_counts=={"both":597,"up":5}

    pcc = []
    for species,condition in (("Maize","up"),("Maize","down"),("Ara","down")):
        prefix = f"topic_new26/topic_enhancer/every_species/{species}/35s/{condition}/predict_model/"
        text = sources[prefix+"00result_train.out"]["text"]
        test = re.findall(r"Test Loss: ([0-9.]+) \| Test PCC: ([0-9.]+)",text)[-1]
        split = re.findall(r"Data split: Train=(\d+), Val=(\d+), Test=(\d+)",text)[-1]
        pcc.append({"species":species,"condition":condition,"test_loss_log":float(test[0]),
                    "test_pcc_log":float(test[1]),"train_n":int(split[0]),"val_n":int(split[1]),"test_n":int(split[2]),
                    "status":"training_log_read_not_test_predictions_recomputed"})
    write_csv(out / "predictor_test_log_verified.csv", pcc)
    real = rows(sources["topic_new26_aiCode/2026/08/04/credible_threshold/real_pred_comparison.csv"]["text"])
    full_pcc=[]
    for condition in ("up","down"):
        truth=np.array([float(r["Maize_35S_"+condition.upper()]) for r in real])
        pred=np.array([float(r["pred_"+condition]) for r in real])
        assert np.all(np.isfinite(truth)) and np.all(np.isfinite(pred))
        full_pcc.append({"condition":condition,"n":len(real),"pcc":float(np.corrcoef(truth,pred)[0,1]),
                         "evaluation_scope":"full_available_dataset_not_independent_test"})
    write_csv(out / "full_dataset_prediction_pcc.csv", full_pcc)
    report={"source_files_read":len(sources),"dataset_rows":len(raw),"valid_sequences":len(valid),
            "generated_archive_files_checked":len(inventory["generated_files"]),
            "generated_archive_sequences_checked":sum(r["count"] for r in inventory["generated_files"]),
            "maize_guided_groups_recomputed":len(sweep_rows),"maize_guided_sequences_recomputed":len(observation_rows),
            "ara_method_pairs_recomputed":len(paired),"july08_current_total_both":sum(r["current_both_pass"] for r in conflict),
            "july08_historical_summary_total_both":sum(r["historical_summary_both_pass"] for r in conflict),
            "july08_archived_filtered_rows":len(archived),
            "july08_archived_filtered_unique_sequences":len({r["sequence"] for r in archived}),
            "raw_data_publication":"DNA sequences and label tables not included",
            "checkpoint_hash_scope":"current files, not proof of historical bytes",
            "independent_seed_repeats_confirmed":False}
    (out/"verification_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",type=Path,required=True)
    args=parser.parse_args()
    analyse(args.source_dir)
