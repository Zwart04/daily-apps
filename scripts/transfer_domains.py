"""Move only the exact 50 task hostnames captured before consolidation."""
import json
from cloudflare_access import ROOT,ACCOUNT,ZONE,api
from repository_safety import RETIRE
before=json.loads((ROOT/'.migration-private/production-before.json').read_text())
services={'zwart04-projects',*{'zwart04-'+n for n in ['daily-apps',*RETIRE] if n!='zwart04-projects'}}
expected=[d for d in before['domains'] if d['service'] in services]
assert len(expected)==50 and all(d['zone_id']==ZONE and d['hostname'].endswith('.zwart.qzz.io') for d in expected)
current={d['hostname']:d for d in api(f'accounts/{ACCOUNT}/workers/domains')}
for d in expected:
 live=current.get(d['hostname']);assert live is None or (live['service'] in services and live['zone_id']==ZONE)
 if live is None or live['service']!='zwart04-daily-apps':
  result=api(f'accounts/{ACCOUNT}/workers/domains','PUT',{'hostname':d['hostname'],'service':'zwart04-daily-apps','zone_id':ZONE,'zone_name':'zwart.qzz.io','enabled':True,'override_existing_origin':True,'override_existing_dns_record':True})
  assert result['service']=='zwart04-daily-apps' and result['hostname']==d['hostname']
 print('DOMAIN_UNIFIED',d['hostname'],flush=True)
final={d['hostname']:d for d in api(f'accounts/{ACCOUNT}/workers/domains')}
assert all(final[d['hostname']]['service']=='zwart04-daily-apps' for d in expected)
config=json.loads((ROOT/'wrangler.jsonc').read_text());config['routes']=[{'pattern':d['hostname'],'custom_domain':True} for d in sorted(expected,key=lambda d:d['hostname'])];(ROOT/'wrangler.jsonc').write_text(json.dumps(config,indent=2)+'\n')
(ROOT/'plans/domain-migration.json').write_text(json.dumps({'canonical':'daily-apps-app.zwart.qzz.io','worker':'zwart04-daily-apps','aliases':sorted(d['hostname'] for d in expected),'count':len(expected)},indent=2))
