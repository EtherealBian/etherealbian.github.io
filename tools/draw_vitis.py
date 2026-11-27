"""Rebuild the five portfolio figures using only Python's standard library.

Evidence and figure-design references: ../ASSETS.md. Run from any directory.
SVG text stays selectable when opened as a standalone file.
"""

from base64 import b64encode
from contextlib import contextmanager
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "plates"
INK, SOFT, GREEN, TEAL, MINT = "#203e46", "#516877", "#236951", "#347a79", "#e6f2ed"
BLUE, BLUE_BG, GOLD, GOLD_BG = "#496987", "#eaf0f6", "#90663a", "#f8f0e1"
RULE, PAPER = "#ccd8d8", "#ffffff"


class Plate:
    def __init__(self, w, h, name, desc):
        self.w, self.h = w, h
        self.el = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(name)}</title><desc id="desc">{escape(desc)}</desc>',
            """<defs><marker id="tip" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 7 3.5 0 7z" fill="#496778"/></marker><pattern id="ruled" width="7" height="7" patternUnits="userSpaceOnUse"><path d="m-1 1 2-2m-1 8 7-7m-1 8 2-2" stroke="#c5d3d6" fill="none"/></pattern></defs><style>text{font-family:'Segoe UI','Microsoft YaHei',sans-serif}.serif{font-family:Georgia,'Times New Roman',serif}.mono{font-family:Consolas,'Microsoft YaHei',monospace}</style>""",
        ]
        self.rect(0, 0, w, h, PAPER)

    def rect(self, x, y, w, h, fill=PAPER, stroke="none", r=0):
        self.el.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
        )

    def text(self, x, y, s, size=16, weight=400, fill=INK, anchor="start", cls=""):
        self.el.append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" class="{cls}">{escape(str(s))}</text>'
        )

    def path(self, d, color=RULE, sw=1, arrow=False, dash=False):
        a = ' marker-end="url(#tip)"' if arrow else ""
        b = ' stroke-dasharray="5 4"' if dash else ""
        self.el.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{a}{b}/>'
        )

    def wire(self, d, dash=False):
        self.path(d, "#496778", 1.7, True, dash)

    def circ(self, x, y, r, fill, stroke="none"):
        self.el.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')

    def block(self, x, y, w, h, title, sub=None, tone="blue"):
        fill, edge = {
            "blue": (BLUE_BG, "#a5b9c9"),
            "green": (MINT, "#9cbfb1"),
            "gold": (GOLD_BG, "#cbbd9b"),
            "white": (PAPER, "#aebec2"),
        }[tone]
        self.rect(x, y, w, h, fill, edge, 4)
        m = x + w / 2
        self.text(m, y + h / 2 + (5 if not sub else -3), title, 17, 600, INK, "middle")
        if sub:
            self.text(m, y + h / 2 + 18, sub, 13, 400, SOFT, "middle")

    def header(self, letter, title, sub):
        self.rect(25, 23, 34, 34, INK, r=4)
        self.text(42, 47, letter, 23, 600, PAPER, "middle", "serif")
        self.text(72, 50, title, 28, 600)
        self.text(self.w - 26, 47, sub, 14, 500, SOFT, "end", "mono")
        self.path(f"M25 70H{self.w - 25}")

    @contextmanager
    def group(self, x, y):
        self.el.append(f'<g transform="translate({x} {y})">')
        try:
            yield
        finally:
            self.el.append("</g>")

    def save(self, file):
        (OUT / file).write_text("\n".join(self.el + ["</svg>", ""]), encoding="utf8")


# The lead plate has its own composition. The four detail plates below can be
# read separately and are deliberately not scaled-down inserts in this figure.
NAVY, SLATE = "#203f58", "#475e6c"
INDIGO = ("#265b8b", "#eaf2fa", "#abc4d9")
JADE = ("#21695a", "#eaf4ef", "#aacdbd")
OCHRE = ("#885a27", "#faf2e5", "#d4be9c")
NEUTRAL = (NAVY, "#f3f6f7", "#b9c7cc")


def node(d, x, y, w, h, label, palette=NEUTRAL, size=17, note=None):
    ink, tint, edge = palette
    d.rect(x, y, w, h, tint, edge, 3)
    middle = x + w / 2
    if note:
        d.text(middle, y + h / 2 - 3, label, size, 600, ink, "middle")
        d.text(middle, y + h / 2 + 17, note, 14, 400, SLATE, "middle")
    else:
        d.text(middle, y + h / 2 + size * 0.34, label, size, 600, ink, "middle")


def letter(d, x, y, value, color):
    d.rect(x, y, 28, 28, color, r=3)
    d.text(x + 14, y + 20, value, 21, 650, PAPER, "middle", "serif")


def kernel_frame(d, letter_id, title, principle, issue, palette):
    accent, _, edge = palette
    d.rect(0, 0, 472, 476, PAPER, edge, 5)
    d.rect(0, 0, 472, 4, accent)
    letter(d, 17, 18, letter_id, accent)
    d.text(57, 41, title, 30, 650, NAVY)
    d.text(18, 77, principle, 18, 550, NAVY)
    d.text(18, 106, issue, 17, 450, SLATE)
    d.path("M18 124H454", edge)


def kernel_result(d, palette, delta, cycles, check, tradeoff):
    ink, tint, edge = palette
    d.rect(1, 308, 470, 139, tint)
    d.path("M1 308H471", edge)
    d.text(18, 334, "总周期缩减", 15, 550, SLATE)
    d.text(205, 334, "同一负载 · 基线 → 优化（周期）", 15, 550, SLATE)
    d.text(17, 379, delta, 42, 650, ink, cls="serif")
    d.text(205, 376, cycles, 25, 600, NAVY, cls="mono")
    d.path("M19 405l4 4 8-10", ink, 2.4)
    d.text(40, 411, check, 16, 600, NAVY)
    d.text(18, 436, tradeoff, 15, 400, SLATE)


def sha_panel(d):
    # The dashed path selects the output core; solid edges carry data.
    d.wire("M56 164V117H414V163", True)
    d.rect(140, 103, 181, 26, PAPER)
    d.text(230, 122, "顺序 FIFO · 核心编号", 15, 500, SLATE, "middle")
    node(d, 17, 167, 79, 53, "分发", note="整条消息")
    node(d, 374, 167, 80, 53, "合并", JADE, note="按序取回")
    for i, y in enumerate((140, 206)):
        d.wire(f"M96 194H111V{y + 21}H126")
        d.rect(130, y, 207, 42, INDIGO[1], INDIGO[2], 3)
        d.text(143, y + 27, f"核 {i}", 17, 650, INDIGO[0])
        d.path(f"M189 {y + 7}v28", INDIGO[2])
        d.text(201, y + 27, "生成 Wₜ → 64 轮", 16, 550, NAVY)
        d.path(f"M337 {y + 21}H354V194", "#496778", 1.7)
    d.wire("M354 194H370")
    d.text(18, 274, "补位时生成调度字，省去块间复制。", 17, 500, NAVY)
    d.text(18, 297, "双核处理不同消息；同一消息的 64 轮仍然串行。", 16, 400, SLATE)
    kernel_result(
        d,
        INDIGO,
        "46.5%",
        "809 → 592 → 433",
        "两条消息的摘要通过 C/RTL 协同仿真。",
        "中间值 592 为仅融合阶段；双核版使用 31,477 LUT。",
    )


def lz_panel(d):
    d.text(18, 129, "8 路 BRAM 分区", 16, 600, JADE[0])
    d.text(169, 129, "并行比较", 16, 600, JADE[0])
    for bank in range(8):
        x = 18 + bank * 14
        d.rect(x, 152, 11, 73, JADE[1], JADE[2])
        d.rect(x, 152, 11, 16, "#81b19f")
        for r in (187, 205):
            d.path(f"M{x} {r}h11", JADE[2])
    d.path("M127 188H143M143 158V219", "#496778", 1.7)
    for j, y in enumerate((146, 177, 208)):
        d.wire(f"M143 {y + 11}H160")
        node(d, 164, y, 94, 23, ("候选 0", "候选 1", "其余候选")[j], JADE, 14)
        d.path(f"M258 {y + 11}H271V188", "#496778", 1.7)
    d.wire("M271 188H282")
    node(d, 286, 163, 77, 51, "取最长", note="两两归约")
    d.wire("M363 188H377")
    node(d, 381, 163, 73, 51, "Token", OCHRE, note="编码查表")
    d.text(18, 249, "有效标签 + 历史项", 14, 400, SLATE)
    d.text(18, 274, "读字典时检查批次标签，旧条目无需清零。", 17, 500, NAVY)
    d.text(18, 297, "并行比较匹配长度，胜出候选送入编码器。", 16, 400, SLATE)
    kernel_result(
        d,
        JADE,
        "≈60.4%",
        "≈3,390 → 1,343",
        "样例解压一致，压缩比保持 2.09396。",
        "协同仿真通过；综合共用 118 个 BRAM_18K。",
    )


def chol_panel(d):
    d.text(18, 129, "3 × 3 定点复矩阵", 16, 600, OCHRE[0])
    d.text(191, 129, "末行的并行部分和", 16, 600, OCHRE[0])
    for r in range(3):
        for c in range(3):
            fill = (OCHRE[0] if r == 2 and c < 2 else OCHRE[2]) if c <= r else "#f3f4f2"
            d.rect(20 + c * 25, 146 + r * 25, 21, 21, fill)
    d.wire("M91 207H123V166H149")
    d.wire("M123 207H149")
    node(d, 154, 151, 82, 29, "|L₂₀|²", OCHRE)
    node(d, 154, 192, 82, 29, "|L₂₁|²", OCHRE)
    d.path("M236 166H252V186M236 207H252V186", "#496778", 1.7)
    d.wire("M252 186H267")
    d.circ(286, 186, 16, OCHRE[1], OCHRE[2])
    d.text(286, 193, "Σ", 22, 600, OCHRE[0], "middle", "serif")
    d.wire("M302 186H335")
    d.circ(353, 186, 15, NEUTRAL[1], NEUTRAL[2])
    d.text(353, 192, "−", 21, 600, NAVY, "middle")
    d.text(353, 150, "A₂₂", 16, 600, NAVY, "middle")
    d.wire("M353 155v12")
    d.wire("M368 186H397")
    d.text(407, 193, "x", 22, 600, OCHRE[0], cls="serif")
    d.text(18, 249, "下三角按行推进", 14, 400, SLATE)
    d.text(175, 249, "x = A₂₂ − (|L₂₀|² + |L₂₁|²)", 16, 550, NAVY)
    d.text(18, 274, "二维完全分区，展开同一行的独立乘加。", 17, 500, NAVY)
    d.text(18, 297, "对角残差 x 取分段初值，再用 Newton 逼近 1/√x。", 16, 400, SLATE)
    kernel_result(
        d,
        OCHRE,
        "71.4%",
        "4,919 → 1,407",
        "8 组矩阵通过残差阈值；非逐元素一致。",
        "单事务协同仿真 175 周期；并行乘法使用 152 个 DSP。",
    )


def finals_panels(d):
    # Independent hardware chain, followed by a separately labelled archival plot.
    d.path("M26 636H1478", "#9dadb6", 1.2)
    d.text(27, 676, "02", 22, 600, INDIGO[0], cls="mono")
    d.text(80, 676, "决赛  /  Zynq 实时频谱仪", 28, 650, NAVY)
    d.text(1478, 672, "独立整机工程   ·   初赛三项算子不接入下方信号链", 17, 450, SLATE, "end")
    d.rect(26, 698, 995, 258, PAPER, "#b8c7ce", 4)
    letter(d, 42, 713, "d", INDIGO[0])
    d.text(81, 735, "从采样到功率谱", 23, 650, NAVY)
    d.text(1003, 733, "AXI4-Stream    /    PL → PS", 15, 550, SLATE, "end", "mono")
    node(d, 45, 764, 207, 49, "10 位 ADC · 32 MSPS", INDIGO, note="异步 FIFO：32 → 100 MHz")
    node(d, 45, 832, 207, 49, "UDP 音频 · 48 kHz", JADE, note="PS → DMA MM2S · int16")
    d.wire("M252 788H269V810H285")
    d.wire("M252 856H269V838H285")
    node(d, 289, 797, 97, 53, "AXIS 选择", note="二选一")
    node(d, 416, 797, 136, 53, "数字下变频", INDIGO, note="NCO · 混频抽取")
    node(d, 583, 797, 116, 53, "FFT", INDIGO, note="可选 Hann 窗")
    node(d, 731, 797, 120, 53, "|X[k]|²", JADE, note="float32 功率")
    node(d, 882, 797, 119, 53, "PYNQ", JADE, note="dB · 峰值追踪")
    for x1, x2 in ((386, 412), (552, 579), (699, 727), (851, 878)):
        d.wire(f"M{x1} 823H{x2}")
    d.text(484, 780, "射频：32 位 NCO", 14, 550, SLATE, "middle")
    d.text(484, 877, "音频：旁路混频与抽取", 14, 500, SLATE, "middle")
    d.text(641, 780, "1,024–16,384 点", 14, 550, SLATE, "middle")
    d.text(873, 780, "DMA S2MM 写回", 14, 550, SLATE, "middle")
    d.path("M45 898H1002")
    d.text(45, 931, "音频模式", 18, 650, JADE[0])
    d.text(155, 931, "0–24 kHz", 19, 650, NAVY)
    d.text(310, 931, "演示配置：48,000 Hz ÷ 4,096 点 ≈ 11.72 Hz / 频点（计算值）", 17, 450, SLATE)
    d.rect(1039, 698, 439, 258, PAPER, "#b8c7ce", 4)
    letter(d, 1055, 713, "e", JADE[0])
    d.text(1094, 735, "竞赛界面的双峰记录", 23, 650, NAVY)
    # Keep the recorded curve, axes and markers. The embedded source makes
    # the SVG portable when loaded via <img> or saved on its own.
    pixels = b64encode((OUT / "spectrum.webp").read_bytes()).decode("ascii")
    d.el.append(
        f'<svg x="1054" y="762" width="245" height="149" viewBox="531 288 214 130" overflow="hidden"><image width="768" height="811" href="data:image/webp;base64,{pixels}"/></svg>'
    )
    d.text(1312, 782, "界面检出主峰", 15, 500, SLATE)
    d.text(1312, 821, "80 Hz", 32, 650, JADE[0], cls="serif")
    d.text(1312, 861, "150 Hz", 32, 650, JADE[0], cls="serif")
    d.text(1055, 936, "截图另用 1 kHz / 1,024 点；曲线截自竞赛原图。", 16, 450, SLATE)


def overview():
    d = Plate(
        1504,
        1008,
        "Vitis HLS 算子微架构、验证结果与 Zynq 信号链",
        "a–c 分别给出 HMAC-SHA256、LZ4、Cholesky 的瓶颈、硬件数据流、固定用例协同仿真周期及验证边界。d 是决赛独立频谱仪的双输入、下变频、FFT 至 PYNQ 通路；e 为竞赛截图中的 80 Hz 与 150 Hz 双峰。",
    )
    d.text(26, 65, "Vitis HLS", 57, 650, INDIGO[0], cls="serif")
    d.path("M329 25v46", "#c0cdd5", 1.5)
    d.text(353, 62, "算子微架构与实时频谱分析", 34, 650, NAVY)
    d.rect(26, 94, 1452, 54, "#edf3f7", "#c2d0d9", 3)
    d.text(42, 129, "01", 20, 600, INDIGO[0], cls="mono")
    d.text(96, 129, "初赛  /  三项独立算子", 23, 650, NAVY)
    for x, label in [(407, "固定赛题输入"), (592, "C/RTL 协同仿真"), (806, "对照总执行周期")]:
        d.text(x, 128, label, 18, 550, SLATE)
    d.wire("M531 121h39")
    d.wire("M744 121h40")
    d.text(1460, 127, "Vitis HLS 2024.2  ·  xc7z020-clg484-1", 16, 500, NAVY, "end", "mono")
    kernels = [
        (
            26,
            "a",
            "HMAC-SHA256",
            "消息与内层密钥散列，所得摘要再与外层密钥散列。",
            "瓶颈：补位与调度分开传块，两条消息先后计算。",
            INDIGO,
            sha_panel,
        ),
        (
            516,
            "b",
            "LZ4",
            "滑窗寻找重复字节，用偏移与长度表示匹配串。",
            "瓶颈：遍历清空 4,096 个字典项，串行比较候选。",
            JADE,
            lz_panel,
        ),
        (
            1006,
            "c",
            "Cholesky",
            "A = LLᴴ：逐行解出正定矩阵的三角因子。",
            "瓶颈：访存与行内累加串行，对角倒根延迟高。",
            OCHRE,
            chol_panel,
        ),
    ]
    for x, panel, name, principle, issue, tone, draw in kernels:
        with d.group(x, 167):
            kernel_frame(d, panel, name, principle, issue, tone)
            with d.group(0, 28):
                draw(d)
    with d.group(0, 28):
        finals_panels(d)
    d.save("vitis-hls-architecture.svg")


def sha():
    d = Plate(
        820,
        286,
        "HMAC-SHA256 消息级并行",
        "完整消息轮询分给两核，每核融合补位与调度；单独的顺序 FIFO 控制摘要合并。",
    )
    d.header("a", "HMAC-SHA256", "消息级并行")
    d.block(24, 143, 119, 60, "消息分发", "轮询 · 整条消息", "white")
    d.block(655, 143, 135, 60, "有序合并", "按记录取摘要", "green")
    d.wire("M84 143V99H718V138", True)
    d.rect(292, 85, 222, 24, PAPER)
    d.text(403, 103, "order_core_strm · 顺序 FIFO", 14, 450, SOFT, "middle", "mono")
    for i, y in enumerate((119, 192)):
        d.rect(218, y, 339, 57, BLUE_BG, "#a9bcc9", 4)
        d.text(233, y + 35, f"SHA {i}", 19, 650, BLUE)
        d.path(f"M301 {y + 9}v39", "#c0cdd7")
        d.text(315, y + 25, "补位 + 调度字", 17, 600)
        d.text(315, y + 45, "融合生成", 13, 400, SOFT)
        d.wire(f"M438 {y + 29}h23")
        d.text(472, y + 34, "64 轮压缩", 16, 600)
        d.wire(f"M143 174H176V{y + 29}H213")
        d.path(f"M557 {y + 29}H604V174", "#496778", 1.7)
    d.wire("M604 174H650")
    d.text(24, 271, "两个核心处理不同消息；同一核心内保留 64 轮的链式依赖。", 15, 400, SOFT)
    d.save("vitis-sha.svg")


def lz4():
    d = Plate(
        820,
        286,
        "LZ4 字典有效性与并行匹配",
        "哈希字典和批次标志分银行存入 BRAM。候选通路并行验证，归约后由编码端查表产生 Token。",
    )
    d.header("b", "LZ4", "字典与候选匹配")
    d.text(29, 102, "分区双口 BRAM", 16, 600)
    d.text(275, 102, "并行匹配", 16, 600)
    d.text(506, 102, "归约与编码", 16, 600)
    for n in range(8):
        xx = 29 + 20 * n
        d.rect(xx, 126, 17, 56, BLUE_BG, "#a4bac8")
        d.rect(xx, 127, 17, 13, "#becfdb")
        d.path(f"M{xx} 158h17", "#b0c3d0")
    d.text(29, 206, "historyData / 批次标签", 14, 500, SOFT)
    d.wire("M186 153H230")
    d.path("M230 125V195", "#496778", 1.7)
    for j, y in enumerate((111, 146, 181)):
        d.wire(f"M230 {y + 14}H263")
        d.rect(268, y, 142, 28, MINT, "#acc7bb", 3)
        d.text(339, y + 20, ["候选 0 · 比较", "候选 1 · 比较", "其余候选 …"][j], 15, 550, INK, "middle")
        d.path(f"M410 {y + 14}H435V160", "#496778", 1.7)
    d.wire("M435 160H480")
    d.block(484, 131, 125, 58, "最佳匹配", "两两选长", "green")
    d.wire("M609 160h30")
    d.block(644, 131, 145, 58, "Token 查表", "编码输出", "gold")
    d.path("M29 229H790")
    d.text(29, 260, "批次标签使上一批字典项失效，省去逐项清空。归档样例压缩比：2.09396。", 15, 400, SOFT)
    d.save("vitis-lz4.svg")


def chol():
    d = Plate(
        820,
        286,
        "Cholesky 矩阵访问与行内归约",
        "分区矩阵向行内并行部分和供数，完成归约。定点对角倒数使用分段初值与 Newton 迭代。",
    )
    d.header("c", "Cholesky", "行内并行 · 行间依赖")
    d.text(29, 102, "二维完全分区", 16, 600)
    d.text(242, 102, "独立部分和", 16, 600)
    d.text(544, 102, "定点对角倒数", 16, 600)
    for row in range(3):
        for col in range(3):
            d.rect(
                32 + col * 29,
                116 + row * 29,
                25,
                25,
                TEAL if row == 2 and col < row else "#b6cfc7" if col <= row else "#f1f4f2",
            )
    d.text(32, 226, "3 × 3 · 末行示例", 13, 400, SOFT)
    d.wire("M116 186H176")
    d.path("M176 132V194", "#496778", 1.7)
    for j, y in enumerate((116, 147, 178)):
        d.wire(f"M176 {y + 14}H215")
        d.rect(220, y, 105, 27, BLUE_BG, "#a8bbc9", 3)
        d.text(272, y + 19, ["|L₂₀|²", "|L₂₁|²", "0（j ≥ i）"][j], 14, 550, INK, "middle")
        d.path(f"M325 {y + 14}H351V161", "#496778", 1.7)
    d.wire("M351 161h27")
    d.circ(399, 161, 19, MINT, "#9bbcad")
    d.text(399, 168, "Σ", 22, 600, GREEN, "middle", "serif")
    d.wire("M418 161h12")
    d.circ(442, 161, 11, GOLD_BG, "#cbbd9b")
    d.text(442, 167, "−", 18, 600, INK, "middle")
    d.text(442, 119, "A₂₂", 16, 500, SOFT, "middle")
    d.wire("M442 125v21")
    d.wire("M453 161h17")
    d.text(453, 221, "x = A₂₂ − Σ |L₂ⱼ|²，j < 2", 15, 500, SOFT)
    d.block(475, 132, 124, 59, "分段初值", "区间选常数", "blue")
    d.wire("M599 161h33")
    d.block(637, 132, 153, 59, "Newton 迭代", "逼近 1 / √x", "green")
    d.path("M29 238H790")
    d.text(29, 265, "固定 3 × 3 复数矩阵。1,407 周期为测试总量；单次事务为 175 周期。", 15, 400, SOFT)
    d.save("vitis-cholesky.svg")


def system():
    d = Plate(
        1160,
        560,
        "Zynq 实时频谱仪的采集域、PL 与 PS",
        "ADC 量化后跨时钟域；UDP 经 DMA 发送。两种输入由 AXIS Switch 选入 DDC 和 FFT；功率通过 DMA 写回 PYNQ。",
    )
    d.header("d", "Zynq 实时频谱仪", "决赛 / 数据与控制通路")
    d.rect(24, 92, 232, 333, "#f4f6f5", "#c8d5d0", 5)
    d.rect(274, 92, 615, 333, "#f4f7fa", "#c1ced7", 5)
    d.rect(905, 92, 230, 333, "#f0f6f1", "#bdcec0", 5)
    d.text(39, 119, "输入源", 20, 650)
    d.text(290, 119, "PL", 23, 650, BLUE, cls="serif")
    d.text(333, 119, "可编程逻辑 · 100 MHz 处理域", 15, 450, SOFT)
    d.text(921, 119, "PS", 23, 650, GREEN, cls="serif")
    d.text(964, 119, "PYNQ", 16, 550, SOFT)
    d.block(39, 148, 201, 59, "10-bit ADC", "32 MSPS · 射频采样", "white")
    d.block(39, 281, 201, 60, "UDP / PCM", "48 kHz · int16 音频", "white")
    d.block(290, 148, 132, 59, "异步 FIFO", "32 → 100 MHz", "blue")
    d.block(290, 281, 132, 60, "DMA MM2S", "从 PS 送样本", "blue")
    d.wire("M240 177h46")
    d.wire("M240 311h46")
    d.text(40, 230, "偏移二进制 → 补码", 14, 450, SOFT)
    d.text(40, 365, "PYNQ 接收 · 每帧 4,096 点", 14, 450, SOFT)
    d.block(468, 215, 105, 60, "AXIS", "选一路输入", "white")
    d.wire("M422 177H443V232H464")
    d.wire("M422 311H443V260H464")
    d.wire("M573 245h25")
    d.block(603, 215, 120, 60, "DDC", "下变频 / 旁路", "blue")
    d.wire("M723 245h25")
    d.block(752, 215, 120, 60, "FFT", "可选 Hann 窗", "green")
    d.wire("M812 275V286H737V391H747")
    d.block(752, 372, 120, 38, "DMA S2MM", None, "blue")
    d.wire("M872 391H897V245H917")
    d.block(921, 215, 197, 60, "PS 连续内存", "接收 float32 功率", "white")
    d.wire("M1020 275v37")
    d.block(921, 317, 197, 63, "PYNQ 显示", "dB 换算 · 平均 · 主峰", "green")
    d.text(603, 308, "32-bit NCO", 15, 600, BLUE)
    d.text(603, 331, "复混频 → 积分抽取", 14, 450, SOFT)
    d.text(603, 354, "音频旁路，实数直通", 14, 450, SOFT)
    d.text(752, 308, "|X[k]|²", 20, 600, GREEN, cls="serif")
    d.text(752, 331, "输出 float32", 14, 450, SOFT)
    d.text(752, 354, "演示 4,096 点", 14, 450, SOFT)
    d.block(921, 140, 197, 48, "AXI4-Lite 配置", None, "white")
    d.wire("M921 162H663V210", True)
    d.wire("M812 162V210", True)
    d.text(452, 402, "AXI4-Stream · 实数样本或打包 I/Q", 15, 400, SOFT)
    d.text(26, 467, "HIGH", 18, 650, BLUE, cls="mono")
    d.text(26, 493, "ADC · 本振对准观察中心", 16, 450)
    d.text(26, 518, "显示中心附近频偏", 14, 400, SOFT)
    d.path("M365 454v72")
    d.text(395, 467, "LOW", 18, 650, BLUE, cls="mono")
    d.text(395, 493, "ADC · 本振频率为零", 16, 450)
    d.text(395, 518, "从直流观察低频段", 14, 400, SOFT)
    d.path("M749 454v72")
    d.text(778, 467, "AUDIO", 18, 650, GREEN, cls="mono")
    d.text(778, 493, "UDP · 旁路混频和抽取", 16, 450)
    d.text(778, 518, "显示 0–24 kHz 音频频谱", 14, 400, SOFT)
    d.save("vitis-zynq-system.svg")


if __name__ == "__main__":
    for draw in (overview, sha, lz4, chol, system):
        draw()
