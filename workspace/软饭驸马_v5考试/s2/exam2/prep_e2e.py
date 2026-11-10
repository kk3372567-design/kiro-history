# 用法：python3 prep_e2e.py 1 2；R04 起：python3 prep_e2e.py 1@v5d 2@v5d（判卷目录 judge/E2Ed_<套>，位置另轮换）
# 每套三份：v3.7 链终稿、v5 链终稿、用户认可过成片的真终稿；只取代码块正文，统一加一行标题，P/Q/R 位置每套轮换
# 答案写 ../../private/判卷_e2e答案.tsv；同时生成判卷任务 briefs/任务/判卷_E2E_<套>.md
import re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
PRIV = E.parent.parent / 'private'
REAL = PRIV / 'E2E_真终稿_38-2D_GEN-D.md'
ORDERS = {1: ['丁', 'v5b', '真'], 2: ['真', '丁', 'v5b']}
ORDERS_NEW = {1: ['v5', '真', '丁'], 2: ['丁', 'v5', '真']}     # 新版重跑时换位置，v5 换成该版
TELL = re.compile(r'v3\.\d|\bv5[bcd]?\b|R0\d|丁|本场用到|内核\s*§|病历\s*M\d|技能包|21_检查|04a_|06最终|A稿-R')


def body(p):
    t = p.read_text(encoding='utf-8')
    blocks = re.findall(r'^```[^\n]*\n(.*?)^```', t, flags=re.M | re.S)
    if not blocks:
        sys.exit(f'!! 没找到代码块：{p}')
    b = max(blocks, key=len)
    b = re.sub(r'(空间图)\s*-?R0\d', r'\1', b)       # 考生稿写"空间图 R03"，真终稿没写版本号，去掉免得成了认稿记号
    return '# GEN-D｜10 秒｜终稿\n\n```\n' + b.rstrip('\n') + '\n```\n'


rows = []
for arg in sys.argv[1:]:
    s, _, ver = arg.partition('@')
    s = int(s)
    tag = 'E2E' + ({'v5d': 'd'}.get(ver, '') if ver else '')
    order = [ver if v == 'v5' else v for v in ORDERS_NEW[s]] if ver else ORDERS[s]
    d = E / 'judge' / f'{tag}_{s}'
    d.mkdir(parents=True, exist_ok=True)
    for L, v in zip('PQR', order):
        src = REAL if v == '真' else E / 'out' / f'E2E_{v}_{s}.md'
        t = body(src)
        (d / f'{L}.md').write_text(t, encoding='utf-8')
        rows.append(f'{tag}\t{s}\t{L}\t{v}\t{src.name}\t{len(t)}')
        for m in TELL.finditer(t):
            print(f'   残留 {tag}_{s}/{L}：…{t[max(0, m.start() - 15): m.end() + 15]}…'.replace('\n', '⏎'))
    (E / 'briefs' / '任务' / f'判卷_{tag}_{s}.md').write_text(f'''先完整读 `{E}/briefs/盲评三方_e2e.md`，照它做。

题：EP38 38-2 二皇子书房 GEN-D（10 秒，「天赐良机」那一段）的三份终稿。
- 三份终稿：`{d}/P.md`、`Q.md`、`R.md`
- 输入目录：`{E}/A/A4/输入/`（剧本与场景、已确认的共创稿、GEN 划分；资产索引很长，只看李玄和书房那几张卡）
- 输出文件：`{E}/judged/{tag}_{s}.md`

回报一行：排名、选哪份。
''', encoding='utf-8')
    print('done', tag, s, order)
key = PRIV / '判卷_e2e答案.tsv'
old = key.read_text(encoding='utf-8').splitlines() if key.exists() else ['题\t组\t字母\t真身\t原文件\t字数']
done = {(r.split('\t')[0], r.split('\t')[1]) for r in rows}
keep = [r for r in old if (r.split('\t')[0], r.split('\t')[1] if '\t' in r else '') not in done]
key.write_text('\n'.join(keep + rows) + '\n', encoding='utf-8')
