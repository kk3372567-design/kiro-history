# 查答案表里的关键短语有没有出现在考生要读的提示词里（v5 与 v3.7 各查一遍，两边都有就算打平）
import os, re
from pathlib import Path

S = Path(os.environ['KIROCREW_SCRATCH']) / 's2'
V5 = S / 'v5/draft'
V5_FILES = ['10_内核.md', '12_共创命令词.md', '13_A命令词.md', '30_包_生活喜剧.md', '31_包_打斗.md',
            '32_包_奇观与系统特效.md', '33_包_大场面与群像.md', '40_病历.md', '软饭驸马_项目事实.md']
V37 = S / 'exam2/prompts/丁'
norm = lambda s: re.sub(r'[\s"“”\'‘’「」（）()，,。、；;：:！!？?—\-]', '', s)
v5 = {f: norm((V5 / f).read_text(encoding='utf-8')) for f in V5_FILES}
v37 = {p.name: norm(p.read_text(encoding='utf-8')) for p in V37.iterdir()}
for key in sorted((S / 'exam2/keys').glob('考试_*.md')):
    t = key.read_text(encoding='utf-8')
    body = t.split('判卷清单')[-1] if '判卷清单' in t else t
    phrases = set()
    for m in re.findall(r'[「"“]([^」"”]{4,30})[」"”]', t):
        phrases.add(m)
    for m in re.findall(r'\*\*([^*]{4,24})\*\*', body):
        phrases.add(m)
    hits = []
    for ph in sorted(phrases):
        n = norm(ph)
        if len(n) < 4:
            continue
        a = [f for f, x in v5.items() if n in x]
        b = [f for f, x in v37.items() if n in x]
        if a or b:
            hits.append((ph, a, b))
    print(f'== {key.name}')
    for ph, a, b in hits:
        print(f'   「{ph}」 v5:{a or "-"}  v3.7:{b or "-"}')
for f, x in v5.items():
    for w in ['不出现台阶', '台阶门楼', '石栏', '马车、落叶', '涂脸', '门纸', '倒影', '铜镜', '你来我回', '传导', '五颗光点', '卫星', '罗盘']:
        if norm(w) in x:
            print(f'   [词] {f}: {w}')
