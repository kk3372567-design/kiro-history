# 把草稿里写稿人要读的 13 份冻结成考试用的 prompts/<新版>（已存在就不覆盖），并列出和上一版冻结稿不同的文件
# 用法：python3 freeze.py v5c v5b
import filecmp, shutil, sys
from pathlib import Path

E = Path(__file__).resolve().parent
D = E.parent / 'v5' / 'draft'
FILES = ['10_内核.md', '12_共创命令词.md', '13_A命令词.md', '14_D2命令词.md', '20_格式_06编译规则.md',
         '21_检查脚本.py', '30_包_生活喜剧.md', '31_包_打斗.md', '32_包_奇观与系统特效.md',
         '33_包_大场面与群像.md', '40_病历.md', '41_审核替换表.md', '软饭驸马_项目事实.md']
new, old = sys.argv[1], sys.argv[2]
dst = E / 'prompts' / new
if dst.exists():
    print('EXISTS, not overwritten:', dst)
else:
    dst.mkdir(parents=True)
    for f in FILES:
        shutil.copy2(D / f, dst / f)
for f in FILES:
    if not filecmp.cmp(E / 'prompts' / old / f, dst / f, shallow=False):
        print(f'changed vs {old}:', f, len((dst / f).read_text(encoding="utf-8")), '字')
