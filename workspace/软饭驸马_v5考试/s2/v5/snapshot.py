# 改 R02 之前，把考试用的 R01 草稿整份存底（已存在就不覆盖）
import shutil
from pathlib import Path

D = Path(__file__).resolve().parent
src, dst = D / 'draft', D / 'R01_考试版'
if dst.exists():
    print('EXISTS, not overwritten:', dst)
else:
    shutil.copytree(src, dst)
    print('saved', sum(1 for p in dst.rglob('*') if p.is_file()), 'files ->', dst)
