import json,datetime,hashlib,os
from cloudflare_access import ROOT,ACCOUNT,ZONE,PRODUCTION_DB,api,query
folder=ROOT/'.migration-private';folder.mkdir(exist_ok=True,mode=0o700)
assert any(x['id']==ACCOUNT for x in api('accounts'))
zone=api('zones/'+ZONE);assert zone['name']=='zwart.qzz.io' and zone['account']['id']==ACCOUNT
database=api(f'accounts/{ACCOUNT}/d1/database/{PRODUCTION_DB}');assert database['name']=='zwart04-unified-v2'
counts=query(PRODUCTION_DB,"SELECT 'users' AS kind,count(*) AS count FROM users UNION ALL SELECT 'workspaces',count(*) FROM workspaces UNION ALL SELECT 'records',count(*) FROM records UNION ALL SELECT 'members',count(*) FROM members")
workspaces=query(PRODUCTION_DB,'SELECT * FROM workspaces ORDER BY id')
record_state=query(PRODUCTION_DB,'SELECT id,workspace_id,kind,data,status,version,deleted_at FROM records ORDER BY id')
users=query(PRODUCTION_DB,'SELECT id,password_hash,recovery_hash FROM users ORDER BY id')
settings=api(f'accounts/{ACCOUNT}/workers/scripts/zwart04-platform-v2/settings')
assert any(b['name']=='PEPPER' and b['type']=='secret_text' for b in settings['bindings'])
assert any(b.get('id')==PRODUCTION_DB and b['name']=='DB' for b in settings['bindings'])
bookmark=api(f'accounts/{ACCOUNT}/d1/database/{PRODUCTION_DB}/time_travel/bookmark')
capture={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':counts,'workspaces':workspaces,'record_state':record_state,'users':users,'bookmark':bookmark,'domains':api(f'accounts/{ACCOUNT}/workers/domains'),'databases':api(f'accounts/{ACCOUNT}/d1/database')}
target=folder/'production-before.json'
if target.exists():raise RuntimeError('Existing pre-migration snapshot preserved')
target.write_text(json.dumps(capture,indent=2));target.chmod(0o600)
safe={'captured_at':capture['captured_at'],'counts':counts,'workspace_count_by_product':{p:sum(w['product']==p for w in workspaces) for p in sorted({w['product'] for w in workspaces})},'production_database_unchanged':True,'server_secret_present':True,'time_travel_bookmark_captured':True,'record_fingerprint':hashlib.sha256(json.dumps(record_state,sort_keys=True).encode()).hexdigest()}
(ROOT/'plans/production-baseline.json').write_text(json.dumps(safe,indent=2))
print('PRODUCTION_BASELINE',json.dumps(counts),'server secret retained; Time Travel bookmark saved privately',flush=True)
