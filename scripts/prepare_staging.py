import json,secrets,subprocess
from cloudflare_access import ROOT,ACCOUNT,api,query
name='daily-workspace-stage-20261027'
databases=api(f'accounts/{ACCOUNT}/d1/database')
db=next((d for d in databases if d['name']==name),None)
if db is None:db=api(f'accounts/{ACCOUNT}/d1/database','POST',{'name':name})
id=db.get('uuid') or db['id']
assert id!='d48363f0-b33e-4cc6-80f1-8c197982f76e'
folder=ROOT/'.migration-private';folder.mkdir(exist_ok=True,mode=0o700)
(folder/'staging.json').write_text(json.dumps({'database':id,'name':name}));(folder/'staging.json').chmod(0o600)
config={'name':'daily-workspace-stage-api','account_id':ACCOUNT,'main':'worker.js','compatibility_date':'2026-10-27','workers_dev':False,'d1_databases':[{'binding':'DB','database_name':name,'database_id':id}],'ai':{'binding':'AI'}}
(ROOT/'platform/wrangler.stage.json').write_text(json.dumps(config,indent=2))
config=json.loads((ROOT/'wrangler.jsonc').read_text());config.update(name='daily-workspace-stage',workers_dev=True,routes=[],services=[{'binding':'BACKEND','service':'daily-workspace-stage-api'}],vars={'PRODUCT':'daily-apps','CANONICAL_HOST':'staging-app.zwart.qzz.io'})
(ROOT/'wrangler.stage.json').write_text(json.dumps(config,indent=2))
# A separate random stage pepper is supplied on stdin; production's existing secret is never read.
p=subprocess.run([str(ROOT/'node_modules/.bin/wrangler'),'secret','put','PEPPER','--config','platform/wrangler.stage.json'],cwd=ROOT,input=secrets.token_hex(48)+'\n',text=True,capture_output=True)
if p.returncode:raise RuntimeError(p.stdout+p.stderr)
print('Staging database and separate staging secret prepared',flush=True)
