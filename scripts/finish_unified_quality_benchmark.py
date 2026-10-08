"""Join same-sample quality metrics with new read-only FIMO scan exports."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.stats import wasserstein_distance
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',required=True)
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1];private=Path(args.source_dir)
scans=[json.loads(l) for l in (private/'unified_fimo_readonly.jsonl').read_text().splitlines()];env=scans[0]
ref=next(s for s in scans if s.get('model')=='Real reference')
rows=list(csv.DictReader((repo/'data/verified/unified_quality_candidates_pre_fimo.csv').open()))
assert len(scans)==len(rows)+2
for row in rows:
 scan=next(s for s in scans if s.get('model')==row['model'] and str(s.get('epoch'))==row['epoch'])
 assert scan['source_sha256']==row['source_sha256'];assert scan['n_selected']==int(row['n'])==1000
 assert sum(scan['position_counts'])==scan['hits_in_selected_records'] and sum(scan['motif_counts'].values())==scan['hits_in_selected_records']
 row['jaspar2024_position_wd']=float(wasserstein_distance(range(160),range(160),ref['position_counts'],scan['position_counts']))
 row['jaspar2024_hits']=scan['hits_in_selected_records'];row['jaspar2024_categories']=scan['num_categories'];row['jaspar2024_hits_per_sequence']=scan['hits_in_selected_records']/1000
 row['comparison_status']='same_reference_sample_size_database_and_scan_parameters;historical_generated_batches'
# Protocol hashes preserve the precise scan and sampling state.
protocol=json.loads((repo/'data/verified/unified_quality_protocol.json').read_text());protocol.update(fimo=env,motif_position='floor((start+stop)/2), positions0..159, observed hit weights only; no positional pseudocount',fimo_real_fasta_source=ref['source_relative_path'],fimo_real_fasta_sha256=ref['source_sha256'],new_analysis=True,new_training_or_generation=False,server_files_written=False)
(repo/'data/verified/unified_quality_protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
with (repo/'data/verified/unified_quality_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
(repo/'data/verified/unified_fimo_scan_results.json').write_text(json.dumps(scans,indent=2)+'\n')
uvit=json.loads((private/'sources_uvit4_sweep_fasta.json').read_text())
with (repo/'data/verified/unified_uvit4_source_manifest.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['source_relative_path','size','sha256'],lineterminator='\n');w.writeheader();w.writerows({k:i[k] for k in w.fieldnames} for i in uvit)
for row in rows:print(row['model'],row['epoch'],'PCC',row['sixmer_pcc'],'GCWD',row['gc_wasserstein'],'MOTIF_WD',row['jaspar2024_position_wd'])
print('PASS: all candidates same 1,000-record sample across metrics; motif hit sums; source hashes; common reference and database')
