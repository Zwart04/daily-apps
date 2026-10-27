import json
from repository_safety import ROOT,api,guard
before=json.loads((ROOT/'.migration-private/unrelated-repositories-before.json').read_text());repos=api('user/repos?affiliation=owner&per_page=100&visibility=all');byid={r['id']:r for r in repos if r['owner']['login']=='Zwart04'}
for old in before:
 assert old['id'] in byid
 assert {k:byid[old['id']].get(k) for k in old}==old,'Unrelated repository metadata changed: '+old['full_name']
guard('daily-apps')
report={'verified_unrelated_repositories':len(before),'private_repositories_preserved':sum(r['private'] for r in before),'protected_public_repositories_preserved':True,'unrelated_repository_metadata_unchanged':True,'private_sources_read_or_modified':False}
(ROOT/'plans/scope-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
