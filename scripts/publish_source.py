import json,subprocess,os
from repository_safety import ROOT,guard,api,git,ENV
meta=guard('daily-apps');remote=api('repos/Zwart04/daily-apps/commits/'+meta['default_branch'])['sha'];assert remote==git(ROOT,'rev-parse','HEAD'),'Remote head changed; reconcile before pushing'
tracked=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True);assert '.migration-private' not in tracked and '.recovery' not in tracked
subprocess.run(['git','add','--all'],cwd=ROOT,env=ENV,check=True)
files=git(ROOT,'diff','--cached','--name-only').splitlines();assert files
assert not any(f.startswith(('.recovery/','.migration-private/','node_modules/','dist/')) or f.endswith(('.bundle','.zip','.sql.export')) for f in files)
assert not any(f in ['wrangler.stage.json','platform/wrangler.stage.json'] for f in files)
# Use existing configured author identity when present; otherwise identify the assistant explicitly.
ident=subprocess.run(['git','var','GIT_AUTHOR_IDENT'],cwd=ROOT,env=ENV,capture_output=True,text=True)
commit_env=dict(ENV)
if ident.returncode:commit_env.update(GIT_AUTHOR_NAME='Codex',GIT_AUTHOR_EMAIL='codex@openai.com',GIT_COMMITTER_NAME='Codex',GIT_COMMITTER_EMAIL='codex@openai.com')
subprocess.run(['git','commit','-m','Unify all products into Daily Workspace with one login and preserved data'],cwd=ROOT,env=commit_env,check=True)
subprocess.run(['git','push','origin','HEAD:'+meta['default_branch']],cwd=ROOT,env=ENV,check=True)
head=git(ROOT,'rev-parse','HEAD');assert api('repos/Zwart04/daily-apps/commits/'+meta['default_branch'])['sha']==head
print('SOURCE_PUBLISHED',head,flush=True)
