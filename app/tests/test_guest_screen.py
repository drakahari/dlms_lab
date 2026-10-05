"""Reject stale markers and command echoes instead of accepting fuzzy OCR."""
import unittest
from PySide6.QtGui import QImage,QColor
from guest_screen import calibrate,matches,marker,ALPHABET,vi_ready,nano_ready

class ScreenMarkerTests(unittest.TestCase):
 def test_nano_header_requires_exact_title_and_filename(self):
  self.assertTrue(nano_ready('GNU nano 8.4 guarded .sh\n','guarded.sh'))
  self.assertFalse(nano_ready('GHU nano 8.4 guarded.sh','guarded.sh'))
  self.assertFalse(nano_ready('GNU nano 8.4 other.sh','guarded.sh'))
  self.assertFalse(nano_ready('learner@lab:~$ nano guarded.sh','guarded.sh'))
 def test_real_vi_status_requires_exact_file_and_counts(self):
  self.assertTrue(vi_ready('Alpha\nBeta\nGamma\n"note.txt" 3 lines, 17 bytes\n'))
  self.assertFalse(vi_ready('learner@lab:~$ vi note.txt'))
  self.assertFalse(vi_ready('"other.txt" 3 lines, 17 bytes'))
  self.assertFalse(vi_ready('"note.txt" Permission denied'))
 def image(self,text,extra=False):
  image=QImage(800,600,QImage.Format_RGB32);image.fill(QColor('black'))
  for col,char in enumerate(text):
   for y in range(2,14):
    for x in range(1,7):
     if (x+y+ALPHABET.index(char))%6==0:image.setPixelColor(col*8+x,32+y,QColor('white'))
  if extra:image.setPixelColor(720,35,QColor('white'))
  return image
 def test_exact_unique_marker_rejects_stale_line(self):
  font=calibrate(self.image('PASSED'),34)
  self.assertTrue(matches(self.image(marker(18)),marker(18),font))
  self.assertFalse(matches(self.image(marker(17)),marker(18),font))
 def test_command_echo_with_other_pixels_is_not_completion(self):
  font=calibrate(self.image('PASSED'),34)
  self.assertFalse(matches(self.image(marker(18),True),marker(18),font))
 def test_bad_calibration_and_counter_refused(self):
  with self.assertRaises(ValueError):calibrate(self.image('PASSED',True),34)
  with self.assertRaises(ValueError):marker(5**6)
