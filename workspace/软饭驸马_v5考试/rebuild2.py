# 把丢失的临时目录 runtime-95ddeb44 重建到当前临时目录：
# 1) 07:46:46 那步（当时用 cli 存档重放 W1–W5／F1／R1）的结果，改从项目包备份 02_草稿_重建备份_1101 取（W1–W5 的 cli 存档已被清理）；G1 的考试 GEN 划分仍从它的 cli 存档重放
# 2) 之后按原顺序重放父会话里所有写文件操作和会改文件的 shell 步骤
# 3) 重放 7 个已完成写稿子代理写进 exam2/out/ 的内容
import json, os, re, shutil, subprocess, sys
from pathlib import Path

SES = Path('/Users/kk/.kiro/sessions')
PARENT = SES / '9abebf782073b545/sess_f569f4b3-9778-4f81-ad15-b46bad4a299c/messages.jsonl'
G1 = SES / 'cli/dcad6680-7535-4e5b-83c6-289848e19142.jsonl'
BACKUP = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效/34_v5重构/02_草稿_重建备份_1101')
OLD = '/Users/kk/.kiro/crew/scratch/runtime-95ddeb44'
OLDER = '/Users/kk/.kiro/crew/scratch/runtime-b5c66c5f'
NEW = os.environ['KIROCREW_SCRATCH'].rstrip('/')
MUTATING_SHELLS = ['07:59:39', '11:28:49', '11:32:57', '12:08:55', '12:09:07', '12:09:52', '12:13:16']
OK_PREFIX = ('Created', 'Appended', 'Replaced', 'Successfully')
mp = lambda s: s.replace(OLD, NEW) if isinstance(s, str) else s

def load(p):
    first, last, res, order = {}, {}, {}, []
    for line in open(p, encoding='utf-8', errors='replace'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        pl = d.get('payload') or {}
        t = pl.get('type')
        if t == 'tool_call':
            cid = pl.get('toolCallId')
            if cid not in first:
                first[cid] = d.get('timestamp', ''); order.append(cid)
            args = dict((last.get(cid) or {}).get('args') or {}); args.update(pl.get('args') or {})
            last[cid] = dict(pl, args=args)
        elif t == 'tool_result':
            c = pl.get('content')
            res[pl.get('toolCallId')] = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
    return [(first[c], last[c], res.get(c, '')) for c in order]

def apply_write(name, a, tag, log):
    p = Path(mp(a.get('path', '')))
    p.parent.mkdir(parents=True, exist_ok=True)
    if name == 'fs_write':
        p.write_text(mp(a.get('text', '')), encoding='utf-8')
    elif name == 'fs_append':
        old = p.read_text(encoding='utf-8') if p.exists() else ''
        if old and not old.endswith('\n'):
            old += '\n'
        p.write_text(old + mp(a.get('text', '')), encoding='utf-8')
    elif name == 'str_replace':
        t = p.read_text(encoding='utf-8')
        o = mp(a.get('oldStr', '')); n = mp(a.get('newStr', ''))
        if t.count(o) == 0:
            sys.exit(f'!! {tag} 替换原句找不到：{p}\n{o[:200]}')
        p.write_text(t.replace(o, n) if a.get('replace_all') else t.replace(o, n, 1), encoding='utf-8')
    log.append(f'{tag} {name:11s} {str(p).replace(NEW + "/", "")}')

def restore_backup(log):
    v5 = Path(NEW) / 's2/v5'
    for f in BACKUP.rglob('*'):
        if not f.is_file():
            continue
        rel = f.relative_to(BACKUP)
        if rel.name in ('盘点说明.md', 'v5写作说明.md') and len(rel.parts) == 1:
            dst = v5 / 'briefs' / rel.name
        elif rel.name == 'check_draft.py' and len(rel.parts) == 1:
            dst = v5 / 'check_draft.py'
        else:
            dst = v5 / 'draft' / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(f.read_text(encoding='utf-8').replace(OLDER, NEW), encoding='utf-8')
    log.append(f'BACKUP restored {sum(1 for _ in BACKUP.rglob("*") if _.is_file())} files')
    for line in open(G1, encoding='utf-8'):                       # G1 旧格式存档：只重放 exam2 下的写操作
        d = json.loads(line); data = d.get('data')
        if d.get('kind') != 'AssistantMessage' or not isinstance(data, dict):
            continue
        for c in data.get('content', []):
            if c.get('kind') == 'toolUse' and c['data'].get('name') == 'write':
                inp = c['data'].get('input') or {}
                if inp.get('command') == 'create' and OLDER + '/s2/exam2/' in inp.get('path', ''):
                    q = Path(inp['path'].replace(OLDER, NEW)); q.parent.mkdir(parents=True, exist_ok=True)
                    q.write_text(inp.get('content', ''), encoding='utf-8')
                    log.append(f'G1     create      {str(q).replace(NEW + "/", "")}')

if (Path(NEW) / 's2').exists():
    shutil.rmtree(Path(NEW) / 's2')                                 # 只清当前会话自己的临时重建结果
log = []
env = dict(os.environ, KIROCREW_SCRATCH=NEW)
restored = False
for ts, pl, r in load(PARENT):
    hhmmss = ts[11:19]
    if ts[:10] != '2026-11-01' or hhmmss < '07:46:00':
        continue
    if not restored and hhmmss >= '07:46:46':
        restore_backup(log); restored = True
    name, a = pl.get('toolName'), pl.get('args') or {}
    s = json.dumps(a, ensure_ascii=False)
    if OLD not in s and 'KIROCREW_SCRATCH' not in s:
        continue
    if name in ('fs_write', 'fs_append', 'str_replace'):
        if r.startswith(OK_PREFIX):
            apply_write(name, a, 'PARENT', log)
    elif name == 'execute_bash' and hhmmss in MUTATING_SHELLS:
        cmd = mp(a.get('command', ''))
        out = subprocess.run(['/bin/zsh', '-c', cmd], env=env, capture_output=True, text=True)
        log.append(f'PARENT shell {hhmmss} exit={out.returncode} {(out.stderr or "").strip()[:120]}')
DONE = {'A1_丁_1', 'A1_丁_2', 'A1_v5_1', 'A1_v5_2', 'A2_丁_1', 'A2_丁_2', 'A3_丁_1'}
for mj in sorted(SES.glob('*/sess_*/messages.jsonl')):
    if mj == PARENT:
        continue
    raw = mj.read_text(encoding='utf-8', errors='replace')
    if OLD + '/s2/exam2/out/' not in raw:
        continue
    for ts, pl, r in load(mj):
        name, a = pl.get('toolName'), pl.get('args') or {}
        path = a.get('path', '') or ''
        if name in ('fs_write', 'fs_append', 'str_replace') and '/s2/exam2/out/' in path:
            if Path(path).stem in DONE and r.startswith(OK_PREFIX):
                apply_write(name, a, mj.parent.name[5:13], log)
        elif name == 'execute_bash' and '/s2/exam2/out/' in (a.get('command') or '') and re.search(r'>|\btee\b|\bcp |\bmv |sed -i', a.get('command') or ''):
            log.append(f'!! 写稿人用 shell 改过 out：{mj.parent.name} {(a.get("command") or "")[:140]}')
print('\n'.join(log))
print('ops', len(log))
