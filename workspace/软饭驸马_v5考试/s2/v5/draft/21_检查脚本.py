#!/usr/bin/env python3
"""终稿检查 v5 R01（由通用底座 04a_终稿检查.py 复制后扩展，原件不动）

用法：python3 21_检查脚本.py <终稿.md>

查这些（都是第一季成片或平台拦截证实过的毛病，编号对应 40_病历.md）：
- 代码块字数（硬上限 1 万，M33）
- 三个一级板块、约束词 12 区块、每个 CUT 16 项标签和静止观察四行、各 CUT 字数（不到 250 字、越写越省）
- 首句三道锁：禁文字水印、反 2D 锁（M01）、肤色锁（M02）；系统提示音（M20）
- 审核高危词（M28-M31）、比喻和颜色词（M02、M31）、拖字语速词（M21）、空景写法（M06）、门纸剪影倒影（M36）
- 内部引用（R06 新增）：内核 §、病历 M、某某包第几条、必见事实编号这类写给人看的引用不进终稿
v5 新增两项提醒：
- 绝对方位：东南西北接 侧/面/墙/端/角/门/窗/边，或 朝/往/向 接东南西北（§1.5 画左画右，不写东南西北）
- 台词时间窗：从 CUT 时间和台词字段算出字/秒，超过约 4.5 字/秒报提醒（02-09、11-07）
分两级：问题（必须改）、提醒（看一眼，多数情况要改）。只报，不改稿。
"""
import re
import sys
from pathlib import Path

LABELS = ['机位与构图', '进入状态', '触发', '动作', '六类表演', '台词', '景别与层次', '景深与焦点',
          '摄影机', '静止观察', '声音', '光线与材质', '切入理由', '切点', '可见或可听停点', '下一镜接口']
STILL4 = ['画内变化', '声音关系', '结果观察', '停点']
BLOCKS12 = ['唯一戏剧任务', '首帧', '核心动作链', '主导画面机制', '摄影总设计', '世界不变量',
            '连续表演总链', '六类表演总链', '整体声音链', '段尾状态', '下一段接口']
HARD = {
    '审核高危词（M28-M31）': r'砸|掐|踹|胸口|揉胸|额头贴地|憋着气|蠢货|脱衣|赤裸',
    '比喻词（M02、M31）': r'像|仿佛|如同|宛如|好似|犹如|恍若|一般地',
    '脸色和颜色词（M02）': r'发白|发灰|发青|死灰|铁青|面如|石化|冻住|涨红|通红|苍白|煤灰|红润',
    '拖字语速词（M21）': r'慢悠悠|拖长|拉长|拖一点|拖一拍|顿半拍|一字一顿|放慢|一个字一个字',
    '空景写法（M06）': r'空无一人|空床|空荡荡',
    '门纸剪影倒影（M36）': r'剪影|倒影|门纸|窗纸',
    '内部引用（内核、病历、技能包、必见事实编号，视频模型看不懂）': r'内核\s*§|病历\s*M\d|(?:喜剧|打斗|奇观|群像|特效)包\s*[一二三四五六七八九十0-9]|技能包|必见事实|§\s*\d',
}
SOFT = {
    '审核提醒（M28-M30，多了容易被拦）': r'血|瘫|压得|插死|床帐|欺压',
    '脸色提醒（M02）': r'脸色|面色|气色',
}
NEG = re.compile(r'[不无没禁别勿非免]')
LABEL_PAT = {k: re.compile(rf'(?<![听总]){k}\s*[：:｜|]') for k in LABELS + STILL4}
CUT_HEAD = re.compile(r'(?m)^\s*\**\s*([0-9.]+)\s*[-–—~～]+\s*([0-9.]+)\s*秒\s*[｜|]')

# v5 新增：绝对方位词（§1.5 画左画右，不写东南西北）
DIR_PAT = re.compile(r'[东南西北][侧面墙端角门窗边]|[朝往向][东南西北]')
# v5 新增：台词时间窗。台词行形如 "台词：0.1–1.0 秒，李沧月……：\"停车！\"……"
# 一行里可能有多个"时间窗 … 原文"，把每句原文配到它前面最近的时间窗，分别算字/秒。
TAICI_TIME = re.compile(r'([0-9.]+)\s*[-–—~～]+\s*([0-9.]+)\s*秒')
TAICI_QUOTE = re.compile(r'[「“"]([^」”"]+)[」”"]')
NO_LINE = re.compile(r'本镜没有台词|没有台词|全员闭口')
# 跨 CUT 没说完的句子，不按被截断的半截时间窗算（02-09 不为短截断台词）
CONTINUE_LINE = re.compile(r'接到下一镜|接下一镜|承接|下一镜说完|说完|句子没完|未说完|往下接|[——]$')
MAX_CPS = 4.5


def code_block(text):
    m = re.search(r'```[^\n]*\n(.*?)```', text, re.S)
    return m.group(1) if m else ''


def scan(body, pat, skip_negated=True):
    hits = []
    for m in re.finditer(pat, body):
        before = body[max(0, m.start() - 10): m.start()]
        before = re.split(r'[。；;\n]', before)[-1]
        ctx = body[max(0, m.start() - 10): m.end() + 10].replace('\n', ' ')
        if skip_negated and NEG.search(before):
            continue
        if m.group(0) == '像' and re.search(r'胸像|图像|影像|画像|像素|镜像|头像|人像', ctx):
            continue
        hits.append(ctx)
    return hits


def cn_len(s):
    """台词字数：只数汉字，不数标点和空白（字/秒按汉字算）。"""
    return len(re.findall(r'[\u4e00-\u9fff]', s))


def scan_direction(shots, parts, starts):
    """返回 [(cut_label_or_index, 片段文本)]，cut 顺序由 parts 对应。"""
    hits = []
    for i, seg in enumerate(parts):
        label = f'第{i + 1}个CUT'
        for m in DIR_PAT.finditer(seg):
            ctx = seg[max(0, m.start() - 8): m.end() + 8].replace('\n', ' ')
            hits.append((label, ctx))
    return hits


def scan_taici_cps(parts):
    """对每个 CUT：找台词行，把每句台词原文配到它前面最近的时间窗，
    汉字数 ÷ 秒数 超过 4.5 报提醒；跨 CUT 没说完的句子和算不出的跳过。"""
    notes = []
    for i, seg in enumerate(parts):
        for line in seg.splitlines():
            if '台词' not in line or ('：' not in line and ':' not in line):
                continue
            if NO_LINE.search(line):
                continue
            if CONTINUE_LINE.search(line.strip()):
                continue  # 这句话跨到下一镜，不按半截窗算（02-09：不为短截断台词）
            # 收集这一行里所有 时间窗 和 原文 的出现位置，按位置把原文配到前一个窗
            times = [(m.start(), float(m.group(2)) - float(m.group(1)))
                     for m in TAICI_TIME.finditer(line)]
            quotes = [(m.start(), cn_len(m.group(1))) for m in TAICI_QUOTE.finditer(line)]
            if not times or not quotes:
                continue
            for qpos, qchars in quotes:
                if qchars == 0:
                    continue
                prev = [d for tpos, d in times if tpos < qpos]
                dur = prev[-1] if prev else times[0][1]
                if dur <= 0:
                    continue
                cps = qchars / dur
                if cps > MAX_CPS:
                    notes.append(
                        f'第{i + 1}个CUT：一句台词约 {qchars} 字 ÷ {dur:.1f} 秒 = {cps:.1f} 字/秒（超 {MAX_CPS}）：'
                        + line.strip()[:48])
    return notes


def main(path):
    p = Path(path)
    if not p.exists():
        print(f'用法: python3 {sys.argv[0]} <终稿.md>')
        return 1
    body = code_block(p.read_text(encoding='utf-8'))
    problems, notes = [], []
    if not body:
        body = p.read_text(encoding='utf-8')
        notes.append('没有代码块，按全文检查（交给视频模型前要放进一个代码块）')
    n = len(body)
    print(f'字数：{n}' + ('（超过 1 万，必须压）' if n > 10000 else ''))
    if n > 10000:
        problems.append('字数超 1 万')

    for b in ['【约束词】', '【对应图片】', '【镜头']:
        if b not in body:
            problems.append(f'缺板块 {b}')
    cons = body.split('【对应图片】')[0]
    miss = [k for k in BLOCKS12 if k not in cons]
    if miss:
        problems.append('约束词缺区块：' + '、'.join(miss))
    head = cons[:700]
    if not ('不要生成音乐' in head and '字幕' in head and '水印' in head):
        problems.append('首句缺"不要生成音乐、字幕、水印、文字"')
    if not re.search(r'不是\s*2D|非\s*2D|不是二维|不是\s*2D\s*动漫', cons):
        problems.append('缺反 2D 锁（M01）')
    if '肤色' not in cons:
        problems.append('缺肤色锁（M02）')
    if scan(body, r'系统(面板|画面|出场|光|空间)') and '不要生成系统提示音' not in body:
        problems.append('有系统画面，但没写"不要生成系统提示音"（M20）')
    if re.search(r'环绕', body) and not re.search(r'不出现摄影机|摄影机.{0,6}不入画|拍摄器材', body):
        notes.append('有环绕运镜，没写"画面里不出现摄影机、拍摄器材"（M24，第一季 26-1 出过一次）')

    shots = body.split('【镜头')[-1]
    heads = list(CUT_HEAD.finditer(shots))
    parts = CUT_HEAD.split(shots)
    # re.split 带捕获组：parts[0] 是镜头板块标题残留，之后每 3 个一组（起、止、正文）
    segs = []
    for k in range(1, len(parts), 3):
        if k + 2 < len(parts):
            segs.append(parts[k + 2])
        elif k < len(parts):
            segs.append(parts[-1])
    cuts = len(heads)
    print(f'CUT 数：{cuts}')
    if cuts == 0:
        problems.append('镜头板块里没找到"起止秒｜CUT 编号"开头的镜头')
    counts = {k: len(pat.findall(shots)) for k, pat in LABEL_PAT.items()}
    print('标签计数（每项应 ≥ CUT 数）：' + '  '.join(f'{k}={v}' for k, v in counts.items()))
    short = {k: v for k, v in counts.items() if v < cuts}
    if short:
        problems.append('这些标签少于 CUT 数：' + '、'.join(f'{k}({v}/{cuts})' for k, v in short.items()))
    if segs:
        lens = [len(x) for x in segs]
        print('各 CUT 字数：' + ' '.join(map(str, lens)))
        thin = [i + 1 for i, L in enumerate(lens) if L < 250]
        if thin:
            problems.append('这些 CUT 不到 250 字：第 ' + '、'.join(map(str, thin)) + ' 个')
        if len(lens) >= 4 and (lens[-1] + lens[-2]) < 0.6 * (lens[0] + lens[1]):
            problems.append('后面的 CUT 比前面明显短（越写越省）')
        oneline = [i + 1 for i, x in enumerate(segs) if x.strip().count('\n') < 6]
        if oneline:
            notes.append('这些 CUT 的标签挤在一两行里，不是一项一行：第 ' + '、'.join(map(str, oneline)) + ' 个')

    for name, pat in HARD.items():
        hits = scan(body, pat)
        if hits:
            problems.append(f'{name}：' + '｜'.join(hits[:8]) + (f' 等 {len(hits)} 处' if len(hits) > 8 else ''))
    for name, pat in SOFT.items():
        hits = scan(body, pat)
        if hits:
            notes.append(f'{name}：' + '｜'.join(hits[:6]) + (f' 等 {len(hits)} 处' if len(hits) > 6 else ''))

    # v5 新增提醒一：绝对方位
    dir_hits = scan_direction(shots, segs, None)
    if dir_hits:
        where = '；'.join(f'{lab}「{ctx}」' for lab, ctx in dir_hits[:8])
        notes.append(f'绝对方位 {len(dir_hits)} 处（§1.5 用画左画右，不写东南西北）：' + where
                     + (f' 等' if len(dir_hits) > 8 else ''))
    # v5 新增提醒二：台词时间窗
    cps_notes = scan_taici_cps(segs)
    for x in cps_notes:
        notes.append('台词时间窗（02-09）：' + x)

    print('---')
    print('问题：' + (f'{len(problems)} 个' if problems else '无'))
    for i, x in enumerate(problems, 1):
        print(f'  {i}. {x}')
    print('提醒：' + (f'{len(notes)} 个' if notes else '无'))
    for i, x in enumerate(notes, 1):
        print(f'  {i}. {x}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ''))
