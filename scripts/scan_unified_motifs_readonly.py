"""CPU FIMO scan core: existing FASTA only, --text output, no server files.
Call run(candidates, reference_sequence_set_sha256) after authorized SSH setup.
No SSH credentials or network operations are included in this module.
"""
from pathlib import Path
import subprocess,json,hashlib,csv,io

def run(candidates, reference_sequence_set_sha256):
    ROOT=Path('/home/yx/ytf')
    assert Path.cwd()==ROOT/'topic_new26_aiCode/2026/10/07/write-paper'
    FIMO=Path('/home/yx/meme/bin/fimo');DB=ROOT/'topic_new26/topic_enhancer/model_about/Database_comparison/jaspar/database/JASPAR2024_CORE_plants_non-redundant_pfms_meme.txt'
    assert hashlib.sha256(DB.read_bytes()).hexdigest()=='8444ed8c0d266b66f99d9bbe5aaa452599b0f4f5496b303a3effcedd474d2335'
    assert subprocess.run([str(FIMO),'--version'],capture_output=True,text=True,check=True).stdout.strip()=='5.4.1'
    print(json.dumps({'kind':'environment','fimo_version':'5.4.1','fimo_executable_sha256':hashlib.sha256(FIMO.read_bytes()).hexdigest(),'database_relative_path':str(DB.relative_to(ROOT)),'database_sha256':hashlib.sha256(DB.read_bytes()).hexdigest(),'settings':{'text':True,'no_qvalue':True,'pvalue_threshold':0.0001,'background':'--nrdb--','motif_pseudocount':0.1,'both_strands':True,'position_pseudocount':0},'server_output_files_created':False}),flush=True)
    candidates=list(candidates)
    ref=ROOT/'topic_all/evaluate_effect/test/real_data/NG_enhancer_data.fasta'
    seqs=[l.strip().upper() for l in ref.read_text().splitlines() if l and not l.startswith('>')]
    assert len(seqs)==11984 and all(len(s)==160 and set(s)<=set('ACGT') for s in seqs)
    assert hashlib.sha256('\n'.join(sorted(set(seqs))).encode()).hexdigest()==reference_sequence_set_sha256
    cases=[{'model':'Real reference','epoch':None,'source_relative_path':str(ref.relative_to(ROOT)),'source_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'source_n':11984,'selected_ids':None}]+candidates
    for case in cases:
     fasta=ROOT/case['source_relative_path']
     assert hashlib.sha256(fasta.read_bytes()).hexdigest()==case['source_sha256']
     selected=None if case['selected_ids'] is None else set(case['selected_ids'])
     cmd=[str(FIMO),'--text','--no-qvalue','--thresh','1e-4','--bfile','--nrdb--','--motif-pseudo','0.1','--verbosity','0',str(DB),str(fasta)]
     child=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
     hist=[0]*160;total=0;scanned_hits=0;categories=set();motifs={};perseq={};header=child.stdout.readline().strip().split('\t')
     assert header[:3]==['motif_id','motif_alt_id','sequence_name'],header
     for line in child.stdout:
      if not line.strip() or line.startswith('#'):continue
      fields=line.rstrip('\n').split('\t');row=dict(zip(header,fields));scanned_hits+=1
      if selected is not None and row['sequence_name'] not in selected:continue
      assert float(row['p-value'])<=0.0001
      mid=(int(row['start'])+int(row['stop']))//2;assert 0<=mid<160
      hist[mid]+=1;total+=1;categories.add(row['motif_alt_id']);motifs[row['motif_id']]=motifs.get(row['motif_id'],0)+1;perseq[row['sequence_name']]=perseq.get(row['sequence_name'],0)+1
     error=child.stderr.read();assert child.wait()==0,error
     result={k:case[k] for k in ['model','epoch','source_relative_path','source_sha256','source_n']};result.update(kind='motif_scan',n_selected=11984 if selected is None else len(selected),hits_in_scanned_source=scanned_hits,hits_in_selected_records=total,num_categories=len(categories),position_counts=hist,motif_counts=motifs,per_sequence_hit_counts=perseq,stderr=error)
     assert sum(hist)==total and sum(motifs.values())==total and sum(perseq.values())==total
     print(json.dumps(result),flush=True)
