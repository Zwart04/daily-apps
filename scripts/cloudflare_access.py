from pathlib import Path
import os,tomllib,json,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1]
ACCOUNT='06403b9ad7c7c150d97e34aad884419d'
ZONE='9de3dce23b7127fe44b10d9121b44e60'
PRODUCTION_DB='d48363f0-b33e-4cc6-80f1-8c197982f76e'
def token():
 for p in [Path.home()/'.config/.wrangler/config/default.toml',Path.home()/'.wrangler/config/default.toml']:
  if p.exists():return tomllib.loads(p.read_text())['oauth_token']
 raise RuntimeError('Wrangler OAuth token not found')
def api(path,method='GET',data=None):
 request=urllib.request.Request('https://api.cloudflare.com/client/v4/'+path,method=method,data=json.dumps(data).encode() if data is not None else None,headers={'Authorization':'Bearer '+token(),'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=60) as response:
   raw=response.read()
   if not raw and method=='DELETE' and 200<=response.status<300:return None
   result=json.loads(raw)
 except urllib.error.HTTPError as e:raise RuntimeError('Cloudflare API '+str(e.code)+': '+e.read().decode()[:400]) from None
 if not result.get('success'):raise RuntimeError('Cloudflare API failed: '+json.dumps(result.get('errors'))[:400])
 return result['result']
def query(database,sql,params=()):return api(f'accounts/{ACCOUNT}/d1/database/{database}/query','POST',{'sql':sql,'params':list(params)})[0]['results']
