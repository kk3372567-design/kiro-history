# 从项目包归档把考试材料复制进新临时目录（不覆盖已有文件）
import os, shutil
from pathlib import Path

S = Path(os.environ['KIROCREW_SCRATCH']) / 's2'
B = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效/33_第一季复盘')
X = B / '11-01回放考试'
I = X / '题目输入'

def copy_dir(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.iterdir()):
        if f.is_file() and not (dst / f.name).exists():
            shutil.copy2(f, dst / f.name)

def copy_file(src, dst_dir):
    dst_dir.mkdir(parents=True, exist_ok=True)
    if not (dst_dir / src.name).exists():
        shutil.copy2(src, dst_dir / src.name)

for q in ['A1', 'A2', 'A3']:
    copy_dir(I / 'A' / q / '输入', S / 'exam2/A' / q / '输入')
copy_dir(I / 'A/A4不退步/输入', S / 'exam2/A/A4/输入')
copy_dir(X / 'v3.7考试/输入_A5/输入', S / 'exam2/A/A5/输入')
for q in ['共创1', '共创2']:
    copy_dir(I / '共创' / q / '输入', S / 'exam2/共创' / q / '输入')
for g in ['24-2B', '38-1H', '38-2D']:
    copy_dir(I / 'D2不退步' / g / '输入', S / 'exam2/D2' / g / '输入')
    copy_file(I / 'D2不退步/04_资产索引_当前可调用.md', S / 'exam2/D2' / g / '输入')
copy_dir(X / 'v3.7考试/冻结提示词/v3.7_丁', S / 'exam2/prompts/丁')
for k in ['A_A1', 'A_A2', 'A_A3', 'A_A4不退步', '共创_共创1', '共创_共创2']:
    copy_file(X / '答案' / f'考试_{k}.md', S / 'exam2/keys')
copy_file(X / 'v3.7考试/答案/考试_A_A5.md', S / 'exam2/keys')
copy_file(B / '04_你说过想要和不要的.md', S / 'ref/judge_ref')
copy_file(Path('/Users/kk/Documents/AI 视频/00_漫剧通用底座/01_视频模型病历.md'), S / 'ref/judge_ref')

for p in sorted(list((S / 'exam2').rglob('*')) + list((S / 'ref').rglob('*'))):
    if p.is_file():
        print(f'{len(p.read_text(encoding="utf-8")):7d}  {p.relative_to(S)}')
