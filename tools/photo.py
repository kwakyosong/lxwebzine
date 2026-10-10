"""사진 정리 (Claude Code가 실행한다. 학생은 쓰지 않는다)

원본 한 장을 용도에 맞는 비율로 잘라 public/images/에 저장하고, credits.txt에 한 줄을 적는다.
- 원본보다 크게 늘리지 않는다
- 용도마다 최대 크기·용량(KB)을 넘지 않게 저장한다
- 휴대폰 사진의 회전 정보를 반영하고, 위치 정보(EXIF)는 지운다

사용 (Windows는 python3 대신 python):
  python3 tools/photo.py 원본 용도 주제 [이름중간] [--focus x,y] [--credit "직접 촬영(teamN)"]

  용도: hero-16x9 | hero-4x5 | og | 16x9 | 4x5 | 9x16 | thumb-16x9
  주제·이름중간: 영문 소문자·숫자·하이픈. 파일 이름 = 주제-이름중간-비율.jpg
                 (hero·og는 이름중간을 비운다 → 주제-hero-16x9.jpg, 주제-og.jpg)
  --focus x,y  : 남길 부분의 가운데 (0~1, 왼쪽 위가 0,0). 기본 0.5,0.5
  --credit     : 출처. 직접 찍은 사진은 "직접 촬영(teamN)", 아니면 "출처 | 라이선스 | 원본 주소"
예:
  python3 tools/photo.py 콘텐츠/새별오름/사진/IMG_0101.jpg 16x9 saebyeol-oreum --focus 0.5,0.7
"""
import argparse, os, re, sys
from io import BytesIO
try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('Pillow가 없다. 한 번만 설치한다: python -m pip install pillow  (Mac은 python3 -m pip install pillow)')
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')   # Windows에서도 한글 결과가 깨지지 않게

USES = {
    'hero-16x9': dict(r=(16, 9), max=1600, min=1200, kb=500, part='hero'),
    'hero-4x5': dict(r=(4, 5), max=1080, min=600, kb=500, part='hero'),
    'og': dict(r=(1200, 630), max=1200, min=1200, kb=300, part='og', exact=True),
    '16x9': dict(r=(16, 9), max=1600, min=500, kb=300),
    '4x5': dict(r=(4, 5), max=1080, min=300, kb=300),
    '9x16': dict(r=(9, 16), max=1080, min=720, kb=300),
    'thumb-16x9': dict(r=(16, 9), max=800, min=300, kb=150),
}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def name_for(use, topic, part):
    u = USES[use]
    if u.get('exact'):
        return f'{topic}-og.jpg'
    parts = [p for p in (topic, part or u.get('part', '')) if p]
    return '-'.join(parts) + '-' + ('x'.join(map(str, u['r']))) + '.jpg'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('use', choices=USES); ap.add_argument('topic'); ap.add_argument('part', nargs='?', default='')
    ap.add_argument('--focus', default='0.5,0.5'); ap.add_argument('--credit', default='직접 촬영')
    ap.add_argument('--out', default=os.path.join(ROOT, 'public', 'images'))
    a = ap.parse_args()
    u = USES[a.use]
    name = name_for(a.use, a.topic, a.part)
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*\.jpg', name):
        sys.exit(f'파일 이름 규칙과 다르다: {name} (영문 소문자·숫자·하이픈)')
    im = ImageOps.exif_transpose(Image.open(a.src)).convert('RGB')
    W, H = im.size
    R = u['r'][0] / u['r'][1]
    w, h = W, W / R
    if h > H: h, w = H, H * R
    fx, fy = (float(v) for v in a.focus.split(','))
    x = min(max(0, fx * W - w / 2), W - w); y = min(max(0, fy * H - h / 2), H - h)
    out_w = min(u['max'], int(w)); out_h = min(int(out_w * u['r'][1] / u['r'][0]), int(h))
    if u.get('exact') and w >= 1200: out_w, out_h = 1200, 630
    crop = im.crop((round(x), round(y), round(x + w), round(y + h))).resize((out_w, out_h), Image.LANCZOS)
    lo, hi, best = .5, .92, None
    room = (u['kb'] - 16) * 1024   # 옮기거나 올릴 때 붙는 정보(메타데이터)로 조금 커져도 한도를 넘지 않게 16KB를 남긴다
    for _ in range(7):
        q = (lo + hi) / 2; buf = BytesIO(); crop.save(buf, 'JPEG', quality=round(q * 100), optimize=True)
        if buf.tell() <= room: best, lo = buf.getvalue(), q
        else: hi = q
    if best is None:
        buf = BytesIO(); crop.save(buf, 'JPEG', quality=50, optimize=True); best = buf.getvalue()
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, name), 'wb').write(best)
    cr = [c.strip() for c in a.credit.split('|')]
    if '직접 촬영' in cr[0]: cr = [cr[0], '-', '-']
    cr += ['[라이선스]', '[원본 주소]'][len(cr) - 1:]
    line = f'{name} | ' + ' | '.join(cr[:3])
    cpath = os.path.join(a.out, 'credits.txt')
    lines = open(cpath, encoding='utf-8').read().splitlines() if os.path.exists(cpath) else ['파일 이름 | 출처 | 라이선스 | 원본 주소']
    lines = [l for l in lines if not l.startswith(name + ' |')] + [line]
    open(cpath, 'w', encoding='utf-8', newline='\n').write('\n'.join([lines[0]] + sorted(lines[1:])) + '\n')
    small = round(w) < u['min']
    box = f'남긴 부분 x{round(x)}~{round(x + w)}, y{round(y)}~{round(y + h)} (원본 {W}x{H})'
    print(f'{name}  {out_w}x{out_h}  {len(best) // 1024}KB  {box}' + (f'  ※ 원본이 작다(남길 부분 가로 {round(w)}px < 최소 {u["min"]}px). 늘리지 않고 저장했다' if small else ''))

if __name__ == '__main__':
    main()
