import json,hashlib,tempfile
from pathlib import Path
from repository_safety import ROOT,guard,gh,api,git
folder=ROOT/'.recovery';report=json.loads((ROOT/'plans/recovery-package.json').read_text());archive=folder/report['file'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==report['sha256'];guard('daily-apps')
tag='workspace-consolidation-backup';head=git(ROOT,'rev-parse','HEAD');assert api('repos/Zwart04/daily-apps/commits/main')['sha']==head
notes=folder/'RELEASE-NOTES.md';notes.write_text('Source recovery sebelum penghapusan 11 repo yang disetujui.\n\nSatu ZIP mempertahankan arsip lama berisi 50 riwayat Git, 12 snapshot sebelum penggabungan, metadata repo, checksum, dan laporan restore. Semua bundle telah dipulihkan dengan clone dan git fsck. Snapshot dapat saling beririsan; ini bukan 62 repo berbeda. Database produksi dan secret tidak termasuk.\n\nSHA256: `'+report['sha256']+'`\n\nLihat RESTORE.md di dalam ZIP dan docs/DEPLOYMENT.md untuk pemulihan. Aplikasi terpadu tetap berada pada repo daily-apps.\n')
exists=gh('release','view',tag,'--repo','Zwart04/daily-apps',check=False)
if exists.returncode:gh('release','create',tag,'--repo','Zwart04/daily-apps','--target',head,'--title','Source recovery sebelum konsolidasi Daily Workspace','--notes-file',str(notes),str(archive),str(folder/'SHA256SUMS.txt'))
else:
 release=api('repos/Zwart04/daily-apps/releases/tags/'+tag)
 names={x['name'] for x in release['assets']}
 for p in [archive,folder/'SHA256SUMS.txt']:
  if p.name not in names:gh('release','upload',tag,str(p),'--repo','Zwart04/daily-apps')
release=api('repos/Zwart04/daily-apps/releases/tags/'+tag);asset=next(x for x in release['assets'] if x['name']==archive.name)
assert asset['size']==report['bytes']
if asset.get('digest'):assert asset['digest']=='sha256:'+report['sha256']
# Download from the retained repository and verify the actual bytes, not just upload metadata.
with tempfile.TemporaryDirectory(prefix='zwart04-remote-recovery-') as tmp:
 target=Path(tmp)/archive.name;gh('release','download',tag,'--repo','Zwart04/daily-apps','--pattern',archive.name,'--output',str(target));assert hashlib.sha256(target.read_bytes()).hexdigest()==report['sha256']
report.update(release=release['html_url'],asset_url=asset['browser_download_url'],server_digest=asset.get('digest'),downloaded_from_retained_repo_and_verified=True)
(ROOT/'plans/recovery-published.json').write_text(json.dumps(report,indent=2));print('RECOVERY_PUBLISHED_AND_DOWNLOADED_VERIFIED',release['html_url'],flush=True)
