# 汇总 E2E 三方判卷：读 judged/E2E*_<套>[b].md 的"合计（只加前六项）"和"第一/第二/第三"，用 private/判卷_e2e答案.tsv 换成真身
# 用法：python3 tally_e2e.py           （全部）
#       python3 tally_e2e.py E2Ed       （只看这一题）
import re, sys
from collections import defaultdict
from pathlib import Path

E = Path(__file__).resolve().parent
KEY = E.parent.parent / 'private' / '判卷_e2e答案.tsv'
who = {}
for line in KEY.read_text(encoding='utf-8').splitlines()[1:]:
    q, s, L, v = line.split('\t')[:4]
    who[(q, s, L)] = v

only = set(sys.argv[1:])
tot = defaultdict(lambda: defaultdict(int))
rank = defaultdict(lambda: defaultdict(list))
for p in sorted((E / 'judged').glob('E2E*_*.md')):
    q, s = p.stem.rsplit('_', 1)
    s = s.rstrip('b')                                   # 二判和一判同一套稿子
    if only and q not in only:
        continue
    t = p.read_text(encoding='utf-8')
    sc = {}
    for L in 'PQR':
        m = re.search(L + r'\s*[＝=][^/\n]*?\**\s*(\d+)\s*/\s*30', t)   # "P = 22/30" 或 "P = 4+4+…= **23/30**"
        if m:
            sc[L] = int(m.group(1))
    m = re.search(r'第一[：:]\s*\**\s*([PQR]).*?第二[：:]\s*\**\s*([PQR]).*?第三[：:]\s*\**\s*([PQR])', t, flags=re.S)
    order = list(m.groups()) if m else []
    names = {L: who.get((q, s, L), '?') for L in 'PQR'}
    line = '  '.join(f'{L}={names[L]}:{sc.get(L, "?")}' for L in 'PQR')
    print(f'{p.stem:9s} {line}  排名 {" > ".join(names[L] for L in order) if order else "?"}')
    for L in 'PQR':
        if L in sc:
            tot[q][names[L]] += sc[L]
    for i, L in enumerate(order):
        rank[q][names[L]].append(i + 1)
print('—— 每题合计（/30 加总）与名次')
for q in tot:
    print(f'{q:5s} ' + '  '.join(f'{v}={n}（名次 {",".join(map(str, rank[q][v]))}）' for v, n in sorted(tot[q].items())))
