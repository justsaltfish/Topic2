"""CPU-only checkpoint evaluation; run on stdin, never writes server files.

Seven project_PredictModel predictors: rebuild seeded random_split using current
CSV and documented sizes. This does not recover archived historical indices.
Ara UP is deliberately excluded until its historical split is resolved/approved.
Prints JSON Lines with individual test predictions (keep those exports private).
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import sys
sys.dont_write_bytecode = True
import json, hashlib, platform, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr

ROOT = Path('/home/yx/ytf')
EXPECTED_CWD = ROOT / 'topic_new26_aiCode/2026/10/07/write-paper'
assert Path.cwd().resolve() == EXPECTED_CWD
assert not torch.cuda.is_available(), 'CPU-only evaluation required'
torch.set_num_threads(2)
source = ROOT / 'topic_new26/topic_enhancer/model_about/project_PredictModel/model.py'
spec = importlib.util.spec_from_file_location('readonly_predictor', str(source))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = ROOT / 'topic_all/topic2_Diffusion/data/NG_enhancer_data.csv'
assert hashlib.sha256(data.read_bytes()).hexdigest() == 'f1bd56a88d5f8d1baabcb29e855a8c11f404dcf5aacc1b184c024287fccd8f49'
df = pd.read_csv(data)
models = [
 ('Ara','down','Arabidopsis_35S_DOWN',42,(9571,1196,1197),'9b7b8a843fe722e7fbe3cbc5d6b816acbe8ae1b66ae9499bafeab76281de5039'),
 ('Benthamiana','up','Benthamiana_35S_UP',42,(9579,1197,1198),'8771d14a170e2081e86ca7dfc6d7ac4c96821b90b9a1b5aee219dd34c647b96b'),
 ('Benthamiana','down','Benthamiana_35S_DOWN',42,(9580,1197,1199),'a34861616a0fd1d6821beacf4f69d1003a564dd854cfbe339f945307768bbe9f'),
 ('Maize','up','Maize_35S_UP',45,(9580,1197,1198),'82b4b3893fa50044ad75e67f98c475f2e892c1a097ffdd7e1bc1297bc0d11891'),
 ('Maize','down','Maize_35S_DOWN',42,(9581,1197,1199),'ca6bea1785991030875d1c4030a02a9868162b551d5aa8e3d042b48ce57c9bce'),
 ('Tomato','up','Tomato_35S_UP',42,(9574,1196,1198),'401dc4ba0971922b382efa22cd4b952324a60c91a801ba7eb878a4697469e1ec'),
 ('Tomato','down','Tomato_35S_DOWN',42,(9580,1197,1198),'1be48fbad9f3b030affcc7709f4d12bc553d22c336de7258c79e9d8510bc81d1'),
]
print(json.dumps({'kind':'environment','torch':torch.__version__,'numpy':np.__version__,
 'pandas':pd.__version__,'python':platform.python_version(),'device':'cpu',
 'model_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'dataset_sha256':hashlib.sha256(data.read_bytes()).hexdigest()}),flush=True)
for species,direction,target,seed,sizes,expected_hash in models:
 records=[(int(i),seq,float(value)) for i,seq,value in zip(df.index,df.Sequence,df[target])
          if pd.notna(value) and isinstance(seq,str) and all(c in 'ACGTacgt' for c in seq)]
 assert len(records)==sum(sizes),(species,direction,len(records),sizes)
 split=torch.utils.data.random_split(list(range(len(records))),list(sizes),
             generator=torch.Generator().manual_seed(seed))
 indices=split[2].indices
 checkpoint=ROOT / ('topic_new26/topic_enhancer/every_species/%s/35s/%s/predict_model/best_model.pth'%(species,direction))
 weight_hash=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
 assert weight_hash==expected_hash
 net=module.Net()
 net.load_state_dict(torch.load(str(checkpoint),map_location='cpu'),strict=True)
 net.eval()
 predictions=[]
 with torch.no_grad():
  for start in range(0,len(indices),64):
   selected=[records[i] for i in indices[start:start+64]]
   assert all(len(r[1])==160 for r in selected)
   x=np.array([[[float(c==base) for c in r[1].upper()] for base in 'ACGT'] for r in selected],dtype=np.float32)
   predictions.extend(net(torch.from_numpy(x)).cpu().numpy().tolist())
 labels=np.asarray([records[i][2] for i in indices],dtype=np.float32)
 preds=np.asarray(predictions,dtype=np.float32)
 assert np.isfinite(preds).all() and np.isfinite(labels).all()
 memberships=[{'dataset_index':i,'csv_row_index':records[i][0],
  'sequence_sha256':hashlib.sha256(records[i][1].upper().encode()).hexdigest()} for i in indices]
 ordered_hash=hashlib.sha256(json.dumps(memberships,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 result={'kind':'test_result','species':species,'direction':direction,'seed':seed,
 'train_n':sizes[0],'val_n':sizes[1],'test_n':sizes[2],
 'pcc':float(pearsonr(preds,labels)[0]),'mse':float(np.mean((preds.astype(np.float64)-labels.astype(np.float64))**2)),
 'checkpoint_sha256':weight_hash,'ordered_test_membership_sha256':ordered_hash,
 'split_status':'reconstructed_from_current_source_csv_seed_and_logged_sizes',
 'observations':[dict(m,target=float(y),prediction=float(p)) for m,y,p in zip(memberships,labels,preds)]}
 print(json.dumps(result),flush=True)
