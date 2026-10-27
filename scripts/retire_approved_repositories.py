"""Delete only human-approved public repositories after all recovery and live gates pass."""
import json,datetime
from repository_safety import ROOT,RETIRE,guard,api,gh,git
review=json.loads((ROOT/'plans/consolidation-review-2026-10-27.json').read_text());assert review['deletion_approved'] and set(review['proposed_repository_deletions'])=={'Zwart04/'+n for n in RETIRE}
recovery=json.loads((ROOT/'plans/recovery-published.json').read_text());assert recovery['downloaded_from_retained_repo_and_verified'] and recovery['legacy_histories']==50 and recovery['pre_merge_histories']==12
live=json.loads((ROOT/'plans/live-verification.json').read_text());assert live['domain_count']==50 and live['records_unchanged'] and live['credential_hashes_unchanged'] and live['production_seed_records']==0
browser=json.loads((ROOT/'plans/browser-verification.json').read_text());native=json.loads((ROOT/'plans/native-features-verification.json').read_text());assert browser['project_task_focus_completion'] and native['javascript_sandbox_execution'] and native['video_decode_trim_webm_export'] and native['sensor_authenticated_ingestion'] and native['ai']['real_response']
release=api('repos/Zwart04/daily-apps/releases/tags/workspace-consolidation-backup');asset=next(a for a in release['assets'] if a['name']==recovery['file']);assert asset['size']==recovery['bytes'];assert not asset.get('digest') or asset['digest']=='sha256:'+recovery['sha256']
head=git(ROOT,'rev-parse','HEAD');assert api('repos/Zwart04/daily-apps/commits/main')['sha']==head
runs=api('repos/Zwart04/daily-apps/actions/runs?head_sha='+head)['workflow_runs'];assert any(r['status']=='completed' and r['conclusion']=='success' for r in runs),'Current source CI has not passed'
before={r['repository'].split('/')[1]:r for r in json.loads((ROOT/'.recovery/repositories-before-merge.json').read_text())}
# Preflight the complete exact list before deleting anything.
for name in RETIRE:
 meta=guard(name);assert meta['id']==before[name]['id'];assert api('repos/Zwart04/'+name+'/commits/'+meta['default_branch'])['sha']==before[name]['head'],'Source changed since backup: '+name
records=[]
for name in [n for n in RETIRE if n!='zwart04-projects']+['zwart04-projects']:
 meta=guard(name);assert meta['id']==before[name]['id'];assert api('repos/Zwart04/'+name+'/commits/'+meta['default_branch'])['sha']==before[name]['head']
 gh('api','--method','DELETE','repos/Zwart04/'+name)
 status=gh('api','--include','repos/Zwart04/'+name,check=False);assert status.returncode!=0 and '404' in status.stdout+status.stderr
 records.append({'repository':'Zwart04/'+name,'id':meta['id'],'verified_http_status':404,'backup_head':before[name]['head']})
 (ROOT/'plans/repositories-deleted.json').write_text(json.dumps({'deleted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical':'Zwart04/daily-apps','recovery_release':recovery['release'],'repositories':records},indent=2))
 print('APPROVED_REPOSITORY_DELETED_AND_404_VERIFIED',name,flush=True)
assert len(records)==11;guard('daily-apps')
