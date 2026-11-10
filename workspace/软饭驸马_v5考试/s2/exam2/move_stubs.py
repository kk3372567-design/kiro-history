# 把中断留下的残稿挪到 _失败残稿/，免得补派的子代理以为是自己写了一半的稿
# 用法：python3 move_stubs.py out/A4_丁_2.md out/共创1_丁_1.md ...（同名已存在时加序号，不覆盖）
import shutil, sys
from pathlib import Path

E = Path(__file__).resolve().parent
bad = E / '_失败残稿'
bad.mkdir(exist_ok=True)
for p in sys.argv[1:]:
    q = E / p
    if not q.exists():
        print('skip (not found)', p)
        continue
    dst = bad / p.replace('/', '__')
    n = 2
    while dst.exists():
        dst = bad / (p.replace('/', '__').replace('.md', f'_{n}.md'))
        n += 1
    shutil.move(str(q), str(dst))
    print('moved', p, '->', dst.name, len(dst.read_text(encoding='utf-8')), '字')
