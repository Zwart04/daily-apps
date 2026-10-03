import unittest,tempfile,pathlib,argparse,importlib.util,contextlib,io,json
spec=importlib.util.spec_from_file_location('daily',pathlib.Path(__file__).parents[1]/'cli/daily.py');daily=importlib.util.module_from_spec(spec);spec.loader.exec_module(daily)
class Tests(unittest.TestCase):
 def output(self,fn,args):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):fn(args)
  return out.getvalue()
 def test_context_omits_environment_and_binary(self):
  with tempfile.TemporaryDirectory() as folder:
   r=pathlib.Path(folder);(r/'code.txt').write_text('real input');(r/'.env').write_text('private=value');(r/'image.bin').write_bytes(b'\0\1')
   result=self.output(daily.context,argparse.Namespace(path=folder,max_bytes=1000,file_bytes=1000,output=None));self.assertIn('real input',result);self.assertNotIn('private=value',result)
 def test_env_only_reports_names(self):
  with tempfile.TemporaryDirectory() as folder:
   r=pathlib.Path(folder);(r/'sample').write_text('API_KEY=\nPORT=\n');(r/'actual').write_text('PORT=9876\n')
   result=self.output(daily.envdoctor,argparse.Namespace(example=str(r/'sample'),env=str(r/'actual')));self.assertNotIn('9876',result);self.assertEqual(json.loads(result)['missing_keys'],['API_KEY'])
 def test_dedupe_defaults_to_read_only_and_quarantine_preserves_bytes(self):
  with tempfile.TemporaryDirectory() as folder:
   r=pathlib.Path(folder);(r/'a.txt').write_text('duplicate content');(r/'b.txt').write_text('duplicate content');(r/'c.txt').write_text('distinct')
   args=argparse.Namespace(path=folder,quarantine=False);report=json.loads(self.output(daily.dedupe,args));self.assertTrue(report['dry_run']);self.assertTrue((r/'b.txt').exists())
   args.quarantine=True;report=json.loads(self.output(daily.dedupe,args));self.assertEqual(report['moved'],1);batch=pathlib.Path(report['quarantine']);self.assertEqual((batch/'b.txt').read_text(),'duplicate content');self.assertTrue((r/'a.txt').exists());self.assertTrue((r/'c.txt').exists())
if __name__=='__main__':unittest.main()
