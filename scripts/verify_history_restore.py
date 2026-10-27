import zipfile,subprocess,tempfile,json,hashlib
from repository_safety import ROOT,git,ENV
folder=ROOT/'.recovery';verified=[]
def verify(path,label,expected=None):
 with tempfile.TemporaryDirectory(prefix='zwart04-restore-') as tmp:
  p=subprocess.run(['git','clone','--mirror',str(path),tmp+'/restored.git'],env=ENV,capture_output=True,text=True)
  assert p.returncode==0,p.stderr[:200]
  git(tmp+'/restored.git','fsck','--full')
  refs=git(tmp+'/restored.git','show-ref').splitlines();assert refs
  if expected:assert any(r.split()[0]==expected for r in refs)
  verified.append({'source':label,'refs':len(refs),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'restored_and_fsck':True})
with tempfile.TemporaryDirectory(prefix='zwart04-legacy-') as tmp:
 with zipfile.ZipFile(folder/'zwart04-unified-backup-2026-10-03.zip') as z:
  for name in z.namelist():
   if name.endswith('.bundle'):
    target=__import__('pathlib').Path(tmp)/__import__('pathlib').Path(name).name;target.write_bytes(z.read(name));verify(target,'legacy/'+name)
print('Legacy histories restored and checked:',len(verified),flush=True)
assert len(verified)==50
for row in json.loads((folder/'repositories-before-merge.json').read_text()):verify(folder/row['file'],row['repository'],row['head'])
(ROOT/'plans/history-restoration.json').write_text(json.dumps({'original_archive_sha256':'cb149e1567b3538c26dfaa4b1000368d292e101e56ab3f50a1daae1ab05d5bd0','legacy_histories':50,'current_histories':12,'verified':verified},indent=2))
print('All 62 Git snapshots restored and fsck passed.',flush=True)
