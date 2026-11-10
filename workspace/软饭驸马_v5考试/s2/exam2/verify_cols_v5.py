# 用法：python3 verify_cols_v5.py A1_1 A1_2 ...（E2E_1 这类三方题自动按 P/Q/R 三列核）
# 读 judged/<题_组>.md 里每个表格列引的原句，只算"只在一份稿子里出现"的引文，看它实际出自 X 还是 Y；列和出处对不上就报"疑似串列"
# 另外数一数：引文两份都找不到的有几条（可能是评审改写或编造）
import re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
Q = re.compile(r'[「"“『]([^」"”』]{4,200})[」"”』]')


def norm(s):
    return re.sub(r'[\s　，。、；：！？,.;:!?（）()【】\[\]…—\-·｜|*`＋+／/~～]', '', s)


def check(q):
    d = E / 'judge' / q
    LS = 'PQR' if q.startswith('E2E') else 'XY'
    files = {L: norm((d / f'{L}.md').read_text(encoding='utf-8')) for L in LS}
    p = E / 'judged' / f'{q}.md'
    if not p.exists():
        print(f'== {q}  还没交')
        return
    hits = {a: {b: 0 for b in LS} for a in LS}
    both = {a: 0 for a in LS}
    none = {a: [] for a in LS}
    header = None
    for line in p.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) or c == '' for c in cells):
            continue
        if header is None:
            header = cells
            continue
        for h, c in zip(header, cells):
            m = re.match(r'^\**([' + LS + r'])', h.replace(' ', ''))
            if not m:
                continue
            col = m.group(1)
            for qt in Q.findall(c):
                for seg in re.split(r'……|…|\.\.\.|⋯', qt):
                    s = norm(seg)
                    if len(s) < 6:
                        continue
                    found = [L for L, body in files.items() if s in body]
                    if len(found) == 1:
                        hits[col][found[0]] += 1
                    elif len(found) >= 2:
                        both[col] += 1
                    else:
                        none[col].append(seg[:40])
    bad = [f'{a}列→{b}' for a in LS for b in LS if a != b and hits[a][b] > hits[a][a]]
    cols = '；'.join(f"{a}列：出自{a} {hits[a][a]}／出自别份 {sum(hits[a][b] for b in LS if b != a)}／多份都有 {both[a]}／都找不到 {len(none[a])}" for a in LS)
    print(f"== {q}  {cols}；疑似串列：{'、'.join(bad) or '无'}")
    for col in LS:
        for s in none[col][:6]:
            print(f'     {col}列找不到：「{s}」')


for a in sys.argv[1:]:
    check(a)
