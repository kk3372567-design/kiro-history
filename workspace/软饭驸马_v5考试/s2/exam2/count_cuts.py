# 数每份考卷逐镜细稿那个 GEN 有几个 CUT、平均每镜几秒（只看逐镜细稿那一节里的时间段）
import re
from pathlib import Path

E = Path(__file__).resolve().parent
SEC = {'A1': 15, 'A2': 14, 'A3': 13, 'A4': 10, 'A5': 14}
TIME = re.compile(r'(\d{1,2}\.\d)\s*[–—\-~～]{1,2}\s*(\d{1,2}\.\d)\s*(?:s|秒)?')
for p in sorted((E / 'out').glob('A*_*.md')):
    q = p.stem.split('_')[0]
    t = p.read_text(encoding='utf-8')
    m = re.search(r'^#{1,4}[^\n]*逐镜[^\n]*$', t, flags=re.M)
    body = t[m.start():] if m else ''
    spans = []
    for line in body.splitlines():
        if not re.search(r'CUT|^\s*\**\s*[A-E]\d?[-－]?\d|^\|\s*[A-E]\d?-?\d|^#{3,4}', line):
            continue
        for a, b in TIME.findall(line[:80]):
            a, b = float(a), float(b)
            if 0 <= a < b <= SEC[q] + 0.01 and (a, b) not in spans:
                spans.append((a, b))
    spans.sort()
    # 只保留首尾相接的那一串（去掉文中零散引用的时间）
    chain, end = [], 0.0
    for a, b in spans:
        if abs(a - end) < 0.05:
            chain.append((a, b)); end = b
    n = len(chain)
    ok = abs(end - SEC[q]) < 0.05
    avg = f'{SEC[q] / n:.1f}' if n else '-'
    print(f'{p.stem:10s} 逐镜 {n} 个 CUT，接到 {end:.1f}/{SEC[q]} 秒{"" if ok else "（没接满，需人工看）"}，平均每镜 {avg} 秒')
