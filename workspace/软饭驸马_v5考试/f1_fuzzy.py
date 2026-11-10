# 对 v3.7 06 里没被逐字保留的句子，在 v5 20_格式 里找最接近的一句，判断是"改写"还是"删除"
import re, os, difflib
from pathlib import Path

V37 = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效/32_工作流重构/v3.7/06_生成视频_v3.7.md')
NEW = Path(os.environ['KIROCREW_SCRATCH']) / 's2/v5/draft/20_格式_06编译规则.md'
DEAD = ['05.5', '5.5', '增强', '保留锁', '三态', 'DIRECT_TO_06', 'NEED_USER_CONFIRMATION', 'BLOCKED', 'compile_receipt',
        'witness', 'emotion_lookup', '迁移配置', '武器卡', '结构化接力', '替换块', '替换清单', '版本标识', 'receipt', '槽位',
        'viewing_path_contract', 'NONE_WITH_REASON', 'DROP_EXPLICIT', 'source_', 'selected_', 'compiled_', 'prompt_span', 'blocked_fields']

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
a, b = V37.read_text(encoding='utf-8'), NEW.read_text(encoding='utf-8')
nb = norm(b)
bs = sents(b)
nbs = [norm(x) for x in bs]
lost = [s for s in sents(a) if norm(s) not in nb]
rows = {'改写': [], '删除·含死路由': [], '删除·不含死路由（要看）': []}
for s in lost:
    ns = norm(s)
    best, score = '', 0.0
    for x, nx in zip(bs, nbs):
        r = difflib.SequenceMatcher(None, ns, nx, autojunk=False).ratio()
        if r > score:
            best, score = x, r
    if score >= 0.55:
        rows['改写'].append((s, best, score))
    elif any(k in s for k in DEAD):
        rows['删除·含死路由'].append((s, best, score))
    else:
        rows['删除·不含死路由（要看）'].append((s, best, score))
for k, v in rows.items():
    print(f'===== {k}：{len(v)} 句')
    for s, best, sc in v:
        if k == '改写':
            print(f'  ({sc:.2f}) 原：{s[:110]}\n         新：{best[:110]}')
        elif k.startswith('删除·不含'):
            print(f'  原：{s[:160]}')
        else:
            print(f'  原：{s[:90]}')
