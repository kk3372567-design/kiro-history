# 把考完的 v5（R05 写法＋R06 检查脚本）装到 /Users/kk/Documents/AI 视频/01_漫剧工作流_v5/，并把考试材料归档进项目包
# 只新建，不覆盖：任何一个目标已存在就停下，什么都不写
import filecmp, shutil, sys
from pathlib import Path

DRAFT = Path('/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试/s2/v5/draft')
EXAM = Path('/Users/kk/.kiro/crew/workspace/软饭驸马_v5考试')
DST = Path('/Users/kk/Documents/AI 视频/01_漫剧工作流_v5')
P = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效')
FACTS = P / '34_v5重构' / '软饭驸马_项目事实.md'
ARCHIVE = P / '33_第一季复盘' / '11-01回放考试' / 'v5考试'

WORKFLOW = ['00_怎么用.md', '10_内核.md', '11_切段命令词.md', '12_共创命令词.md', '13_A命令词.md',
            '14_D2命令词.md', '15_出片反馈与集末.md', '20_格式_06编译规则.md', '21_检查脚本.py',
            '30_包_生活喜剧.md', '31_包_打斗.md', '32_包_奇观与系统特效.md', '33_包_大场面与群像.md',
            '40_病历.md', '41_审核替换表.md', '50_样板索引.md', '51_成片账本.md']
EVIDENCE = sorted(p.name for p in DRAFT.glob('证据表_*.md')) + ['审稿记录_R1.md'] + \
           sorted(p.name for p in DRAFT.glob('改动单_R0*.md'))

for t in (DST, FACTS, ARCHIVE):
    if t.exists():
        sys.exit(f'!! 已存在，停下不写：{t}')
for f in WORKFLOW + EVIDENCE + ['软饭驸马_项目事实.md']:
    if not (DRAFT / f).exists():
        sys.exit(f'!! 草稿里缺：{f}')

(DST / '证据').mkdir(parents=True)
for f in WORKFLOW:
    shutil.copy2(DRAFT / f, DST / f)
for f in EVIDENCE:
    shutil.copy2(DRAFT / f, DST / '证据' / f)
shutil.copy2(DRAFT / '软饭驸马_项目事实.md', FACTS)
shutil.copytree(EXAM, ARCHIVE, symlinks=True)

bad = [f for f in WORKFLOW if not filecmp.cmp(DRAFT / f, DST / f, shallow=False)]
bad += [f for f in EVIDENCE if not filecmp.cmp(DRAFT / f, DST / '证据' / f, shallow=False)]
bad += [] if filecmp.cmp(DRAFT / '软饭驸马_项目事实.md', FACTS, shallow=False) else ['软饭驸马_项目事实.md']
n_arch = sum(1 for p in ARCHIVE.rglob('*') if p.is_file())
n_src = sum(1 for p in EXAM.rglob('*') if p.is_file())
print('工作流', len(WORKFLOW), '份 ->', DST)
print('证据', len(EVIDENCE), '份 ->', DST / '证据', EVIDENCE)
print('项目事实 ->', FACTS)
print('考试归档', n_arch, '/', n_src, '个文件 ->', ARCHIVE)
print('和草稿逐字不同的：', bad or '无')
