"""Exact console acknowledgements for static developer guest fixtures only.
No guest agent, host share, application import or arbitrary lesson execution.
Calibrate from an OCR-located PASSED line, then require exact whole-row pixels.
The pinned preview uses its verified 800x600 framebuffer and 8x16 console font.
"""
from PySide6.QtGui import QImage

ALPHABET='PASED'

def vi_ready(text):
 """Pinned Vim Tiny uses its long English file-status form, not '3L'."""
 import re
 return re.search(r'(?m)^"note[.]txt"\s+[1-9][0-9]* lines?, [1-9][0-9]* bytes\s*$',text) is not None

def nano_ready(text,filename):
 """Exact title and static fixture filename from the isolated header row."""
 import re
 return re.fullmatch(r'GNUnano[0-9]+(?:[.][0-9]+)+'+re.escape(filename),''.join(text.split())) is not None

def pixels(image):
 if isinstance(image,str):image=QImage(image)
 if image.isNull() or image.width()!=800 or image.height()!=600:raise ValueError('Unsupported console framebuffer')
 return [bytes(1 if image.pixelColor(x,y).red()+image.pixelColor(x,y).green()+image.pixelColor(x,y).blue()>0 else 0 for x in range(800)) for y in range(600)]

def calibrate(image,top):
 rows=pixels(image);y=(int(top)//16)*16
 if not 0<=y<=584:raise ValueError('Invalid calibration row')
 glyphs={}
 for index,char in enumerate('PASSED'):
  glyph=tuple(row[index*8:(index+1)*8] for row in rows[y:y+16])
  if not any(any(row) for row in glyph):raise ValueError('Empty calibration glyph')
  if char in glyphs and glyphs[char]!=glyph:raise ValueError('Inconsistent calibration glyph')
  glyphs[char]=glyph
 if len(set(glyphs.values()))!=5:raise ValueError('Ambiguous calibration')
 if not matches(image,'PASSED',glyphs):raise ValueError('Calibration is not a complete console line')
 return glyphs

def matches(image,text,glyphs):
 if not text or len(text)>100 or any(c not in glyphs for c in text):raise ValueError('Unsupported acknowledgement')
 pattern=[b''.join(glyphs[c][y] for c in text)+bytes(800-len(text)*8) for y in range(16)]
 rows=pixels(image)
 return any(rows[y:y+16]==pattern for y in range(0,585,16))

def marker(sequence):
 if not 0<=sequence<5**6:raise ValueError('Acknowledgement limit exceeded')
 return 'PASSED'+''.join(ALPHABET[(sequence//5**i)%5] for i in range(5,-1,-1))

def locate_calibration(image,tsv):
 import csv,io
 for row in csv.DictReader(io.StringIO(tsv),delimiter='\t'):
  if row.get('text')=='PASSED' and int(row['left'])<8:
   try:return calibrate(image,int(row['top']))
   except ValueError:continue
 raise ValueError('Exact PASSED calibration line is not visible')
