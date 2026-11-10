# 交回的考卷逐份核对：字数、逐镜写没写指定 GEN、GEN 划分秒数是否照固定表、v5 稿首有没有"本场用到"
import os, re, sys
from pathlib import Path

S = Path(os.environ['KIROCREW_SCRATCH']) / 's2/exam2'
TARGET = {'A1': 'GEN-D', 'A2': 'GEN-E', 'A3': 'GEN-C2', 'A4': 'GEN-D', 'A5': 'GEN-B'}

def fixed_secs(q):
    t = (S / 'A' / q / '输入/GEN划分.md').read_text(encoding='utf-8')
    return dict(re.findall(r'\|\s*(GEN-[A-Z0-9]+)\s*\|\s*(\d+)\s*秒', t))

for p in sorted((S / 'out').glob('*.md')):
    t = p.read_text(encoding='utf-8')
    name = p.stem
    q = name.split('_')[0]
    row = [f'{name:14s}', f'{len(t):6d}字']
    if q in TARGET:
        fs = fixed_secs(q)
        found = {g: s for g, s in re.findall(r'(GEN-[A-Z0-9]+)[^\n|｜]{0,6}[｜|]\s*(\d+)\s*秒', t)}
        bad = [f'{g}:{found[g]}≠{s}' for g, s in fs.items() if g in found and found[g] != s]
        miss = [g for g in fs if g not in t]
        extra = sorted(set(re.findall(r'GEN-[A-Z]\d?\b', t)) - set(fs))
        tg = TARGET[q]
        cuts = len(re.findall(rf'{tg}-\d+|{tg[4:]}-0?\d+\s*[｜|]', t))
        row += [f'秒数不符{bad or "无"}', f'缺{miss or "无"}', f'多{extra or "无"}', f'{tg}镜号行≈{cuts}']
        if '_v5_' in name:
            row.append('本场用到✓' if '本场用到' in t[:1500] else '本场用到✗')
    print('  '.join(row))
