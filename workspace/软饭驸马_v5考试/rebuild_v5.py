# 从子代理会话存档重放写文件操作，重建旧临时目录 runtime-b5c66c5f/s2 下的 v5 草稿
import json, os, shutil, sys
from pathlib import Path

ARCH = Path('/Users/kk/.kiro/sessions/cli')
OLD = '/Users/kk/.kiro/crew/scratch/runtime-b5c66c5f/'
NEW = os.environ['KIROCREW_SCRATCH'].rstrip('/') + '/'

SESS = [  # (标签, 会话 id, 只重放这些路径片段)
    ('PARENT', 'ce732f84-e90c-4511-97e6-b4c82870cea6', ['s2/v5/briefs/', 's2/v5/check_draft.py']),
    ('W1', '97c8a8fc-ba47-4115-9583-c00579e85b72', None),
    ('W2', '09675a00-0d42-4211-a4c2-073c670b53b9', None),
    ('W3', 'd66c19a7-b746-4777-9b13-b9fbc8d10ef9', None),
    ('W4', 'faf8bd4a-a075-4f4f-9514-6e66a79a7cf4', None),
    ('W5', '186bb0e0-294b-48fc-b586-e032712abdd8', None),
    ('G1', 'dcad6680-7535-4e5b-83c6-289848e19142', None),
    ('F1', 'a2dcfe51-8ab9-43b2-8e85-fbe73dc7acd0', None),
    ('R1', 'f0731ac0-3b2e-4bdd-923c-483b4696db53', None),
]

def events(sid):
    uses, order, res = {}, [], {}
    for line in open(ARCH / f'{sid}.jsonl', encoding='utf-8'):
        d = json.loads(line)
        data = d.get('data')
        if not isinstance(data, dict):
            continue
        for c in data.get('content', []):
            if c.get('kind') == 'toolUse':
                t = c['data']; uses[t['toolUseId']] = t; order.append(t['toolUseId'])
            elif c.get('kind') == 'toolResult':
                r = c['data']; res[r['toolUseId']] = r
    for u in order:
        t = uses[u]
        if t.get('name') == 'write':
            yield t['input'], res.get(u, {})

log = []
for tag, sid, only in SESS:
    if tag == 'F1':  # F1 第一步：cp -n 把 W2 版本备份进 备份/
        d = Path(NEW + 's2/v5/draft'); (d / '备份').mkdir(parents=True, exist_ok=True)
        for src, dst in [('14_D2命令词.md', '14_D2命令词_W2版.md'), ('20_格式_06编译规则.md', '20_格式_06编译规则_W2版.md')]:
            if not (d / '备份' / dst).exists():
                shutil.copy2(d / src, d / '备份' / dst)
        log.append(('F1', 'cp-backup', '备份/'))
    for inp, r in events(sid):
        p = inp.get('path', '')
        if OLD not in p:
            continue
        if only and not any(o in p for o in only):
            continue
        if r.get('status') != 'success':
            log.append((tag, 'SKIP-failed', p.replace(OLD, ''))); continue
        q = Path(p.replace(OLD, NEW)); cmd = inp.get('command')
        q.parent.mkdir(parents=True, exist_ok=True)
        if cmd == 'create':
            q.write_text(inp.get('content', ''), encoding='utf-8')
        elif cmd == 'strReplace':
            t = q.read_text(encoding='utf-8'); o, n = inp['oldStr'], inp.get('newStr', '')
            k = t.count(o)
            if k == 0:
                sys.exit(f'!! {tag} 替换原句找不到：{q}\n{o[:200]}')
            q.write_text(t.replace(o, n) if inp.get('replaceAll') else t.replace(o, n, 1), encoding='utf-8')
        elif cmd == 'append':
            with open(q, 'a', encoding='utf-8') as f:
                f.write(inp.get('content', ''))
        else:
            sys.exit(f'!! 未知 command {cmd} in {tag}')
        log.append((tag, cmd, p.replace(OLD, '')))

for x in log:
    print(*x, sep=' | ')
print('ops:', len(log))
