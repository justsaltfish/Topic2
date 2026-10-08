"""Reanalyse private read-only JSON exports; no server connections.
Input files are described in results/00_model_selection/README.md.
"""
from pathlib import Path
import json,csv,io
from scipy.stats import wasserstein_distance
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source-dir',required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1];private=Path(args.source_dir)
items=[json.loads(l) for l in (private/'legacy_selection_fimo_metadata.jsonl').read_text().splitlines()];ref=next(i for i in items if i['kind']=='fimo' and i['source_relative_path'].endswith('res_real_data'))
results=[]
for item in items:
 if item['kind']=='fimo' and item is not ref:
  item['recomputed_position_wd']=float(wasserstein_distance(range(160),range(160),ref['position_counts'],item['position_counts']))
  assert (item['count'],item['categories']) in [(37327,648),(34025,649),(39813,648)]
  model='DDPM' if 'res_DDPM' in item['source_relative_path'] else 'DiT';epoch=int(item['source_relative_path'].split('/')[-1])
  source=next(i for i in json.loads((private/'sources_ppt_legacy.json').read_text()) if i['source_relative_path'].endswith('res_'+('DDPM' if model=='DDPM' else 'Dit')+'.csv') and '/final/' in i['source_relative_path'])
  row=next(r for r in csv.DictReader(io.StringIO(source['text'])) if r['epoch']==str(epoch));assert abs(float(row['wd'])-item['recomputed_position_wd'])<1e-10
  results.append((model,epoch,item['recomputed_position_wd']))
(root/'data/verified/legacy_selection_fimo_audit.json').write_text(json.dumps(items,indent=2)+'\n')
print('PASS: raw legacy FIMO selected counts/categories and WD match original CSV',results)
