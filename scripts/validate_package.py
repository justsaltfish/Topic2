#!/usr/bin/env python3
"""Validate working-draft consistency; submission mode rejects unresolved data."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

from docx import Document
from export_docx import ROOT, PARTS, merged_text, paragraphs


def validate(submission=False):
    errors = []
    required = list(PARTS) + [
        "README.md", "plan/outline.md", "plan/project-overview.md",
        "plan/experiment-protocol.md", "plan/task-packets/computational-sections.md",
        "plan/review/method-experiment-traceability.md", "tables/table-schema.md",
        "figures/data-manifest.md", "figures/figure-plan.md",
        "evidence/missing-items.md", "evidence/missing-items.json",
        "data/manifest.json", "submission/CHECKLIST.md",
        "manuscript/computational_sections_zh.md",
        "manuscript/computational_sections_zh.docx",
    ]
    absent = [name for name in required if not (ROOT / name).is_file()]
    if absent:
        return ["Missing files: " + ", ".join(absent)]
    merged = (ROOT / "manuscript/computational_sections_zh.md").read_text(encoding="utf-8")
    if merged != merged_text():
        errors.append("Merged Markdown is stale; rerun export_docx.py")
    expected = [content for _, content in paragraphs(merged_text())]
    doc = Document(ROOT / "manuscript/computational_sections_zh.docx")
    actual = [p.text for p in doc.paragraphs if p.text.strip()]
    if actual != expected:
        errors.append("DOCX paragraphs differ from Markdown source")
    result_headings = re.findall(r"^## Results (\d+)\.", merged, re.MULTILINE)
    if result_headings != ["1", "2"]:
        errors.append("The manuscript must contain exactly Results 1 and Results 2")
    gaps = json.loads((ROOT / "evidence/missing-items.json").read_text(encoding="utf-8"))
    gap_ids = {g["id"] for g in gaps}
    if len(gap_ids) != len(gaps):
        errors.append("Duplicate missing-item IDs")
    used = set(re.findall(r"\bM\d{2}\b", merged))
    if used - gap_ids:
        errors.append("Undefined gap IDs: " + ", ".join(sorted(used - gap_ids)))
    if gap_ids - used:
        errors.append("Missing-item IDs not represented in manuscript: " + ", ".join(sorted(gap_ids - used)))
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    for item in manifest["history_files"]:
        path = ROOT / item["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            errors.append("History file absent or hash mismatch: " + item["path"])
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if any(row["status"] != "index_summary_not_raw_verified" for row in rows):
            errors.append("Historical summary mislabeled as verified: " + item["path"])
    for path in (ROOT / "data/templates").glob("*.csv"):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            if len(header) != len(set(header)) or not header:
                errors.append("Invalid template header: " + path.name)
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            target = target.split("#", 1)[0]
            if not (path.parent / target).exists():
                errors.append(f"Broken local link in {path.relative_to(ROOT)}: {target}")
        if any(marker in text for marker in ("BEGIN OPENSSH PRIVATE KEY", "218.199.69.4", "topic_ai_ed25519")):
            errors.append("Infrastructure identity leaked: " + str(path.relative_to(ROOT)))
    if re.search(r"^\s*(?:[-*+]\s|\d+\.\s)", merged, re.MULTILINE):
        errors.append("Bullet-like manuscript prose")
    if submission:
        unresolved = [g["id"] for g in gaps if g["status"] != "resolved"]
        if unresolved or "[待核实" in merged:
            errors.append("Unresolved manuscript evidence: " + ", ".join(unresolved))
        if manifest.get("package_status") != "submission_ready":
            errors.append("Package remains a working draft")
        for flag in ("raw_results_verified", "final_figures_verified", "final_dataset_confirmed",
                     "final_checkpoint_confirmed", "final_threshold_confirmed"):
            if not manifest.get(flag):
                errors.append("Submission prerequisite false: " + flag)
        for key in ("final_result_files", "figure_outputs"):
            items = manifest.get(key, [])
            if not items:
                errors.append("No verified artifacts: " + key)
            for item in items:
                path = ROOT / item["path"]
                if item.get("status") != "verified" or not path.is_file() or path.stat().st_size == 0:
                    errors.append("Unverified or absent artifact: " + item["path"])
                elif hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
                    errors.append("Artifact hash mismatch: " + item["path"])
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", action="store_true")
    args = parser.parse_args()
    findings = validate(args.submission)
    if findings:
        for finding in findings:
            print("FAIL:", finding)
        sys.exit(1)
    print("PASS:", "submission prerequisites" if args.submission else "working-draft structure and synchronization")
