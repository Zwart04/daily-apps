"""Remove only retired frontend workers and this task's isolated test environment."""
import json
from cloudflare_access import ROOT,ACCOUNT,PRODUCTION_DB,api
from repository_safety import RETIRE
removed=json.loads((ROOT/'plans/repositories-deleted.json').read_text());assert len(removed['repositories'])==11
live=json.loads((ROOT/'plans/live-verification.json').read_text());assert live['domain_count']==50 and live['records_unchanged']
domains=api(f'accounts/{ACCOUNT}/workers/domains');expected=json.loads((ROOT/'plans/domain-migration.json').read_text())['aliases'];assert all(next(d for d in domains if d['hostname']==host)['service']=='zwart04-daily-apps' for host in expected)
workers=['zwart04-projects' if n=='zwart04-projects' else 'zwart04-'+n for n in RETIRE]
assert len(workers)==11 and not {'zwart04-daily-apps','zwart04-platform-v2'}&set(workers)
current={s['id'] for s in api(f'accounts/{ACCOUNT}/workers/scripts')};deleted=[]
for name in workers:
 assert not any(d['service']==name for d in domains)
 if name in current:api(f'accounts/{ACCOUNT}/workers/scripts/{name}','DELETE');deleted.append(name);print('RETIRED_FRONTEND_REMOVED',name,flush=True)
stage=json.loads((ROOT/'.migration-private/staging.json').read_text());assert stage['name']=='daily-workspace-stage-20261027' and stage['database']!=PRODUCTION_DB
for name in ['daily-workspace-stage','daily-workspace-stage-api']:
 if name in current:api(f'accounts/{ACCOUNT}/workers/scripts/{name}','DELETE');deleted.append(name)
info=api(f'accounts/{ACCOUNT}/d1/database/{stage["database"]}');assert info['name']==stage['name'];api(f'accounts/{ACCOUNT}/d1/database/{stage["database"]}','DELETE')
(ROOT/'plans/cloudflare-cleanup.json').write_text(json.dumps({'removed_worker_ids':deleted,'staging_database_deleted':True,'production_database_retained':True,'production_backend_retained':True,'unrelated_resources_removed':False},indent=2))
print('Task-only Cloudflare cleanup completed; production backend/database retained',flush=True)
