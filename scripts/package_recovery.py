"""Public source recovery only: no production exports, sessions, credentials or env files."""
import zipfile,json,hashlib
from repository_safety import ROOT
folder=ROOT/'.recovery';report=json.loads((ROOT/'plans/history-restoration.json').read_text());assert len(report['verified'])==62
files=[folder/'zwart04-unified-backup-2026-10-03.zip',folder/'repositories-before-merge.json',folder/'release-assets.json',*sorted((folder/'repositories').glob('*.bundle')),*sorted((folder/'github-metadata').glob('*.json'))]
if (folder/'release-assets').exists():files.extend(p for p in (folder/'release-assets').rglob('*') if p.is_file())
assert len(list((folder/'repositories').glob('*.bundle')))==12
assert len(list((folder/'github-metadata').glob('*.json')))==11
manifest=[]
for p in files:
 assert p.is_file() and p.is_relative_to(folder) and '.migration-private' not in p.parts
 manifest.append({'file':str(p.relative_to(folder)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest_path=folder/'RECOVERY-MANIFEST.json';manifest_path.write_text(json.dumps({'legacy_histories':50,'pre_merge_histories':12,'files':manifest,'verification':'Every Git bundle cloned and git fsck --full passed. Original legacy ZIP SHA256 retained.','private_production_data_included':False},indent=2))
archive=folder/'zwart04-workspace-recovery-2026-10-27.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
 for p in [*files,manifest_path]:z.write(p,p.relative_to(folder))
 z.write(ROOT/'plans/history-restoration.json','verification/history-restoration.json');z.write(ROOT/'plans/REBUILD-PLAN.md','verification/REBUILD-PLAN.md');z.write(ROOT/'docs/DEPLOYMENT.md','RESTORE.md')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for entry in manifest:assert hashlib.sha256(z.read(entry['file'])).hexdigest()==entry['sha256']
digest=hashlib.sha256(archive.read_bytes()).hexdigest();(folder/'SHA256SUMS.txt').write_text(digest+'  '+archive.name+'\n')
(ROOT/'plans/recovery-package.json').write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':digest,'legacy_histories':50,'pre_merge_histories':12,'zip_integrity_verified':True,'contained_file_hashes_verified':True,'private_production_data_included':False},indent=2))
print('Public recovery package verified:',archive.stat().st_size,'bytes; SHA256',digest,flush=True)
