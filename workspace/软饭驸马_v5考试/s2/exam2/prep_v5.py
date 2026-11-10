# 用法：python3 prep_v5.py A1 A2 ...
# 每题两套：第一套用两版各自的第 1 份，第二套用第 2 份并且把 X/Y 位置对调；去掉版本痕迹；答案写 keys/判卷_v5答案.tsv
import random, re, sys
from pathlib import Path

E = Path(__file__).resolve().parent
PACK = r'(?:生活喜剧|打斗|奇观与系统特效|大场面与群像)(?:（3[0-3]）)?包'

def clean(t, q=''):
    lines = t.split('\n')
    if lines and lines[0].startswith('# ') and '｜' in lines[0]:                # 标题统一，去掉 R01／05／版本这类痕迹
        lines[0] = lines[0].split('｜')[0] + ('｜导演共创稿' if q.startswith('共创') else '｜A 稿')
    if q.startswith('共创') and lines and lines[0].startswith('# '):      # 共创稿标题统一成"…导演共创稿"，括号里的副标题／版本号都去掉
        lines[0] = re.sub(r'场?[\s｜]*(导演共创稿).*$', r' \1', lines[0])
        lines[0] = re.sub(r'^#\s*共创\d[^：:\n]*[：:]\s*', '# ', lines[0])   # 去掉考卷编号前缀"共创2 v5c："
    if not q.startswith('共创') and lines and lines[0].startswith('# '):    # A 稿标题统一成"…｜A 稿"（有的用"·"、有的带"（v5d_2）"）
        lines[0] = re.sub(r'\s*[·｜|]?\s*A ?稿.*$', '｜A 稿', lines[0])
    t = '\n'.join(lines)
    t = re.sub(r'（(?:v5[bcde]?|丁)(?:_\d)?）', '', t)                     # 标题或正文里的"（v5d_2）"
    t = re.sub(r'^.*读取清单.*\n?', '', t, flags=re.M)                       # "读取清单：10_内核、13_A命令词……"整行
    t = re.sub(r'（05\s*导演深化[^）]*）|05\s*导演深化', '导演深化', t)
    t = re.sub(r'(?<![0-9.])05\s*(?:第[一二三四五六七八九十]+节|§\s*[0-9.]+)', '', t)
    t = re.sub(r'^.*本场用到.*\n?', '', t, flags=re.M)                       # v5 稿首"本场用到：××包"整行
    t = re.sub(r'^.*(?:真源|命令词)[：:].*\n?', '', t, flags=re.M)            # 稿首"真源：……／命令词：……"说明行
    t = re.sub(r'（[^（）\n]*(?:内核|病历|' + PACK + r'|技能包|3[0-3]_包|05_设计镜头|05 真源|A命令词|命令词)[^（）\n]*）', '', t)
    t = re.sub(r'\((?:[^()\n]*)(?:内核|病历|技能包|05_设计镜头|A命令词)[^()\n]*\)', '', t)
    t = re.sub(r'照?(?:10_)?内核\s*§\s*[0-9.]+(?:\s*[、/／]\s*§?\s*[0-9.]+)*', '', t)
    t = re.sub(r'照?(?:40_)?病历\s*M[0-9W]+(?:\s*[、/／]\s*M?[0-9W]+)*', '', t)
    t = re.sub(r'`?(?:1[0-5]|2[01]|3[0-3]|4[01])_[^\s`，。；）)]+\.(?:md|py)`?', '', t)
    t = re.sub(PACK + r'|技能包', '', t)
    t = re.sub(r'-?\s?v3\.\d+|\bv5[bcde]?(?:\.\d)?\b|（[甲乙丙丁]\d?）', '', t)
    t = re.sub(r'_(?:丁|v5[bcde]?)_\d\.md', '.md', t)
    t = re.sub(r'prompts/(?:丁|v5[bcde]?)/', 'prompts/', t)
    return t

TELL = re.compile(r'本场用到|内核\s*§|病历\s*M\d|技能包|v3\.\d|\bv5[bcde]?\b|_丁_|05_设计镜头|13_A|10_内核|(?<![0-9.])05\s*(?:导演|真源|第|§)|' + PACK)

def run(q, only=None, ver='v5'):
    # ver='v5b'／'v5c'／'v5d' 是 R02／R03／R04 重考：对手仍是同一题同一组的 v3.7 稿，X/Y 位置和 R01 那次相同；判卷目录和答案行用 q+'b'
    tag = q + {'v5b': 'b', 'v5c': 'c', 'v5d': 'd', 'v5e': 'e'}.get(ver, '')
    vs = ['丁', 'v5']
    random.Random(f'20261101-v5-{q}').shuffle(vs)
    vs = [ver if v == 'v5' else v for v in vs]
    rows = []
    done = set()
    for setno, order in [(1, vs), (2, vs[::-1])]:
        if only and setno not in only:
            continue
        done.add(str(setno))
        d = E / 'judge' / f'{tag}_{setno}'
        d.mkdir(parents=True, exist_ok=True)
        for L, v in zip('XY', order):
            src = E / 'out' / f'{q}_{v}_{setno}.md'
            t = clean(src.read_text(encoding='utf-8'), q)
            (d / f'{L}.md').write_text(t, encoding='utf-8')
            rows.append(f'{tag}\t{setno}\t{L}\t{v}\t{src.name}\t{len(t)}')
            for m in TELL.finditer(t):
                print(f'   残留 {tag}_{setno}/{L}：…{t[max(0, m.start() - 15): m.end() + 15]}…'.replace('\n', '⏎'))
        print('done', tag, setno, order)
    key = E.parent.parent / 'private' / '判卷_v5答案.tsv'
    key.parent.mkdir(parents=True, exist_ok=True)
    old = key.read_text(encoding='utf-8').splitlines() if key.exists() else ['题\t组\t字母\t真身\t原文件\t字数']
    keep = [r for r in old if not (r.startswith(tag + '\t') and r.split('\t')[1] in done)]
    key.write_text('\n'.join(keep + rows) + '\n', encoding='utf-8')

if __name__ == '__main__':
    # 用法：A4 打乱两套；A4:1 只打乱第 1 套；A2:1,2@v5b 用 R02 稿重考（判卷目录 judge/A2b_1）
    for a in sys.argv[1:]:
        a, _, ver = a.partition('@')
        q, _, s = a.partition(':')
        run(q, {int(x) for x in s.split(',')} if s else None, ver or 'v5')
