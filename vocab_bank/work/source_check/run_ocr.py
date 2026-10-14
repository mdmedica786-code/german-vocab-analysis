import sys, json, subprocess, os
from rapidocr_onnxruntime import RapidOCR
eng = RapidOCR()
name, pdf, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
out = {}
for p in range(first, last + 1):
    png = f'{os.path.dirname(os.path.abspath(__file__))}/ocr/_tmp_{name}_{p}'
    subprocess.run(['pdftoppm', '-r', '150', '-f', str(p), '-l', str(p), '-png', '-singlefile', pdf, png], check=True)
    res, _ = eng(png + '.png')
    boxes = []
    for b, t, c in (res or []):
        xs = [pt[0] for pt in b]; ys = [pt[1] for pt in b]
        boxes.append([min(xs), min(ys), max(xs), max(ys), t, float(c)])
    out[p] = boxes
    os.remove(png + '.png')
    json.dump(out, open(f'{os.path.dirname(os.path.abspath(__file__))}/ocr/{name}.json', 'w'), ensure_ascii=False)
    print(name, p, len(boxes), flush=True)
