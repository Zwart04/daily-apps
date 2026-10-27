"""GitHub access is always pinned to Zwart04 and this task's explicit allowlist."""
from pathlib import Path
import os,json,subprocess,base64
ROOT=Path(__file__).resolve().parents[1]
CANONICAL='daily-apps'
RETIRE=['zwart04-projects','daganghub','renderforge','tutormind','servora','aquapure','clinic-os','legalbot-garuda','codeforgeme','gridcraft','stockgenie']
ALLOW={CANONICAL,*RETIRE}
PROTECTED={'agenmini','zwartos','zwartguard','rakaat-counter'}
token=subprocess.check_output(['gh','auth','token','--hostname','github.com','--user','Zwart04'],text=True).strip()
ENV={**os.environ,'GH_TOKEN':token};ENV.pop('GITHUB_TOKEN',None)
ENV.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+token).encode()).decode(),GIT_CONFIG_KEY_1='credential.helper',GIT_CONFIG_VALUE_1='')
def command(args,cwd=None,check=True):
 p=subprocess.run(args,cwd=cwd,env=ENV,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if check and p.returncode:raise RuntimeError(args[0]+' failed: '+p.stderr[:300])
 return p
def gh(*args,check=True):return command(['gh',*args],check=check)
def api(path):return json.loads(gh('api',path).stdout)
def git(path,*args):return command(['git','-C',str(path),*args]).stdout.strip()
assert api('user')['login']=='Zwart04'
def guard(name):
 assert name in ALLOW and name.lower() not in PROTECTED
 meta=api('repos/Zwart04/'+name)
 assert meta['owner']['login']=='Zwart04' and meta['full_name']=='Zwart04/'+name and not meta['private']
 return meta
