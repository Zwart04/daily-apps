import json
from repository_safety import ROOT,RETIRE,guard,gh,api
def pages(path):
 rows=[];page=1
 while True:
  part=api(path+'&page='+str(page));rows.extend(part)
  if len(part)<100:return rows
  page+=1
folder=ROOT/'.recovery/github-metadata';folder.mkdir(exist_ok=True)
for name in RETIRE:
 meta=guard(name);base='repos/Zwart04/'+name
 issues=pages(base+'/issues?state=all&per_page=100')
 pulls=pages(base+'/pulls?state=all&per_page=100')
 comments=pages(base+'/issues/comments?per_page=100')
 reviews=pages(base+'/pulls/comments?per_page=100')
 (folder/(name+'.json')).write_text(json.dumps({'repository':meta,'issues':issues,'pulls':pulls,'comments':comments,'review_comments':reviews},indent=2))
 print('METADATA_SAVED',name,'issues',len(issues),'pulls',len(pulls),flush=True)
