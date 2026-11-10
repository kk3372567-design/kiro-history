# 核对 GEN 划分：引号里的台词能否在输入原文找到（按省略号拆段），有没有导演词
import os, re
from pathlib import Path

S = Path(os.environ['KIROCREW_SCRATCH']) / 's2/exam2/A'
BAD = ['机位', '俯拍', '仰拍', '横移', '景别', '特写', '近景', '中景', '全景', '远景', '画左', '画右', '镜头', '虚化',
       '环绕', '推轨', '拉轨', '越肩', '慢动作', '水晶柱', 'SYS', '前景', '后景', '深焦', '贴地', '梁上', '低位', '高位', '光束里']
norm = lambda s: re.sub(r'[\s"“”\'‘’「」]', '', s)
for q in ['A1', 'A2', 'A3', 'A4', 'A5']:
    d = S / q / '输入'
    g = (d / 'GEN划分.md').read_text(encoding='utf-8')
    src = ''.join(p.read_text(encoding='utf-8') for p in d.iterdir() if p.name not in ('GEN划分.md',) and '资产索引' not in p.name)
    ns = norm(src)
    miss = []
    for m in re.findall(r'「(.+?)」', g):
        for frag in re.split(r'……|\.\.\.\.\.\.|…', m):
            f = norm(frag)
            if len(f) >= 2 and f not in ns:
                miss.append(frag)
    bad = [b for b in BAD if b in g]
    print(f'{q}: 找不到的台词片段 {len(miss)}', miss[:12])
    print(f'    导演词：{bad or "无"}')
