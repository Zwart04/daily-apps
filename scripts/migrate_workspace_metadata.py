"""Add only root workspaces and links; existing records, secrets, IDs and ACLs stay intact."""
import json,uuid,time,hashlib,sys
from cloudflare_access import ROOT,PRODUCTION_DB,query
AREA={'daily-apps','daganghub','renderforge','tutormind','servora','aquapure','clinic-os','legalbot-garuda','codeforgeme','gridcraft','stockgenie'}
folder=ROOT/'.migration-private';baseline=json.loads((folder/'production-before.json').read_text())
def fingerprint(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
def records():return query(PRODUCTION_DB,'SELECT id,workspace_id,kind,data,status,version,deleted_at FROM records ORDER BY id')
def users():return query(PRODUCTION_DB,'SELECT id,password_hash,recovery_hash FROM users ORDER BY id')
if '--apply' not in sys.argv:raise SystemExit('Use --apply only after stage checks and reviewed additive schema')
# Refuse a migration while existing data has drifted from the reviewed snapshot.
assert fingerprint(records())==fingerprint(baseline['record_state']),'New production record changes: capture a new baseline first'
assert users()==baseline['users'],'Credentials changed since baseline'
plan_path=folder/'workspace-migration-plan.json'
if not plan_path.exists():
 old=query(PRODUCTION_DB,"SELECT * FROM workspaces w WHERE product<>'daily-apps' AND NOT EXISTS(SELECT 1 FROM workspace_areas a WHERE a.workspace_id=w.id) ORDER BY created_at,id")
 groups=[]
 for w in old:
  assert w['product'] in AREA
  members=query(PRODUCTION_DB,'SELECT user_id,role FROM members WHERE workspace_id=? ORDER BY user_id,role',[w['id']])
  group=next((g for g in groups if g['owner_id']==w['owner_id'] and g['members']==members and w['product'] not in [a['product'] for a in g['areas']]),None)
  if group is None:
   group={'id':uuid.uuid4().hex,'owner_id':w['owner_id'],'name':'Ruang kerja utama' if not groups else 'Ruang kerja '+str(len(groups)+1),'members':members,'areas':[]};groups.append(group)
  group['areas'].append({'id':w['id'],'product':w['product']})
 plan_path.write_text(json.dumps(groups,indent=2));plan_path.chmod(0o600)
plan=json.loads(plan_path.read_text());now=int(time.time()*1000)
for group in plan:
 query(PRODUCTION_DB,"INSERT OR IGNORE INTO workspaces(id,product,name,owner_id,created_at) VALUES(?,'daily-apps',?,?,?)",[group['id'],group['name'],group['owner_id'],now])
 for m in group['members']:query(PRODUCTION_DB,'INSERT OR IGNORE INTO members(workspace_id,user_id,role) VALUES(?,?,?)',[group['id'],m['user_id'],m['role']])
 for a in group['areas']:query(PRODUCTION_DB,'INSERT OR IGNORE INTO workspace_areas(root_id,area,workspace_id,created_at) VALUES(?,?,?,?)',[group['id'],a['product'],a['id'],now])
 actual=query(PRODUCTION_DB,'SELECT user_id,role FROM members WHERE workspace_id=? ORDER BY user_id,role',[group['id']]);assert actual==group['members']
 for a in group['areas']:
  assert query(PRODUCTION_DB,'SELECT root_id,area FROM workspace_areas WHERE workspace_id=?',[a['id']])==[{'root_id':group['id'],'area':a['product']}]
  assert query(PRODUCTION_DB,'SELECT user_id,role FROM members WHERE workspace_id=? ORDER BY user_id,role',[a['id']])==group['members']
assert records()==baseline['record_state'];assert users()==baseline['users']
report={'new_visible_workspaces':len(plan),'preserved_original_workspaces':sum(len(g['areas']) for g in plan),'records_unchanged':True,'passwords_and_recovery_unchanged':True,'memberships_preserved':True,'record_fingerprint':fingerprint(records()),'production_seed_records':0}
(ROOT/'plans/data-migration-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
