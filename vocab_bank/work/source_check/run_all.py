#!/usr/bin/env python3
"""run_all.py - re-check the bank against every source PDF.

  python3 work/source_check/run_all.py

Needs `pdftotext` (poppler). The Netzwerk neu A1/A2/B1 glossaries are scanned images; their OCR text is
stored in work/source_check/ocr/*.json (made once with run_ocr.py, needs rapidocr_onnxruntime + pdftoppm).
Prints, for every source, how many entries could not be found in the bank. Those leftovers must be read
by a human: they are page headers, OCR noise, Swiss/Austrian variants or words deliberately skipped.
Result files go to $SOURCE_CHECK_DIR (default: a temp folder), not into the repo.
"""
import subprocess, sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, TXT
PDF = ROOT / 'source_lists' / 'pdf'
for f in PDF.glob('*.pdf'):
    base = Path(TXT) / f.stem
    if not base.with_suffix('.txt').exists():
        subprocess.run(['pdftotext', '-layout', str(f), str(base.with_suffix('.txt'))], check=True)
    if f.name.startswith(('A1_SD1', 'Goethe')):
        subprocess.run(['pdftotext', '-bbox', str(f), str(Path(TXT) / (f.stem + '.bbox.html'))], check=True)
for script in ('goethe_cov.py', 'goethe_cov2.py', 'nw_cov.py', 'klett_cov.py'):
    print('=====', script)
    subprocess.run([sys.executable, str(HERE / script)], cwd=HERE)
subprocess.run([sys.executable, str(ROOT / 'vocab_bank' / 'work' / 'klettsrc.py'), 'status'], cwd=ROOT / 'vocab_bank')
