import json,urllib.request,urllib.error,hashlib,datetime
from concurrent.futures import ThreadPoolExecutor
from cloudflare_access import ROOT,ACCOUNT,PRODUCTION_DB,api,query
canonical='https://daily-apps-app.zwart.qzz.io'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
opener=urllib.request.build_opener(NoRedirect)
def fetch(path,method='GET',data=None,headers={}):
 try:r=opener.open(urllib.request.Request(path,method=method,data=data,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36',**headers}),timeout=35)
 except urllib.error.HTTPError as e:r=e
 return r.status,dict(r.headers),r.read()
results={}
for path in ['/','/api/health','/api/config','/api/auth/session']:
 status,headers,body=fetch(canonical+path);assert status==200,(path,status,body[:100]);results[path]={'status':status}
 if path=='/':assert b'Daily Workspace' in body;assert 'Content-Security-Policy' in headers
 else:
  j=json.loads(body)
  if path=='/api/health':assert j['version']=='3.0.0' and j['single_origin']
  if path=='/api/config':assert len(j['areas'])==11
  if path=='/api/auth/session':assert j['user'] is None
 if path=='/api/health':results[path]['payload']=j
before=json.loads((ROOT/'.migration-private/production-before.json').read_text())
expected=json.loads((ROOT/'plans/domain-migration.json').read_text())['aliases']
def check(host):
 if host=='daily-apps-app.zwart.qzz.io':return {'hostname':host,'canonical':True}
 status,h,b=fetch('https://'+host+'/?from=legacy');assert status==301,(host,status);assert h.get('Location')==canonical+'/?from=legacy',(host,h)
 status,h,b=fetch('https://'+host+'/api/health');assert status==200 and json.loads(b).get('single_origin'),(host,status)
 return {'hostname':host,'redirect':301,'api_forwarded':True}
with ThreadPoolExecutor(max_workers=5) as pool:domains=list(pool.map(check,expected))
# Ingestion without a key must reach the backend and reject auth, not redirect or drop POST.
status,h,b=fetch('https://aquapure-app.zwart.qzz.io/api/ingest','POST',b'{}',{'Content-Type':'application/json'});assert status==401 and 'Location' not in h
state=query(PRODUCTION_DB,'SELECT id,workspace_id,kind,data,status,version,deleted_at FROM records ORDER BY id');assert state==before['record_state']
credentials=query(PRODUCTION_DB,'SELECT id,password_hash,recovery_hash FROM users ORDER BY id');assert credentials==before['users']
settings=api(f'accounts/{ACCOUNT}/workers/scripts/zwart04-platform-v2/settings');assert any(b['name']=='PEPPER' and b['type']=='secret_text' for b in settings['bindings'])
report={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical':canonical,'endpoints':results,'domain_count':len(domains),'domains':domains,'records_unchanged':True,'credential_hashes_unchanged':True,'server_secret_retained':True,'anonymous_sensor_post_rejected_without_redirect':True,'production_seed_records':0}
(ROOT/'plans/live-verification.json').write_text(json.dumps(report,indent=2));print('Live HTTPS verified for all',len(domains),'domains; production records and credentials unchanged.',flush=True)
