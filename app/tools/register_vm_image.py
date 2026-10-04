#!/usr/bin/env python3
"""Explicit local registration of the exact reviewed image; no arbitrary VM import."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.vm_preview.image_bundle import register_local_image
p=argparse.ArgumentParser();p.add_argument('image',type=Path);p.add_argument('--vm-home',type=Path,required=True);a=p.parse_args()
print(register_local_image(a.image,a.vm_home))
