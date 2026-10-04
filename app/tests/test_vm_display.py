"""Display defaults and exact old/new process-policy compatibility, no real VM."""
import json,unittest,uuid
from learning_lab.vm_preview.files import Refused
from learning_lab.vm_preview.policy import (BACKEND,GTK_LEGACY,GTK_READABLE,VGA_READABLE,
    image_spec,launch_arguments,verify_arguments)

class DisplayPolicyTests(unittest.TestCase):
 def setUp(self):
  self.run=str(uuid.uuid4());self.socket='/run/user/1000/private/qmp'
  self.args=launch_arguments(7,8,9,self.run,self.socket)
 def verify(self,args):verify_arguments(args,self.run,self.socket)
 def legacy(self):
  args=self.args.copy();args[args.index('-device')+1]='VGA';args[args.index('-display')+1]=GTK_LEGACY
  return args
 def test_default_readable_aspect_preserving_fit(self):
  self.assertEqual(self.args[self.args.index('-display')+1],GTK_READABLE)
  self.assertEqual(self.args[self.args.index('-device')+1],VGA_READABLE)
  self.verify(self.args)
 def test_old_running_console_remains_recognizable(self):self.verify(self.legacy())
 def test_headless_policy_unchanged(self):
  a=launch_arguments(7,8,9,self.run,self.socket,display='none');self.verify(a)
  self.assertEqual(a[a.index('-display')+1],'none');self.assertEqual(a[a.index('-device')+1],'VGA')
 def test_mixed_old_new_forms_refused(self):
  for key,value in (('-device','VGA'),('-display',GTK_LEGACY)):
   a=self.args.copy();a[a.index(key)+1]=value
   with self.assertRaises(Refused):self.verify(a)
 def test_no_arbitrary_display_or_device_options(self):
  for key,value in (('-display',GTK_READABLE+',full-screen=on'),('-display',GTK_READABLE.replace('clipboard=off','clipboard=on')),('-display',GTK_READABLE.replace('keep-aspect-ratio=on','keep-aspect-ratio=off')),('-device','VGA,xres=1024,yres=768'),('-device','virtio-vga'),('-display','sdl')):
   a=self.args.copy();a[a.index(key)+1]=value
   with self.assertRaises(Refused):self.verify(a)
 def test_both_forms_keep_exact_isolation_and_graph(self):
  for a in (self.args,self.legacy()):
   for flag in ('-nodefaults','-no-user-config'):self.assertIn(flag,a)
   for key,value in (('-nic','none'),('-serial','none'),('-monitor','none'),('-qmp','unix:'+self.socket+',server=on,wait=off')):self.assertEqual(a[a.index(key)+1],value)
   nodes=[json.loads(a[i+1])for i,v in enumerate(a)if v=='-blockdev']
   self.assertEqual([n.get('filename')for n in nodes if 'filename'in n],['/dev/fdset/1','/dev/fdset/2'])
   self.assertEqual(nodes[-1]['backing'],'base');self.assertTrue(nodes[1]['read-only'])
   for appended in (['-netdev','user,id=n'],['-fsdev','local,id=s,path=/home,security_model=none'],['-monitor','stdio']):
    with self.assertRaises(Refused):self.verify(a+appended)
 def test_legacy_does_not_relax_process_identity(self):
  for a in (self.args,self.legacy()):
   for key,value in (('-uuid',str(uuid.uuid4())),('-qmp','unix:/tmp/foreign,server=on,wait=off'),('-add-fd','fd=7,set=2')):
    changed=a.copy();changed[changed.index(key)+1]=value
    with self.assertRaises(Refused):self.verify(changed)
 def test_image_and_backend_pins_unchanged(self):
  self.assertEqual(BACKEND,'offline-qemu-preview-1')
  self.assertEqual(image_spec()['sha256'],'a9bd127cc641ecf877896d86eea74e7e528d584158f0b12374c136cd3ea46d3d')
 def test_source_environment_not_modified(self):
  # No GTK scaling override is necessary: fit fixes the constrained minimum.
  import os
  from unittest.mock import patch
  with patch.dict(os.environ,{'GDK_SCALE':'2','GDK_DPI_SCALE':'1.25'}):
   before=dict(os.environ);self.verify(launch_arguments(7,8,9,self.run,self.socket));self.assertEqual(dict(os.environ),before)

if __name__=='__main__':unittest.main()
