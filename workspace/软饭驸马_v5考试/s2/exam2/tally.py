# 汇总判卷：读 judged/<题>_<组>.md 的"合计"和"重犯数"两行，用 private/判卷_v5答案.tsv 换成真身，打印每套和每题的分数
# 用法：python3 tally.py            （全部）
#       python3 tally.py A2b A5b    （只看这几题）
import re, sys
from collections import defaultdict
from pathlib import Path

E = Path(__file__).resolve().parent
KEY = E.parent.parent / 'private' / '判卷_v5答案.tsv'

who = {}
for line in KEY.read_text(encoding='utf-8').splitlines()[1:]:
    q, s, L, v = line.split('\t')[:4]
    who[(q, s, L)] = v

only = set(sys.argv[1:])
per_q = defaultdict(lambda: defaultdict(int))
picks = defaultdict(int)
for p in sorted((E / 'judged').glob('*_*.md')):
    q, s = p.stem.rsplit('_', 1)
    if only and q not in only:
        continue
    t = p.read_text(encoding='utf-8')
    nums = []
    for line in t.splitlines():                     # 合计行有三种写法："X = 28/35"、"X = 4+…= 29/35"、表格"| 合计 | 32/35 | 30/35 |"
        if '合计' in line:
            nums = re.findall(r'(\d+)\s*[/／]\s*35', line)
            if len(nums) >= 2:
                break
    if len(nums) < 2 and '合计' in t:               # 第四种：「### 合计」下面两行各写一个
        nums = re.findall(r'(\d+)\s*[/／]\s*35', t[t.rfind('合计'):][:400])
    if len(nums) < 2:
        print(f'{p.stem:8s} 没找到合计行，需人工看')
        continue
    sc = {'X': int(nums[0]), 'Y': int(nums[1])}
    rp = re.search(r'重犯数[^\n]*', t)
    pick = re.search(r'选\s*\**\s*([XY])', t[t.find('第三部分'):] if '第三部分' in t else t)
    vx, vy = who.get((q, s, 'X'), '?'), who.get((q, s, 'Y'), '?')
    for L, v in (('X', vx), ('Y', vy)):
        per_q[q][v] += sc[L]
    pv = who.get((q, s, pick.group(1)), '?') if pick else '?'
    picks[pv] += 1
    print(f'{p.stem:8s} X={vx}:{sc["X"]}  Y={vy}:{sc["Y"]}  选 {pick.group(1) if pick else "?"}（{pv}）')
    if rp:
        print(f'         {rp.group(0)[:120]}')
print('—— 每题合计')
for q, d in per_q.items():
    print(f'{q:5s} ' + '  '.join(f'{v}={n}' for v, n in sorted(d.items())))
print('—— 选中次数', dict(picks))
