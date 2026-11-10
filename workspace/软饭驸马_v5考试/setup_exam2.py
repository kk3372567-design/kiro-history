# 冻结两套考生提示词（v3.7＝丁、v5），写新版考生须知
import os, shutil
from pathlib import Path

S = Path(os.environ['KIROCREW_SCRATCH']) / 's2'
E = S / 'exam2'
# 1. v3.7 冻结副本里 05 真源路径改指新位置（只改路径这一行）
a = E / 'prompts/丁/A命令词.md'
t = a.read_text(encoding='utf-8')
old = '/Users/kk/.kiro/crew/scratch/runtime-b5c66c5f/s2/exam/prompts/丁/05_设计镜头.md'
if old in t:
    a.write_text(t.replace(old, str(E / 'prompts/丁/05_设计镜头.md')), encoding='utf-8')
# 2. v5 冻结副本：写稿人要读的文件
V = E / 'prompts/v5'; V.mkdir(parents=True, exist_ok=True)
for f in ['10_内核.md', '12_共创命令词.md', '13_A命令词.md', '14_D2命令词.md', '20_格式_06编译规则.md',
          '21_检查脚本.py', '30_包_生活喜剧.md', '31_包_打斗.md', '32_包_奇观与系统特效.md',
          '33_包_大场面与群像.md', '40_病历.md', '41_审核替换表.md', '软饭驸马_项目事实.md']:
    shutil.copy2(S / 'v5/draft' / f, V / f)
# 3. 考生须知
(E / '考生须知.md').write_text(f'''# 考生须知

你是一个全新的写稿员，没看过这个项目的任何历史。只依据任务里点名的提示词目录和输入目录干活。

下文 `S2` 指 `{S}`。

## 严禁（违反则这次作废）

- 不读、不 grep、不列目录：`S2` 下除了任务点名的提示词目录、输入目录以外的任何东西。特别是 `S2/v5/`、`S2/ref/`、`S2/exam2/keys/`、`S2/exam2/out/` 里别人的稿子、`S2/exam2/judge*/`、`S2/exam2/prompts/` 下没点名给你的那套提示词。
- 不读 `/Users/kk/Documents/AI 视频/` 和 `/Users/kk/Desktop/` 下的任何文件。唯一例外：提示词要求运行的检查脚本可以运行，不用读它的源码。
- 不查会话记录、记忆库、规则库。

## 怎么做

1. 先完整读提示词目录里的命令词，再完整读命令词要求读的其他文件。它们都在同一个提示词目录里；命令词里写的路径或文件名，一律改读这个目录里的同名文件。
2. 再完整读输入目录里的文件。资产索引很长，只取本场用到的人物、场景、道具那几张卡。输入里有 `GEN划分.md` 的，GEN 划分已定，照它切，不改。
3. 按提示词干活。提示词里说"等用户确认后再继续"的地方，视为用户已经确认，接着往下写，不要停。提示词要你问用户的问题，写在文件末尾"待问用户"一节，不要停下来等。
4. 全部写进任务指定的输出文件（write 工具，目录会自动建）。只交这一份文件。
5. 回报一行：输出路径、`wc -m` 字数、大约用了多久。
''', encoding='utf-8')
for p in sorted(list(V.iterdir()) + [a, E / '考生须知.md']):
    print(f'{len(p.read_text(encoding="utf-8")):7d}  {p.relative_to(S)}')
print('05 path now:', [l for l in a.read_text(encoding='utf-8').splitlines() if '05 真源路径' in l])
