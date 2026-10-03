"""DailyOS CLI: real local tools. No network telemetry or fabricated output."""
import argparse,datetime,hashlib,json,os,pathlib,re,shutil,socket,ssl,subprocess,sys,uuid
EXCLUDED={'.git','node_modules','.next','.venv','venv','dist','build','__pycache__','.wrangler'}
SENSITIVE=re.compile(r'(^\.env($|\.)|token|secret|credential|private.?key|\.pem$|\.p12$)',re.I)
def context(args):
 root=pathlib.Path(args.path).resolve(strict=True)
 if not root.is_dir():raise ValueError('Path harus direktori.')
 output=[];budget=args.max_bytes;total=0
 for current,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in EXCLUDED and not pathlib.Path(current,d).is_symlink())
  for name in sorted(files):
   p=pathlib.Path(current,name)
   if p.is_symlink() or SENSITIVE.search(name) or p.stat().st_size>args.file_bytes:continue
   raw=p.read_bytes()
   if b'\0' in raw:continue
   try:text=raw.decode('utf-8')
   except UnicodeDecodeError:continue
   if total+len(raw)>budget:continue
   total+=len(raw);output.append(f'\n--- {p.relative_to(root).as_posix()} ---\n{text}')
 result=''.join(output)
 if args.output:pathlib.Path(args.output).write_text(result,encoding='utf-8');print(f'{len(output)} berkas, {total} bytes -> {args.output}')
 else:print(result)
def certificate(args):
 context=ssl.create_default_context()
 with socket.create_connection((args.host,args.port),timeout=10) as raw:
  with context.wrap_socket(raw,server_hostname=args.host) as stream:
   cert=stream.getpeercert();expires=datetime.datetime.strptime(cert['notAfter'],'%b %d %H:%M:%S %Y %Z').replace(tzinfo=datetime.timezone.utc);days=(expires-datetime.datetime.now(datetime.timezone.utc)).days
   print(json.dumps({'host':args.host,'port':args.port,'validated':True,'expires_at':expires.isoformat(),'days_remaining':days,'warning':days<args.warn_days},indent=2))
def gittree(args):
 root=pathlib.Path(args.path).resolve(strict=True);repos=[]
 for current,dirs,files in os.walk(root,followlinks=False):
  if '.git' in dirs or '.git' in files:
   r=subprocess.run(['git','-C',current,'status','--short','--branch'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=20)
   repos.append({'path':current,'status':r.stdout.strip(),'error':r.stderr.strip() if r.returncode else ''});dirs[:]=[]
  else:dirs[:]=[d for d in dirs if d not in EXCLUDED and not pathlib.Path(current,d).is_symlink()]
 print(json.dumps(repos,indent=2))
def env_keys(path):
 p=pathlib.Path(path)
 if not p.exists():return set()
 return {m.group(1) for line in p.read_text(encoding='utf-8').splitlines() if (m:=re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=',line))}
def envdoctor(args):
 needed=env_keys(args.example);actual=env_keys(args.env)
 print(json.dumps({'missing_keys':sorted(needed-actual),'extra_keys':sorted(actual-needed),'present_keys':sorted(actual&needed),'values_shown':False},indent=2))
def notes(args):
 root=pathlib.Path.home()/'.dailyos';root.mkdir(exist_ok=True);file=root/'notes.json';rows=json.loads(file.read_text(encoding='utf-8')) if file.exists() else []
 if args.text:
  rows.append({'id':str(uuid.uuid4()),'text':args.text,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});temp=root/'notes.tmp';temp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(temp,file)
 print(json.dumps(rows,ensure_ascii=False,indent=2))
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while block:=f.read(1024*1024):h.update(block)
 return h.hexdigest()
def dedupe(args):
 root=pathlib.Path(args.path).resolve(strict=True)
 if not root.is_dir() or root==pathlib.Path(root.anchor) or root==pathlib.Path.home():raise ValueError('Pilih folder tugas yang spesifik, bukan root drive/home.')
 groups={};skipped=[]
 for current,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if d not in EXCLUDED and d!='.dailyos-trash' and not pathlib.Path(current,d).is_symlink())
  for name in sorted(files):
   p=pathlib.Path(current,name)
   if p.is_symlink():continue
   try:groups.setdefault((p.stat().st_size,digest(p)),[]).append(p)
   except OSError as e:skipped.append({'path':str(p),'error':str(e)})
 duplicates=[{'keep':str(v[0]),'duplicates':[str(p) for p in v[1:]]} for v in groups.values() if len(v)>1]
 report={'dry_run':not args.quarantine,'groups':duplicates,'skipped':skipped}
 if args.quarantine:
  batch=root/'.dailyos-trash'/str(uuid.uuid4());moves=[]
  for group in duplicates:
   for name in group['duplicates']:
    source=pathlib.Path(name).resolve(strict=True)
    if not source.is_relative_to(root):raise ValueError('Path keluar dari folder yang dipilih.')
    destination=batch/source.relative_to(root);destination.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(source),str(destination));moves.append({'from':str(source),'to':str(destination)})
  if moves:(batch/'restore.json').write_text(json.dumps(moves,indent=2),encoding='utf-8')
  report.update(quarantine=str(batch) if moves else None,moved=len(moves))
 print(json.dumps(report,indent=2))
def main():
 parser=argparse.ArgumentParser(description='DailyOS local productivity tools');commands=parser.add_subparsers(dest='command',required=True)
 p=commands.add_parser('context');p.add_argument('path');p.add_argument('--output');p.add_argument('--max-bytes',type=int,default=500000);p.add_argument('--file-bytes',type=int,default=100000);p.set_defaults(handler=context)
 p=commands.add_parser('cert');p.add_argument('host');p.add_argument('--port',type=int,default=443);p.add_argument('--warn-days',type=int,default=30);p.set_defaults(handler=certificate)
 p=commands.add_parser('repos');p.add_argument('path');p.set_defaults(handler=gittree)
 p=commands.add_parser('env');p.add_argument('example');p.add_argument('env');p.set_defaults(handler=envdoctor)
 p=commands.add_parser('notes');p.add_argument('text',nargs='?');p.set_defaults(handler=notes)
 p=commands.add_parser('dedupe');p.add_argument('path');p.add_argument('--quarantine',action='store_true',help='Pindahkan duplikat ke .dailyos-trash; tidak hapus permanen.');p.set_defaults(handler=dedupe)
 args=parser.parse_args()
 try:args.handler(args)
 except (ValueError,OSError,ssl.SSLError,subprocess.SubprocessError) as e:print(str(e),file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
