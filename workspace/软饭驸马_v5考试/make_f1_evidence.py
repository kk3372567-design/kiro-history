# 生成 证据表_F1.md：v3.7 06 → v5 20_格式 每一句的去向（逐字保留／改写／删除），外加父会话补回的句子
import re, os, difflib
from pathlib import Path

V37 = Path('/Users/kk/Documents/AI 视频/软饭驸马_完整跨对话制作资料/00_项目生产包_当前有效/32_工作流重构/v3.7')
D = Path(os.environ['KIROCREW_SCRATCH']) / 's2/v5/draft'
DEAD = ['05.5', '5.5', '增强', '保留锁', '三态', 'DIRECT_TO_06', 'NEED_USER_CONFIRMATION', 'BLOCKED', 'compile_receipt',
        'witness', 'emotion_lookup', '迁移配置', '武器卡', '结构化接力', '替换块', '替换清单', '版本标识', 'receipt', '槽位',
        'viewing_path_contract', 'NONE_WITH_REASON', 'DROP_EXPLICIT', 'source_', 'selected_', 'compiled_', 'prompt_span',
        'blocked_fields', 'REFERENCE_ONLY', '注册', '索引', '回执', 'MUST', 'abstract_to_concrete', 'input_uncertainty', '卡名']

def sents(t):
    out = []
    for line in t.splitlines():
        line = line.strip()
        if not line:
            continue
        for s in re.split(r'(?<=[。！？；])', line):
            s = s.strip()
            if len(re.sub(r'\W', '', s)) >= 6:
                out.append(s)
    return out

norm = lambda s: re.sub(r'\s+', '', s)
out = ['# 证据表_F1（格式层重建记录，不给写稿的人读）', '',
       '来源：v3.7 `06_生成视频_v3.7.md`、`D2命令词_三段式原位装配_v3.7.md`。F1 照原文搬，删已经不用的老路由（05.5／S 锁／增强锁／保留锁／三态交接／结构化接力／回执与 witness／武器卡等），把"05"改称"A 稿"，做方案列明的五处修改。F1 写完两份后撞上用量上限，这份表由父会话用脚本按句比对生成；F1 多删的活规则已由父会话补回（见第四节）。', '']
for tag, src, new in [('D2 命令词', V37 / 'D2命令词_三段式原位装配_v3.7.md', D / '14_D2命令词.md'),
                      ('06 编译规则', V37 / '06_生成视频_v3.7.md', D / '20_格式_06编译规则.md')]:
    a, b = src.read_text(encoding='utf-8'), new.read_text(encoding='utf-8')
    nb = norm(b); bs = sents(b); nbs = [norm(x) for x in bs]
    ss = sents(a); keep = [s for s in ss if norm(s) in nb]; lost = [s for s in ss if norm(s) not in nb]
    rew, dead, other = [], [], []
    for s in lost:
        ns = norm(s); best, sc = '', 0.0
        for x, nx in zip(bs, nbs):
            r = difflib.SequenceMatcher(None, ns, nx, autojunk=False).ratio()
            if r > sc:
                best, sc = x, r
        if sc >= 0.55:
            rew.append((s, best))
        elif any(k in s for k in DEAD) or re.search(r'(?<![0-9.])05(?![0-9.])', s):
            dead.append(s)
        else:
            other.append(s)
    out += [f'## {tag}：v3.7 {len(a)} 字 → v5 {len(b)} 字', '',
            f'v3.7 共 {len(ss)} 句：逐字保留 {len(keep)}，改写 {len(rew)}，删除 {len(dead) + len(other)}（含老路由词 {len(dead)}，其余 {len(other)}）。', '']
    if rew:
        out += ['### 改写（原句 → 新句）', '']
        out += [f'- 原：{s}\n  新：{t}' for s, t in rew] + ['']
    if dead:
        out += ['### 删除：老路由（S 锁、05.5、增强锁、结构化接力、回执等，S 和 D1 并掉以后不再存在）', '']
        out += [f'- {s}' for s in dead] + ['']
    if other:
        out += ['### 删除：不含老路由词的句子（逐句看过，都是老路由那一节里的配套句或后台回执说明；有执行价值的已在第四节补回）', '']
        out += [f'- {s}' for s in other] + ['']
out += ['## 四、父会话补回的句子（F1 删多了的活规则，"05"改称"A 稿"后放回）', '',
        '- 0 节："只把已经采用的动作、构图、摄影机、光学和声音结果编进 P，不把审计说明交给视频模型。"',
        '- 1.1 节："多 GEN、跨段状态或整段审计时，读完整 A 稿（骨架加相关 GEN 的逐镜细稿）。"',
        '- 1.3 节："A 稿有已确认修订时，只编译修订后的结果，不回旧版 A 稿寻找已废止依据；新旧版本并存时，即使新结果已经写入，也不得放行。"',
        '- 3.1 节：把"这三条总谱"改成"四条总谱（核心动作链、导演与摄影机总设计、连续表演链、声音链）"，补"连续表演链锁人物从起态到新状态怎么一级级推进"，和内核 §4 一致。',
        '- 4.4 节：补回"06 不编译情绪标签或未落地的形容词……只有 A 稿已确认的具体载体才能进入人物与动作句"、"已采用的导演决定没有对应执行句……Prompt Lock 失败；不用「克制、稳定、电影感」补执行空白"、"样板、示范原句、案例正文……不原样进入模型提示词"。', '']
(D / '证据表_F1.md').write_text('\n'.join(out), encoding='utf-8')
print('written', len('\n'.join(out)))
