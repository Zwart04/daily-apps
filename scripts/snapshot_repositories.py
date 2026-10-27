from pathlib import Path
import json,hashlib,zipfile,subprocess,datetime
from repository_safety import ROOT,RETIRE,CANONICAL,guard,gh,git,api,ENV
RECOVERY=ROOT/'.recovery';RECOVERY.mkdir(exist_ok=True)
original=RECOVERY/'zwart04-unified-backup-2026-10-03.zip'
expected='cb149e1567b3538c26dfaa4b1000368d292e101e56ab3f50a1daae1ab05d5bd0'
if not original.exists():gh('release','download','unified-rebuild-backup','--repo','Zwart04/zwart04-projects','--pattern','zwart04-unified-backup.zip','--output',str(original))
assert hashlib.sha256(original.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(original) as z:assert z.testzip() is None;assert len([n for n in z.namelist() if n.endswith('.bundle')])==50
clones=RECOVERY/'clones';clones.mkdir(exist_ok=True);bundles=RECOVERY/'repositories';bundles.mkdir(exist_ok=True)
rows=[];releases=[]
for name in [CANONICAL,*RETIRE]:
 meta=guard(name);path=ROOT if name==CANONICAL else clones/name
 if not path.exists():command=['git','clone','https://github.com/Zwart04/'+name+'.git',str(path)];p=subprocess.run(command,env=ENV,capture_output=True,text=True);assert p.returncode==0,p.stderr[:200]
 assert git(path,'remote','get-url','origin')=='https://github.com/Zwart04/'+name+'.git'
 head=api('repos/Zwart04/'+name+'/commits/'+meta['default_branch'])['sha'];assert head==git(path,'rev-parse','HEAD')
 target=bundles/(name+'.bundle');git(path,'bundle','create',str(target),'--all');git(path,'bundle','verify',str(target))
 rows.append({'repository':'Zwart04/'+name,'id':meta['id'],'head':head,'file':'repositories/'+target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 release_list=json.loads(gh('api','repos/Zwart04/'+name+'/releases?per_page=100').stdout)
 for release in release_list:
  release_info={'repository':name,'tag':release['tag_name'],'id':release['id'],'body':release.get('body'),'assets':[]}
  for asset in release['assets']:
   if name=='zwart04-projects' and asset['name']=='zwart04-unified-backup.zip':continue
   # Public artifacts only; preserve named release assets before retiring their repository.
   folder=RECOVERY/'release-assets'/name/str(release['id']);folder.mkdir(parents=True,exist_ok=True)
   target=folder/asset['name'];assert target.parent==folder and target.name==asset['name']
   if not target.exists():gh('release','download',release['tag_name'],'--repo','Zwart04/'+name,'--pattern',asset['name'],'--dir',str(folder))
   digest=hashlib.sha256(target.read_bytes()).hexdigest()
   if asset.get('digest'):assert asset['digest']=='sha256:'+digest
   assert target.stat().st_size==asset['size']
   release_info['assets'].append({'name':asset['name'],'bytes':asset['size'],'sha256':digest,'file':str(target.relative_to(RECOVERY))})
  releases.append(release_info)
 print('SOURCE_SNAPSHOT_VERIFIED',name,flush=True)
(RECOVERY/'repositories-before-merge.json').write_text(json.dumps(rows,indent=2))
(RECOVERY/'release-assets.json').write_text(json.dumps(releases,indent=2))
print('All 12 current histories and existing recovery archive retained. Release assets:',sum(len(x['assets']) for x in releases),flush=True)
