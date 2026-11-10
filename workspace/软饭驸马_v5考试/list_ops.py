# 列出父会话（新格式 messages.jsonl）里所有碰过旧临时目录 runtime-95ddeb44 的写操作和 shell 命令，带结果状态
import json, sys
from pathlib import Path

P = Path('/Users/kk/.kiro/sessions/9abebf782073b545/sess_f569f4b3-9778-4f81-ad15-b46bad4a299c/messages.jsonl')
OLD = 'runtime-95ddeb44'
calls, results = [], {}
for line in open(P, encoding='utf-8', errors='replace'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    pl = d.get('payload') or {}
    t = pl.get('type')
    if t == 'tool_call':
        calls.append((d.get('timestamp', ''), pl))
    elif t == 'tool_result':
        c = pl.get('content')
        results[pl.get('toolCallId')] = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)

seen = set()
for ts, pl in calls:
    cid = pl.get('toolCallId')
    if cid in seen:
        continue
    seen.add(cid)
    name = pl.get('toolName') or ''
    args = pl.get('args') or {}
    s = json.dumps(args, ensure_ascii=False)
    if OLD not in s and 'KIROCREW_SCRATCH' not in s:
        continue
    res = (results.get(cid) or '')
    ok = 'ERR' if ('rejected' in res or 'Error' in res[:200] or 'blocked' in res[:300].lower()) else 'ok'
    if name in ('fs_write', 'str_replace', 'fs_append', 'write'):
        what = (args.get('path') or '').split(OLD + '/')[-1]
        extra = f"{len(args.get('text') or args.get('newStr') or '')}ch"
    elif name in ('execute_bash', 'shell'):
        what = (args.get('command') or '').replace('\n', ' ⏎ ')[:170]
        extra = ''
    else:
        continue
    print(f'{ts[11:19]} {name:12s} {ok:3s} {extra:>7s} {what}')
