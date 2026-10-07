#!/usr/bin/env python3
"""Register current analysis artifacts; never upgrade author decisions."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def entry(path):
    return {"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "status":"verified","scope":"current_archive_analysis"}


if __name__=="__main__":
    path=ROOT/"data/manifest.json"
    manifest=json.loads(path.read_text(encoding="utf-8"))
    manifest.update(package_status="verified_archive_analysis_author_review_pending",
                    raw_results_verified=True,archive_figures_verified=True,
                    final_figures_verified=False,final_dataset_confirmed=False,
                    final_checkpoint_confirmed=False,final_threshold_confirmed=False)
    files=sorted((ROOT/"data/verified").glob("*.csv"))+[ROOT/"data/verified/verification_report.json",ROOT/"tables/table_s1_study_registry.csv"]
    manifest["analysis_files"]=[entry(p) for p in files]
    manifest["figure_outputs"]=[entry(p) for p in sorted((ROOT/"figures/results").glob("*")) if p.suffix in (".png",".svg")]
    manifest["final_result_files"]=[entry(ROOT/name) for name in (
        "data/verified/sequence_quality_summary.csv","data/verified/ara_guidance_methods_recomputed.csv",
        "data/verified/maize_guided_sweep_recomputed.csv","data/verified/homopolymer_sensitivity.csv")]
    manifest["review_docx"]=entry(ROOT/"manuscript/computational_sections_zh.docx")
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Registered",len(files),"analysis artifacts and",len(manifest["figure_outputs"]),"figure files; author decisions remain pending")
