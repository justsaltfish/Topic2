"""Read-only CPU evaluation of fixed Ara UP best_model.pt.

Reconstructs the legacy dictionary-filtered dataset, seed 42 and fractional
80/10/10 split. Fraction rounding follows modern torch.random_split semantics:
floor each length, then distribute remaining records from the first split.
This is a documented reconstruction, not recovery of historical split indices.
"""
import os,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.dont_write_bytecode=True
import json,hashlib,platform,importlib.util,math,random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr
ROOT=Path('/home/yx/ytf')
assert Path.cwd().resolve()==ROOT/'topic_new26_aiCode/2026/10/07/write-paper'
assert not torch.cuda.is_available()
torch.set_num_threads(2)
data=ROOT/'topic_all/topic2_Diffusion/data/NG_enhancer_data.csv'
checkpoint=ROOT/'topic_new26/topic_enhancer/every_species/Ara/35s/up/predict_model/best_model.pt'
source=ROOT/'topic_new26/topic_enhancer/model_about/predict_model/predict_model.py'
train_source=ROOT/'topic_new26/topic_enhancer/model_about/predict_model/train.py'
data_hash=hashlib.sha256(data.read_bytes()).hexdigest()
weight_hash=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
assert data_hash=='f1bd56a88d5f8d1baabcb29e855a8c11f404dcf5aacc1b184c024287fccd8f49'
assert weight_hash=='eeb77dd0768bdc6ac8060f67d3304d618014828ba1fa2b52d039b847721667f5'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='93d5d3294ff671a06a554a4ad03ccebb554d6a07aac88dc7bbba0db8da79ac66'
assert hashlib.sha256(train_source.read_bytes()).hexdigest()=='2b7540001b0c9be082867a5a35c90dfbe38dda7e96a7ce83277bcdd2bf4adc8f'
spec=importlib.util.spec_from_file_location('readonly_legacy_predictor',str(source))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
df=pd.read_csv(data)
# Match the legacy dictionary: preserve the first insertion order, last label
# for exact duplicate sequence keys (the current eligible source is unique).
records={}
for i,seq,value in zip(df.index,df.Sequence,df.Arabidopsis_35S_UP):
 if pd.notna(value) and isinstance(seq,str) and all(c in 'ACGTacgt' for c in seq):
  records[seq]=(int(i),seq,float(value))
records=list(records.values())
assert len(records)==11971, len(records)
seed=42
random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
ratios=[0.8,0.1,0.1]
sizes=[math.floor(len(records)*ratio) for ratio in ratios]
for i in range(len(records)-sum(sizes)):sizes[i%len(sizes)]+=1
assert sizes==[9577,1197,1197], sizes
# Global seeded generator matches legacy main flow; no model initialization
# or other Torch random operation occurs between manual_seed and splitting.
splits=torch.utils.data.random_split(list(range(len(records))),sizes)
indices=splits[2].indices
net=module.Net()
net.load_state_dict(torch.load(str(checkpoint),map_location='cpu'),strict=True)
net.eval()
predictions=[]
with torch.no_grad():
 for start in range(0,len(indices),64):
  batch=[records[i] for i in indices[start:start+64]]
  assert all(len(r[1])==160 for r in batch)
  x=np.asarray([[[float(c==base) for c in r[1].upper()] for base in 'ACGT'] for r in batch],dtype=np.float32)
  predictions.extend(net(torch.from_numpy(x)).cpu().numpy().tolist())
labels=np.asarray([records[i][2] for i in indices],dtype=np.float32)
preds=np.asarray(predictions,dtype=np.float32)
assert np.isfinite(labels).all() and np.isfinite(preds).all()
membership=[{'dataset_index':i,'csv_row_index':records[i][0],
 'sequence_sha256':hashlib.sha256(records[i][1].upper().encode()).hexdigest()} for i in indices]
memberhash=hashlib.sha256(json.dumps(membership,sort_keys=True,separators=(',',':')).encode()).hexdigest()
print(json.dumps({'kind':'environment','torch':torch.__version__,'numpy':np.__version__,
 'pandas':pd.__version__,'python':platform.python_version(),'device':'cpu',
 'model_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'training_source_sha256':hashlib.sha256(train_source.read_bytes()).hexdigest(),
 'dataset_sha256':data_hash,'fractional_rounding':'floor_each_then_round_robin_remainder',
 'author_authorized_reconstruction':True}),flush=True)
print(json.dumps({'kind':'test_result','species':'Ara','direction':'up','seed':seed,
 'train_n':sizes[0],'val_n':sizes[1],'test_n':sizes[2],
 'pcc':float(pearsonr(preds,labels)[0]),
 'mse':float(np.mean((preds.astype(np.float64)-labels.astype(np.float64))**2)),
 'checkpoint_sha256':weight_hash,'ordered_test_membership_sha256':memberhash,
 'split_status':'author_authorized_legacy_fractional_split_reconstruction;historical_membership_not_recovered',
 'observations':[dict(m,target=float(y),prediction=float(p)) for m,y,p in zip(membership,labels,preds)]}),flush=True)
