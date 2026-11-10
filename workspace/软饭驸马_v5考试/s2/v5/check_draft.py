# 用法：python3 check_draft.py [草稿目录，默认 s2/v5/draft]
# 1 字数和上限  2 写稿人读的文件里有没有考题场号、考题场人物  3 「」里的原句能不能在原材料里逐字找到  4 文件之间 14 字以上逐字重复
import re, sys
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/v5/draft')
P = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效')
B = Path('/Users/kk/Documents/AI 视频/00_漫剧通用底座')
BUDGET = {'00_怎么用.md': 1500, '10_内核.md': 8000, '11_切段命令词.md': 1200, '12_共创命令词.md': 4000, '13_A命令词.md': 6000,
          '15_出片反馈与集末.md': 1500, '14_D2命令词.md': 5000, '20_格式_06编译规则.md': 15000, '40_病历.md': 5000,
          '41_审核替换表.md': 2000, '软饭驸马_项目事实.md': 5000, '30_包_生活喜剧.md': 3500, '50_样板索引.md': 4000,
          '51_成片账本.md': 1000, '31_包_打斗.md': 3000, '32_包_奇观与系统特效.md': 3000, '33_包_大场面与群像.md': 3000}
NOT_FOR_WRITER = {'50_样板索引.md', '51_成片账本.md', '00_怎么用.md'}
EXAM = re.compile(r'EP\s*19|19-1(?!\d)|EP\s*17|17-1(?!\d)|EP\s*26|26-1(?!\d)|EP\s*38-38-2|38-2(?!\d)|EP\s*24-24-2|(?<!24-)24-2(?![\d-])|EP\s*13|13-2(?!\d)|EP\s*37|37-2(?!\d)'
                  r'|药库|太医院|演武场|二皇子书房|吞丹|浴池|公主府书房|刘承|张柬之|阿七|天赐良机|以毒攻毒|家庭核心地位')


def norm(s):
    return re.sub(r'[\s　，。、；：！？,.;:!?（）()【】\[\]…—\-·｜|*`"“”‘’\'「」『』]', '', s)


files = sorted(p for p in D.glob('*') if p.is_file() and not p.name.startswith('证据表'))
txt = {p.name: p.read_text(encoding='utf-8', errors='replace') for p in files}

print('== 1 字数')
for n, t in txt.items():
    b = BUDGET.get(n)
    flag = '' if b is None else ('✓' if len(t) <= b else f'✗ 超 {len(t) - b}')
    print(f'   {n:24} {len(t):6}  上限 {b or "-"} {flag}')
missing = [n for n in BUDGET if n not in txt]
print('   还没交：' + ('、'.join(missing) or '无'))

print('\n== 2 写稿人读的文件里的考题痕迹')
for n, t in txt.items():
    if n in NOT_FOR_WRITER or not n.endswith('.md'):
        continue
    hits = [t[max(0, m.start() - 14): m.end() + 14].replace('\n', ' ') for m in EXAM.finditer(t)]
    if hits:
        print(f'   {n}：{len(hits)} 处')
        for h in hits[:6]:
            print('      …' + h + '…')

print('\n== 3 示范原句核对')
corpus_files = list(P.glob('EP*.md')) + list(P.glob('*.md')) + [p for p in (P / '33_第一季复盘').rglob('*') if p.is_file() and p.suffix in ('.md', '.txt') and '打乱稿' not in p.parts and '评审' not in p.parts and '考卷' not in p.parts]
corpus_files += list((P / '32_工作流重构').glob('0*.md')) + list((P / '32_工作流重构' / 'v3.7').glob('*.md')) + [p for p in B.rglob('*.md')]
corpus = norm(''.join(p.read_text(encoding='utf-8', errors='replace') for p in set(corpus_files)))
for n, t in txt.items():
    if not n.endswith('.md'):
        continue
    qs = re.findall(r'「([^」]{8,})」', t)
    bad = []
    for q in qs:
        for seg in re.split(r'……|…|\.\.\.', q):
            s = norm(seg)
            if len(s) >= 6 and s not in corpus:
                bad.append(seg[:40])
    print(f'   {n}：引号 {len(qs)} 处，找不到原文 {len(bad)} 段' + ('：' + '｜'.join(bad[:5]) if bad else ''))

print('\n== 4 跨文件逐字重复（14 字以上）')
where = {}
for n, t in txt.items():
    if not n.endswith('.md'):
        continue
    for s in re.split(r'[。；\n]', t):
        s2 = norm(s)
        if len(s2) >= 14:
            where.setdefault(s2, set()).add(n)
dup = [(s, v) for s, v in where.items() if len(v) >= 2]
print(f'   {len(dup)} 句')
for s, v in dup[:12]:
    print('   ', '/'.join(sorted(v)), s[:50])
