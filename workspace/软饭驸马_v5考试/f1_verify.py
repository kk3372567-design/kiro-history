# 核对 F1 重建的格式层：v3.7 原句逐字保留了多少，没保留的逐句列出，供人工判断是不是只删了死路由
import re, os
from pathlib import Path

V37 = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效/32_工作流重构/v3.7')
D = Path(os.environ['KIROCREW_SCRATCH']) / 's2/v5/draft'
PAIRS = [('D2', V37 / 'D2命令词_三段式原位装配_v3.7.md', D / '14_D2命令词.md'),
         ('06', V37 / '06_生成视频_v3.7.md', D / '20_格式_06编译规则.md')]
DEAD = ['05.5', '增强锁', '保留锁', '三态', 'DIRECT_TO_06', 'NEED_USER_CONFIRMATION', 'BLOCKED',
        'compile_receipt', 'witness', 'emotion_lookup', '迁移配置', '武器卡', '结构化接力', 'S 锁', 'S锁']

def sents(t):
    out = []
    for line in t.splitlines():
        line = line.strip()
        if not line:
            continue
        for s in re.split(r'(?<=[。！？；])', line):
            s = s.strip()
            if len(re.sub(r'\W', '', s)) >= 6:
                out.append(s)
    return out

norm = lambda s: re.sub(r'\s+', '', s)
for tag, src, new in PAIRS:
    a, b = src.read_text(encoding='utf-8'), new.read_text(encoding='utf-8')
    nb = norm(b)
    ss = sents(a)
    keep = [s for s in ss if norm(s) in nb]
    lost = [s for s in ss if norm(s) not in nb]
    print(f'===== {tag}: v3.7 {len(a)} 字 -> v5 {len(b)} 字；v3.7 句子 {len(ss)}，逐字保留 {len(keep)}（{len(keep)*100//max(1,len(ss))}%），未逐字保留 {len(lost)}')
    left = [k for k in DEAD if k in b]
    print('   v5 里残留的死路由词：', left or '无')
    for s in lost:
        dead = [k for k in DEAD if k in s] + (['05'] if re.search(r'(?<![0-9.])05(?![0-9.])', s) else [])
        print(f'   [{"死路由:" + "/".join(dead) if dead else "无死路由词"}] {s[:150]}')
