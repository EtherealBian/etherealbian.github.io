"""Draw the five detailed catalog plates from archived project evidence (Pillow).

Run: python -B tools/draw_project_covers.py. The UAV and compiler covers are
independent originals, deliberately not generated here. Sources: ../ASSETS.md.
"""

import base64
import xml.etree.ElementTree as ET
from html import escape
from io import BytesIO
from math import cos, pi, radians, sin

from draw_vitis import INDIGO, JADE, NAVY, OCHRE, OUT, SLATE, Plate
from PIL import Image, ImageOps

ASSETS = OUT.parent
BLUE, GREEN, AMBER = INDIGO[0], JADE[0], OCHRE[0]
WHITE, RULE, PALE, DARK, MINT, GOLD = "#fff", "#cad6d7", "#f1f6f5", "#16383f", "#a9e0ca", "#ecc180"


def t(d, x, y, s, size=17, color=NAVY, weight=500, anchor="start", cls=""):
    d.text(x, y, s, size, weight, color, anchor, cls)


def center(d, x, y, s, size=17, color=NAVY, weight=550, cls=""):
    t(d, x, y, s, size, color, weight, "middle", cls)


def poly(d, pts, fill, stroke="none", sw=1):
    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    d.el.append(
        f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
    )


def line(d, pts, color, w=1, arrow=False, dash=False):
    d.path("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts), color, w, arrow, dash)


def grid(d, x, y, w, h, dx, dy, c):
    for u in range(x, x + w + 1, dx):
        d.path(f"M{u} {y}v{h}", c, 0.7)
    for v in range(y, y + h + 1, dy):
        d.path(f"M{x} {v}h{w}", c, 0.7)


def encode(im, size, crop=None, quality=86):
    if crop:
        im = im.crop(crop)
    im = ImageOps.fit(im.convert("RGB"), size, Image.Resampling.LANCZOS)
    out = BytesIO()
    im.save(out, "WEBP", quality=quality, method=6)
    return out.getvalue()


def embed(d, data, x, y, w, h):
    uri = base64.b64encode(data).decode("ascii")
    d.el.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/webp;base64,{uri}"/>')


def photo(d, name, x, y, w, h, crop=None):
    with Image.open(ASSETS / name) as im:
        embed(d, encode(im, (2 * w, 2 * h), crop), x, y, w, h)


def meta(d, txt):
    d.el.append("<metadata>" + escape(txt) + "</metadata>")


def page(n, word, title, sub, series, desc):
    d = Plate(1080, 720, title, desc)
    t(d, 34, 61, word, 44, BLUE, 690, cls="serif")
    t(d, 34, 93, sub, 18, SLATE, 480)
    t(d, 1046, 58, title, 33, NAVY, 670, "end")
    if series:
        t(d, 1046, 91, f"{series}   /   {n:02d}", 15, GREEN, 600, "end", "mono")
    d.path("M34 110H1046", NAVY, 1.6)
    return d


def section(d, x, y, letter, title, tone=GREEN):
    d.rect(x, y - 18, 24, 24, tone, r=3)
    center(d, x + 12, y, letter, 18, WHITE, 650, "serif")
    t(d, x + 35, y + 1, title, 21, tone, 650)


def footer(d, left, right=None):
    d.path("M34 677H1046", RULE)
    t(d, 34, 703, left, 15, SLATE)
    if right:
        t(d, 1046, 703, right, 15, SLATE, 520, "end")


def trace(d, cx, cy, rx, ry, fx, fy, phase, color, w=2.5):
    line(
        d,
        [
            (cx + rx * sin(fx * 2 * pi * i / 210), cy - ry * sin(fy * 2 * pi * i / 210 + phase))
            for i in range(211)
        ],
        color,
        w,
    )


def phase():
    d = page(
        3,
        "Lissajous",
        "两种闭环，一幅李萨如图形",
        "有线模式跟踪输入电压；无线模式观察屏幕轨迹。两种模式均由 FPGA 合成 Y 轴。",
        None,
        "工作台实拍、X–Y 示波原理与两条反馈通路：DPLL 以本振为参考，Jetson Nano 以摄像头为反馈。",
    )
    section(d, 34, 141, "a", "竞赛工作台", BLUE)
    photo(d, "lissajous-hardware.jpg", 34, 156, 266, 150, (0, 0, 1706, 1135))
    d.rect(34, 310, 266, 64, PALE)
    photo(d, "lissajous-hardware.jpg", 40, 314, 99, 56, (853, 95, 1138, 260))
    t(d, 153, 338, "示波器实拍", 18, BLUE, 650)
    t(d, 153, 360, "屏幕局部放大", 15, SLATE)

    # The two time series and the large XY trace share frequency ratio and phase.
    d.rect(319, 125, 727, 249, DARK, r=5)
    t(d, 339, 157, "示波器 · X–Y 显示", 22, WHITE, 630)
    t(d, 1025, 156, "X 接信号源   /   Y 接 DAC1", 17, MINT, 580, "end")
    grid(d, 338, 176, 490, 146, 21, 21, "#35585b")
    for y, axis, f, col in [(214, "X(t)", 1, GOLD), (283, "Y(t)", 2, MINT)]:
        t(d, 341, y + 5, axis, 17, col, 630, cls="mono")
        d.path(f"M386 {y}h138", "#759591", 0.9)
        line(d, [(386 + j, y - 20 * sin(2 * pi * f * j / 136)) for j in range(137)], col, 2.6)
    d.path("M530 214h12v35h21m-33 34h12v-34", "#8faea5", 1.4)
    poly(d, [(563, 245), (572, 249), (563, 253)], MINT)
    d.path("M580 249h244M702 181v136", "#829f97", 1)
    trace(d, 702, 249, 109, 55, 1, 2, 0, "#315952", 6)
    trace(d, 702, 249, 109, 55, 1, 2, 0, MINT, 3)
    t(d, 339, 351, "时域 · 同一段时间", 15, "#cee0d8")
    center(d, 702, 351, "二倍频   /   X : Y = 1 : 2", 16, MINT, 580)
    d.path("M848 177v174", "#51736e")
    t(d, 867, 196, "同频时的轨迹", 17, WHITE, 620)
    for y, phi, label in [(242, 0, "同相"), (313, pi / 2, "正交")]:
        d.path(f"M866 {y}h58M895 {y - 25}v50", "#77958d", 0.8)
        trace(d, 895, y, 19, 19, 1, 1, phi, GOLD, 2.1)
        t(d, 940, y + 5, label, 17, "#e0ebe4", 600)

    def node(x, width, title, detail, palette):
        d.rect(x, 434, width, 61, palette[1], palette[2], 4)
        center(d, x + width / 2, 459, title, 18, palette[0], 650)
        center(d, x + width / 2, 482, detail, 15, SLATE)

    def feedback(x1, x2, label, tone):
        # Split the return wire so there is no line behind its label.
        mid = (x1 + x2) / 2
        gap = sum(7.5 if ch.isascii() else 15 for ch in label) / 2 + 10
        d.path(f"M{x2} 495V523H{mid + gap}", tone, 1.5)
        d.path(f"M{mid - gap} 523H{x1}V498", tone, 1.5, True)
        center(d, mid, 528, label, 15, tone, 550)

    d.path("M533 393V653", RULE)
    section(d, 34, 409, "b", "有线模式 · 数字锁相", BLUE)
    for x, w, name, detail in [
        (34, 147, "ADC · I/Q 相关", "输入与本振分块相关"),
        (205, 131, "CORDIC", "求每块相角"),
        (360, 152, "48 位 DDS", "累加相位，正弦查表"),
    ]:
        node(x, w, name, detail, INDIGO)
    d.wire("M183 465h18")
    d.wire("M338 465h18")
    feedback(108, 436, "本振正交参考", BLUE)

    cx, cy = 91, 592
    d.circ(cx, cy, 36, "#f1f5f8", "#b2c5d0")
    d.path("M45 592h89M91 633v-82", "#92a9b5", 0.9)
    for a, col in [(20, BLUE), (66, GREEN)]:
        u, v = cx + 33 * cos(radians(a)), cy - 33 * sin(radians(a))
        line(d, [(cx, cy), (u, v)], col, 2.2)
        d.circ(u, v, 2.8, col)
    d.path("M110 585A20 20 0 0 0 99 574", AMBER, 1.6)
    t(d, 116, 572, "Δφ", 14, AMBER, 600)
    center(d, cx, 652, "相邻块相量", 15, SLATE)
    for i, (label, detail) in enumerate(
        [
            ("捕获", "1 kHz 粗扫 → 100 Hz 细扫"),
            ("跟踪", "块间相角差修正频率字"),
            ("调相", "相位误差修正输出偏置"),
        ]
    ):
        y = 573 + 34 * i
        t(d, 166, y, label, 17, BLUE, 650)
        t(d, 219, y, detail, 17, NAVY)

    section(d, 554, 409, "c", "无线模式 · 视觉反馈", GREEN)
    for x, w, name, detail in [
        (554, 113, "摄像头", "采集屏幕轨迹"),
        (689, 149, "Jetson Nano", "八帧融合测频"),
        (895, 151, "FPGA DDS", "更新频率与相位"),
    ]:
        node(x, w, name, detail, JADE)
    d.wire("M669 465h16")
    center(d, 866, 457, "UART", 14, GREEN, 650, "mono")
    d.wire("M841 470h49")
    feedback(610, 971, "DAC1 → 示波器 Y 轴 → 复拍", GREEN)
    for i, p in enumerate([0.15, 0.7, 1.2]):
        x = 554 + 48 * i
        d.rect(x, 566, 45, 54, "#eff5f1", "#b3ccbe", 2)
        trace(d, x + 22, 593, 17, 18, 1, 2, p, GREEN, 1.5)
    center(d, 625, 651, "连续画面示意", 15, SLATE)
    for i, (label, detail) in enumerate(
        [
            ("选档", "四档切换，提取包络折返点"),
            ("精扫", "以 100 Hz 为步长双侧判图"),
            ("调相", "改变相位后重新判读轨迹"),
        ]
    ):
        y = 573 + 34 * i
        t(d, 722, y, label, 17, GREEN, 650)
        t(d, 771, y, detail, 17, NAVY)
    footer(d, "Mizar Z7  /  XC7Z020")
    d.save("atlas-03-phase.svg")


def sobel(im):
    """Apply the base RTL's gradient decision to a grayscale photo crop, offline."""
    gray = im.convert("L")
    edge = Image.new("L", gray.size)
    g, out = gray.load(), edge.load()
    for y in range(1, gray.height - 1):
        for x in range(1, gray.width - 1):
            a, b, c = [g[x + i, y - 1] for i in [-1, 0, 1]]
            l, r = g[x - 1, y], g[x + 1, y]
            e, f, h = [g[x + i, y + 1] for i in [-1, 0, 1]]
            gx, gy = c + 2 * r + h - a - 2 * l - e, a + 2 * b + c - e - 2 * f - h
            out[x, y] = 255 if abs(gx) + abs(gy) > 80 else 0
    return edge


def vision():
    d = page(
        4,
        "Pixel stream",
        "摄像头到显示器的像素通路",
        "视频流逐像素处理，算法选择按帧提交；数字识别走独立的 RAW8 通路。",
        None,
        "竞赛实拍、三时钟域缓存、Sobel 双向梯度、模式切换和 RAW8 数字识别。",
    )
    section(d, 34, 143, "a", "竞赛工作台", BLUE)
    photo(d, "elinx-competition-demo.png", 34, 158, 245, 166)

    # Keep FIFO crossings explicit; the two output paths fork after the processing stage.
    d.rect(298, 125, 748, 199, DARK, r=5)
    t(d, 315, 155, "RGB565 视频通路", 22, WHITE, 650)
    t(d, 1026, 154, "基础版", 16, MINT, 560, "end")
    light, ink = "#cce1db", "#ebf5ee"
    for x, width, clock in [(315, 164, "CAM_PCLK"), (501, 174, "clk_sdram"), (697, 151, "clk_hdmi")]:
        d.path(f"M{x} 170h{width}", "#688782")
        t(d, x, 190, clock, 15, MINT, 600, cls="mono")
    t(d, 315, 220, "OV5640", 21, ink, 650)
    for i in range(16):
        d.rect(
            315 + i * 8,
            232,
            7,
            15,
            ("#d79380", "#83be9e", "#83aacc")[0 if i < 5 else 1 if i < 11 else 2],
            r=1,
        )
    for x, txt in [(333, "R5"), (377, "G6"), (421, "B5")]:
        center(d, x, 266, txt, 14, light, 600, "mono")
    for x, label in [(472, "写 FIFO"), (680, "读 FIFO")]:
        for j in range(4):
            d.rect(x - 14 + 7 * j, 231, 5, 16, "#b7d1c3" if j < 3 else "#4e716d", r=1)
        center(d, x, 292, label, 15, GOLD, 580)
    for x, end in [(444, 456), (488, 510), (647, 663), (696, 710), (829, 855)]:
        d.path(f"M{x} 239H{end - 4}", light, 1.3)
        poly(d, [(end - 5, 236), (end, 239), (end - 5, 242)], light)
    for j, col in enumerate(["#426268", "#57787b", "#dce9e4"]):
        d.rect(513 + j * 3, 217 - j * 3, 125, 49, col, "#83a29c", 3)
    center(d, 581, 242, "SDRAM", 21, DARK, 670, "mono")
    center(d, 581, 292, "突发读写", 15, light, 550)
    d.rect(713, 213, 116, 51, "#284e50", "#83a99c", 3)
    center(d, 771, 246, "像素算子", 19, WHITE, 650)
    center(d, 771, 292, "模式选择", 15, light, 550)
    d.path("M858 239V211H874 M858 239V269H874", MINT, 1.7)
    d.circ(858, 239, 3, MINT)
    for y, title, sub in [(211, "HDMI", "本地扫描输出"), (269, "UDP → PyQt6", "上位机按帧重组")]:
        t(d, 881, y + 4, title, 19, WHITE, 650)
        t(d, 881, y + 26, sub, 15, light)

    d.path("M34 342H1046 M553 358V539", RULE)
    section(d, 34, 375, "b", "Sobel · 从邻域到边缘", BLUE)
    with Image.open(ASSETS / "elinx-competition-demo.png") as im:
        patch = im.crop((58, 143, 242, 266))
        for x, pic in [(34, patch), (405, sobel(patch))]:
            embed(d, encode(pic, (256, 170), quality=96), x, 393, 128, 85)
    for x, kernel, label in [
        (184, ((-1, 0, 1), (-2, 0, 2), (-1, 0, 1)), "Gx"),
        (290, ((1, 2, 1), (0, 0, 0), (-1, -2, -1)), "Gy"),
    ]:
        for row, coeffs in enumerate(kernel):
            for col, v in enumerate(coeffs):
                xx, yy = x + col * 25, 398 + row * 25
                d.rect(xx, yy, 24, 24, INDIGO[1] if v < 0 else "#f1f3ee" if v == 0 else "#d7eade", r=1)
                center(d, xx + 12, yy + 17, str(v), 15, BLUE if v < 0 else GREEN, 600, "mono")
        center(d, x + 37, 502, label, 16, BLUE, 640, "mono")
    d.wire("M165 436h14")
    d.wire("M369 436h30")
    center(d, 98, 502, "实拍屏幕裁片", 15, SLATE)
    center(d, 469, 502, "离线二值结果", 15, SLATE)
    t(d, 34, 535, "行缓存 → 3 × 3 窗口", 17, NAVY, 600)
    t(d, 534, 535, "|Gx| + |Gy| > 80 判为边缘", 16, BLUE, 620, "end")

    section(d, 573, 375, "c", "算法切换 · 只在帧首生效", GREEN)
    t(d, 573, 411, "串口命令", 16, NAVY, 630)
    for j, byte in enumerate(["AA", "0A", "00", "55"]):
        x = 656 + 38 * j
        d.rect(x, 390, 34, 27, JADE[1] if j in (1, 2) else PALE, r=2)
        center(d, x + 17, 409, byte, 16, GREEN if j in (1, 2) else SLATE, 650, "mono")
    t(d, 824, 410, "Sobel  /  1 Mbaud", 16, SLATE, 550)
    for y, label in [(448, "跨域握手"), (478, "等待帧首"), (510, "当前算法")]:
        t(d, 573, y, label, 16, SLATE)
    d.path("M663 445H721V431H745V445H1034", BLUE, 2)
    d.path("M663 475H745V460H864V475H1034", AMBER, 2)
    d.path("M864 426V513", GREEN, 1.3, False, True)
    for x, w, label, pal in [(663, 201, "原模式", INDIGO), (865, 169, "Sobel", JADE)]:
        d.rect(x, 488, w, 29, pal[1], pal[2], 2)
        center(d, x + w / 2, 508, label, 16, pal[0], 650)
    t(d, 864, 538, "↑ 帧同步边界", 15, GREEN, 600)

    d.path("M34 554H1046", RULE)
    section(d, 34, 586, "d", "独立 CNN · RAW8 数字识别", BLUE)
    # One archived camera frame, not a predicted label or a classifier benchmark.
    t(d, 1046, 585, "独立输入，不串入 HDMI / UDP 主通路", 15, SLATE, 520, "end")
    d.rect(34, 604, 346, 91, PALE, r=4)
    with Image.open(OUT / "vision-density-3.png") as density:
        # Preserve the 32×32 cell edges. Maximum density code is (20×16) >> 3 = 40.
        heatmap = ImageOps.colorize(density, "#e3eae4", "#1f5d4f", whitepoint=40)
        buf = BytesIO()
        heatmap.save(buf, "PNG", optimize=True)
        data = base64.b64encode(buf.getvalue()).decode("ascii")
        d.el.append(
            f'<image x="47" y="617" width="64" height="64" style="image-rendering:pixelated" href="data:image/png;base64,{data}"/>'
        )
    t(d, 124, 633, "32 × 32 特征图", 19, GREEN, 650)
    t(d, 124, 658, "实采 ROI · 每格 20 × 16 像素", 15, SLATE)
    t(d, 124, 681, "75 MHz · 统计暗像素密度", 15, SLATE)
    for x, w, title, detail, pal in [
        (461, 227, "定点 CNN", "25 MHz · 卷积与全连接", INDIGO),
        (782, 264, "识别结果稳定化", "连续三次一致，在帧首更新", JADE),
    ]:
        d.rect(x, 604, w, 91, pal[1], pal[2], 4)
        center(d, x + w / 2, 645, title, 20, pal[0], 650)
        center(d, x + w / 2, 673, detail, 16, SLATE)
    for x, w, cap in [(382, 75, "特征 FIFO"), (691, 87, "返回 FIFO")]:
        center(d, x + w / 2, 641, cap, 14, SLATE, 550)
        d.wire(f"M{x} 654h{w}")
    d.save("atlas-04-vision.svg")


# Nominal local centres in millimetres; see generate_n60_csv.py at the pinned
# N60 revision in ASSETS.md. The perspective is for legibility, not metrology.
N12 = [
    (0, 0),
    (14.280, 10.958),
    (-10.958, 14.280),
    (-14.280, -10.958),
    (10.958, -14.280),
    (35.097, 8.011),
    (15.620, 32.435),
    (-15.620, 32.435),
    (-35.097, 8.011),
    (-28.146, -22.446),
    (0, -36),
    (28.146, -22.446),
]
MODULES = [-45, -22.5, 0, 22.5, 45]


def n60():
    d = page(
        5,
        "N60 array",
        "五个子阵，六十路输出",
        "上位机逐阵元计算相位与幅度，FPGA 将同一音频调制为 60 路 PWM。",
        None,
        "工作台实拍、子阵安装角和通道编号、串口参数帧与音频通路；三行示意波形对照相移与脉宽。",
    )
    section(d, 34, 143, "a", "阵列实物", BLUE)
    photo(d, "n60-hardware.jpg", 34, 158, 250, 164, (0, 0, 1600, 1048))
    d.rect(34, 329, 250, 51, PALE, r=3)
    photo(d, "n60-hardware.jpg", 39, 333, 69, 43, (545, 25, 1005, 315))
    t(d, 119, 351, "FPGA 控制板", 17, BLUE, 650)
    t(d, 119, 371, "排线连接阵列驱动级", 15, SLATE)

    d.rect(302, 125, 744, 255, "#f0f5f3", r=5)
    t(d, 320, 155, "阵元布局与通道分组", 22, GREEN, 650)
    t(d, 1027, 154, "5 个子阵 × 12 阵元", 17, GREEN, 600, "end")
    accents = ["#44698a", "#4b7c87", "#2b7365", "#63794e", "#906a40"]
    face = ["#dbe5ec", "#d9e6e8", "#d9e8e0", "#e2e8d8", "#eee3d6"]

    def pt(theta, lx, ly, depth=0):
        a = radians(theta)
        x = 176.445 * sin(a) + lx * cos(a) + depth * sin(a)
        z = -176.445 * cos(a) + lx * sin(a) - depth * cos(a)
        return 674 + 1.93 * x, 220 - 1.02 * ly + 0.59 * (z + 176.445)

    line(d, [pt(a, 0, -40) for a in range(-51, 52)], "#b9c9c1", 3)
    for i in [2, 1, 3, 0, 4]:
        a = MODULES[i]
        col = accents[i]

        def disc(cx, cy, r, depth, theta=a):
            count = 56 if r > 8 else 18
            return [
                pt(theta, cx + r * cos(th * 2 * pi / count), cy + r * sin(th * 2 * pi / count), depth)
                for th in range(count)
            ]

        poly(d, disc(0, 0, 44, 7), "#acbcb5", col)
        poly(d, disc(0, 0, 44, 0), face[i], col)
        for lx, ly in sorted(N12, key=lambda v: -v[1]):
            poly(d, disc(lx, ly, 6.2, 0), "#71857c")
            poly(d, disc(lx, ly, 6.1, -5), "#f4f5ee", "#7e9388", 0.8)
            poly(d, disc(lx, ly, 4.2, -5), "#344c49")
            poly(d, disc(lx, ly, 2.5, -5), "#627772")
        u, v = pt(a, 0, -45)
        d.path(f"M{u} {v}V307", col, 1)
        d.circ(u, 307, 2.9, col)
        center(d, u, 332, f"U{i}  /  {a:g}°", 16, col, 650, "mono")
        center(d, u, 355, f"CH {12 * i:02d}–{12 * i + 11:02d}", 15, SLATE, 530, "mono")

    d.path("M34 396H1046", RULE)
    section(d, 34, 427, "b", "上位机 · 逐通道参数下发", BLUE)
    t(d, 603, 425, "UART  /  115200 baud", 15, SLATE, 570, "end", "mono")
    t(d, 34, 457, "路径差 → 相位刻度", 18, BLUE, 640)
    d.path("M238 442v18", RULE)
    t(d, 257, 457, "阵元朝向与目标方向 → 幅度权重", 18, GREEN, 640)
    fields = [
        (34, 100, "帧头与指令", "AA BB 01", INDIGO),
        (138, 115, "幅度", "60 × 1 B", JADE),
        (257, 135, "相位 · 小端", "60 × 2 B", INDIGO),
        (396, 91, "累加校验", "1 B", OCHRE),
        (491, 112, "帧尾", "0D 0A", INDIGO),
    ]
    for x, w, title, value, pal in fields:
        d.rect(x, 473, w, 55, pal[1], pal[2], 3)
        center(d, x + w / 2, 494, title, 15, pal[0], 630)
        center(d, x + w / 2, 516, value, 16, NAVY, 600, "mono")
    t(d, 34, 555, "校验和与帧尾均正确后，FPGA 一次更新 60 组参数。", 16, SLATE)

    d.path("M34 575H603", RULE)
    section(d, 34, 606, "c", "音频 · 从采样到占空比", GREEN)
    for x, w, head, note, pal in [
        (34, 158, "WM8978 / I²S", "16 位左声道采样", OCHRE),
        (213, 153, "音频预处理", "噪声门、增益、限幅", JADE),
        (389, 214, "平方根 ROM 映射", "基础脉宽 × 通道幅度", INDIGO),
    ]:
        d.rect(x, 627, w, 64, pal[1], pal[2], 3)
        center(d, x + w / 2, 654, head, 18, pal[0], 640)
        center(d, x + w / 2, 679, note, 15, SLATE)
    d.wire("M194 659h15")
    d.wire("M369 659h16")

    # Shared time axis: B changes center relative to A; C changes only width relative to B.
    d.rect(626, 412, 420, 279, DARK, r=5)
    t(d, 645, 446, "PWM · 脉冲中心与宽度", 22, WHITE, 650)
    t(d, 1027, 445, "时序示意", 15, MINT, 560, "end")
    t(d, 645, 474, "40 kHz", 18, GOLD, 640, cls="mono")
    t(d, 1026, 474, "100 MHz 时钟 / 每周期 2500 拍", 15, "#cfdfd9", 530, "end")
    left, period = 745, 132
    grid(d, left, 490, 2 * period, 141, 33, 24, "#365959")
    for x in [left, left + period, left + 2 * period]:
        d.path(f"M{x} 488V634", "#708d84", 1, False, True)
    for y, offset, width, title, tone in [
        (525, 40, 40, "A  参考", MINT),
        (573, 74, 40, "B  移相", GOLD),
        (621, 74, 20, "C  缩窄", "#a8c9e0"),
    ]:
        t(d, 645, y - 3, title, 17, tone, 570)
        points = [(left, y)]
        for k in range(2):
            mid = left + k * period + offset
            u, v = mid - width / 2, mid + width / 2
            points.extend([(u, y), (u, y - 20), (v, y - 20), (v, y)])
            d.circ(mid, y - 20, 2.6, tone)
        points.append((left + 2 * period, y))
        line(d, points, tone, 2)
    for x in [left + 74, left + period + 74]:
        d.path(f"M{x} 555v42", "#b0c9ba", 1, False, True)
    d.path(f"M{left} 641v5h{period}v-5", "#91afa4", 1.2)
    center(d, left + period / 2, 670, "一个周期 · 25 μs", 16, MINT, 580)
    d.save("atlas-05-array.svg")


def ct():
    d = page(
        7,
        "ConeFDK",
        "CUDA 锥束反投影与逐层核对",
        "720 幅 X 射线投影 → 512³ 体素；以 ASTRA 为参考，逐层核对同一颗核桃的重建强度。",
        None,
        "真实核桃的三个正交断面；锥束射线穿过同一列体素，在探测器上做双线性插值；下方为 CUDA 与 ASTRA 的 512 层强度差。",
    )
    section(d, 34, 144, "a", "同一颗核桃的三个断面", BLUE)
    d.rect(34, 156, 352, 247, "#101315", r=3)
    with Image.open(ASSETS / "conefdk-sweep.gif") as im:
        im.seek(12)
        data = encode(im, (276, 276), quality=93)
    (OUT / "atlas-07-still.webp").write_bytes(data)
    embed(d, data, 95, 164, 230, 230)
    t(d, 43, 183, "XY", 17, "#a5c8bb", 600, cls="mono")
    t(d, 43, 206, "轴向", 15, "#c0d2d1")
    for x, tag, name, crop in [
        (34, "XZ", "冠状", (310, 34, 620, 344)), (213, "YZ", "矢状", (620, 34, 930, 344))
    ]:
        d.rect(x, 409, 173, 102, "#16242b", r=3)
        photo(d, "conefdk-walnut.png", x + 61, 411, 98, 98, crop)
        t(d, x + 10, 437, tag, 17, "#a5c8bb", 600, cls="mono")
        t(d, x + 10, 461, name, 15, "#c0d2d1")
    section(d, 406, 144, "b", "一个线程如何更新一列体素", GREEN)
    # Annotate the fixed view and column, not the moving axial image.
    t(d, 414, 181, "单个投影角 θ", 17, NAVY, 630)
    t(d, 414, 205, "探测器列 u 不变，行 v 随 z 改变。", 15, SLATE)
    # Perspective projection: a source, a volume and a gridded detector.
    src = (443, 292)
    tl, tr, br, bl = (826, 184), (930, 210), (930, 393), (826, 367)
    for face, c in [([src, tl, tr], "#edf1e9"), ([src, tl, bl], "#f8f1dc"), ([src, tr, br], "#f3ead5")]:
        poly(d, face, c)
    poly(d, [tl, tr, br, bl], "#dfede8", "#729287", 1.4)
    for i in range(1, 8):
        q = i / 8
        line(d, [(826 + 104 * q, 184 + 26 * q), (826 + 104 * q, 367 + 26 * q)], "#9bb9b0", 0.8)
    for i in range(1, 13):
        q = i / 13
        line(d, [(826, 184 + 183 * q), (930, 210 + 183 * q)], "#9bb9b0", 0.8)
    line(d, [tl, src, bl], "#ccb384", 1.1)
    line(d, [src, br], "#d3bd93", 0.9)
    x, y = 626, 251
    front = [(x, y), (x + 73, y + 15), (x + 73, y + 100), (x, y + 85)]
    poly(d, front, "#d5e6e4", "#739995")
    poly(d, [front[0], (649, 229), (722, 244), front[1]], "#eff5f2", "#8baba4")
    poly(d, [front[1], (722, 244), (722, 328), front[2]], "#adcbc5", "#799f97")
    for k in range(1, 5):
        q = k / 5
        line(d, [(x + q * 73, y + q * 15), (x + q * 73, y + q * 15 + 85)], "#9ab6af", 0.9)
        line(d, [(x, y + q * 85), (x + 73, y + q * 85 + 15)], "#a2beb8", 0.8)
    poly(d, [(654, 257), (665, 259), (665, 344), (654, 342)], "#448a77", GREEN)
    for j in range(1, 9):
        d.path(f"M654 {257 + 9.5 * j}l11 2", "#c2ddd2", 0.7)
    # Two sample rays from the same x/y column, at different heights.
    # Both voxel heights land on the same detector column for this view.
    d.path("M867 239v116", GREEN, 1.2, False, True)
    for vy in [268, 321]:
        uv = 867
        dy = 292 + (vy - 292) * (uv - 443) / (660 - 443)
        line(d, [src, (uv, dy)], "#a06937", 1.15, False, True)
        d.circ(660, vy, 3.2, AMBER)
        d.circ(uv, dy, 3.2, AMBER)
    d.circ(*src, 5, AMBER)
    t(d, 418, 321, "射线源", 16, AMBER, 620)
    d.path("M660 346v12h-40", GREEN, 1.2)
    t(d, 550, 380, "固定 (x, y) · 共享几何权重", 16, GREEN, 620)
    t(d, 939, 346, "探测器平面", 16, GREEN, 620)
    # Detail of the four detector samples bracketing one projected point.
    d.path("M870 245h61l18-29h12", AMBER, 1, False, True)
    d.rect(961, 181, 76, 77, "#f7faf7", RULE, 2)
    d.rect(970, 190, 29, 29, "#e6efe5")
    grid(d, 970, 190, 58, 58, 29, 29, "#b1c6be")
    for xx in (970, 999):
        for yy in (190, 219):
            d.circ(xx, yy, 3.1, GREEN)
    d.path("M970 208h29M988 190v29", AMBER, 0.9, False, True)
    d.circ(988, 208, 3.0, AMBER)
    center(d, 997, 281, "四邻点", 16, GREEN, 610)
    center(d, 997, 303, "双线性插值", 15, SLATE)
    # Each glyph depicts an operation rather than a measured intensity profile.
    # Left: a selected detector row and its padded tail. Middle: the ramp in
    # frequency space. Right: one thread updating successive z positions.
    d.rect(406, 407, 640, 104, DARK, r=4)
    for x in (617, 835):
        d.path(f"M{x} 421v75", "#51736e", 1)
    for x, name, note in [
        (420, "逐行加权", "几何加权，行尾补零"),
        (632, "cuFFT 滤波", "频域乘 Ram-Lak，再逆变换"),
        (850, "按列反投影", "每线程更新至多 16 个体素"),
    ]:
        t(d, x + 49, 447, name, 18, WHITE, 630)
        t(d, x, 488, note, 15, "#d2e2d8")
    for j in range(3):
        for i in range(6):
            d.rect(420 + i * 6, 429 + j * 6, 5, 5,
                   (GOLD if i < 4 else "#82958e") if j == 1 else "#43645f")
    d.path("M632 429v23h38", "#829e93", 1)
    d.path("M634 431l15 18 18-18", GOLD, 2.2)
    for j in range(4):
        d.rect(852, 423 + j * 7, 14, 6, MINT if j in (0, 3) else "#74a997")
    d.path("M874 423v27m-3-4 3 4 3-4", GOLD, 1.4)
    d.path("M34 528H1046", RULE)
    section(d, 34, 562, "c", "CUDA 与 ASTRA 的强度差", BLUE)
    t(d, 34, 636, "0.02899%", 51, GREEN, 660, cls="serif")
    t(d, 36, 670, "整卷相对 L2 差异", 19, NAVY, 610)
    t(d, 36, 695, "同一组投影 · 全部 512³ 个体素", 16, SLATE)
    x0, x1, y0, y1 = 443, 1023, 588, 659
    root = ET.parse(ASSETS / "conefdk-walnut-peak.svg")
    raw = next(n.get("points") for n in root.iter() if n.tag.endswith("polyline")).split()
    assert len(raw) == 512
    points = []
    for pair in raw:
        u, v = map(float, pair.split(","))
        points.append((x0 + (u - 54) / 450 * (x1 - x0), y1 - (130 - v) / 94 * (y1 - y0)))
    t(d, 443, 562, "逐层最大绝对强度差", 19, NAVY, 630)
    t(d, 1023, 562, "首个峰值：z = 256", 16, AMBER, 630, "end")
    for yy in [y0, (y0 + y1) / 2, y1]:
        d.path(f"M{x0} {yy}H{x1}", RULE, 1, False, True)
    poly(d, [(x0, y1), *points, (x1, y1)], "#e7f0f3")
    line(d, points, BLUE, 1.5)
    px, py = points[256]
    d.path(f"M{px} {py}V{y1}", AMBER, 1.1, False, True)
    d.circ(px, py, 4, AMBER)
    for xx, s in [(x0, "0"), (px, "256"), (x1, "511")]:
        center(d, xx, 681, s, 14, SLATE, 550, "mono")
    t(d, 431, y0 + 5, "4.74e−5", 14, SLATE, 500, "end", "mono")
    t(d, 431, y1 + 4, "0", 14, SLATE, 500, "end", "mono")
    center(d, (x0 + x1) / 2, 704, "轴向层号 z", 14, SLATE)
    meta(
        d,
        "Source: Alexander Meaney, University of Helsinki, https://doi.org/10.5281/zenodo.6986012 ; CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ . Projections binned, normalized and reconstructed. The chart preserves all 512 measurements.",
    )
    d.save("atlas-07-ct.svg")


def rocket():
    d = page(
        9,
        "Rocket / RV64GC",
        "从 FPGA 配置到 BusyBox 应答",
        "两条线连接 VCU118：J106 配置逻辑，J4 串口传送固件并接收 shell 回答。",
        "Board bring-up",
        "板上验收字段、五级 Rocket 与软件启动路径示意；同一板卡与 bitstream 的两次串口启动计时。",
    )
    section(d, 34, 146, "a", "实板验收记录", BLUE)
    d.rect(34, 166, 300, 236, DARK, r=4)
    t(d, 49, 195, "linux-oscheck", 21, WHITE, 620, cls="mono")
    d.path("M49 207H320", "#486363")
    t(d, 51, 235, "SLR", 15, "#b5c9c6", 550, cls="mono")
    for j in range(3):
        center(d, 224 + j * 40, 235, str(j), 16, "#b9cec6", 550, "mono")
    for i, (name, val) in enumerate([("DONE", "1"), ("CRC_ERROR", "0")]):
        yy = 260 + 34 * i
        t(d, 51, yy + 5, name, 17, "#eff4e9", 560, cls="mono")
        for j in range(3):
            xx = 224 + 40 * j
            d.rect(xx - 13, yy - 15, 26, 25, "#2a5351", "#53827a", 2)
            center(d, xx, yy + 4, val, 16, MINT, 650, "mono")
    d.path("M49 312H320", "#486363")
    t(d, 50, 340, "UART", 16, "#d5e2dc", 520, cls="mono")
    t(d, 317, 340, "115200 8N1", 17, MINT, 600, "end", "mono")
    t(d, 51, 374, "shell 命令应答", 16, "#d5e2dc")
    t(d, 317, 374, "verified", 17, MINT, 600, "end", "mono")
    section(d, 356, 146, "b", "配置与执行路径", GREEN)
    # Functional board schematic, not a photograph or device floorplan.
    d.rect(355, 167, 691, 236, "#edf4ef", "#adc6ba", 9)
    for xx in [367, 1033]:
        for yy in [180, 390]:
            d.circ(xx, yy, 4.2, "#fafcfa", "#a8bbb2")
            d.circ(xx, yy, 1.4, "#a1b5aa")
    t(d, 376, 194, "VCU118   /   功能示意", 17, GREEN, 600)
    t(d, 1019, 194, "RV64GC · 100 MHz", 17, GREEN, 620, "end", "mono")
    for yy, key, label in [(231, "J106", "JTAG 配置"), (304, "J4", "UART 收发")]:
        d.rect(375, yy, 97, 49, "#d9e5df", "#90a99b", 3)
        t(d, 383, yy + 20, key, 17, NAVY, 650, cls="mono")
        t(d, 383, yy + 41, label, 14, SLATE)
    d.wire("M473 254h30v-45h41")
    t(d, 548, 205, "配置逻辑", 13, SLATE)
    d.wire("M473 329h32v14h34")
    d.rect(543, 216, 333, 151, "#c1d7ca", "#8aaf99", 4)
    d.rect(550, 222, 320, 139, "#fbfcf7", "#95af9c", 3)
    t(d, 565, 251, "Rocket 单核", 22, GREEN, 650)
    t(d, 853, 249, "五级流水", 16, SLATE, 550, "end")
    for j, (name, note) in enumerate(
        [("IF", "取指"), ("ID", "译码"), ("EX", "执行"), ("MEM", "访存"), ("WB", "写回")]
    ):
        xx = 560 + j * 60
        poly(
            d,
            [(xx, 270), (xx + 49, 270), (xx + 55, 289), (xx + 49, 309), (xx, 309), (xx + 5, 289)],
            ["#dbe9ed", "#d6e8e5", "#c2ded1", "#d6e8e5", "#e2ebdc"][j],
        )
        center(d, xx + 27, 295, name, 17, GREEN, 650, "mono")
        center(d, xx + 27, 339, note, 15, SLATE)
    for i in range(13):
        xx = 564 + i * 24
        d.path(f"M{xx} 211v5m0 151v5", "#839e8d", 1.7)
    for yy, dev in [(242, "Boot ROM"), (313, "DDR4")]:
        d.rect(914, yy, 107, 45, "#dce5db", "#95aa93", 2)
        center(d, 967, yy + 29, dev, 16, GREEN, 620, "mono")
        d.path(f"M877 {yy + 22}h37", "#90a797", 1.4)
    t(d, 1019, 389, "功能连接，不表示器件物理布局。", 14, SLATE, 500, "end")
    section(d, 34, 443, "c", "启动中的控制权交接", GREEN)
    for i, (u, v, xx) in enumerate(
        [
            ("复位 / Boot ROM", "J4 接收固件", 52),
            ("DDR4", "装载到内存", 281),
            ("OpenSBI", "移交内核", 512),
            ("Linux 6.6.65", "启动用户态", 708),
            ("BusyBox", "shell 应答", 932),
        ]
    ):
        d.circ(xx, 470, 4.5, GREEN if i < 4 else AMBER)
        t(d, xx, 498, u, 20, NAVY, 650)
        t(d, xx, 522, v, 15, SLATE)
        if i < 4:
            d.wire(f"M{xx + 6} 470H{[281, 512, 708, 932][i] - 8}")
    d.path("M34 538H1046", RULE)
    section(d, 34, 572, "d", "相同固件，两种串口传法", BLUE)
    for i, (title, bytes_, sec, p) in enumerate(
        [("原始", "5,341,704 B", 495.050, INDIGO), ("自解压", "2,018,528 B", 194.469, JADE)]
    ):
        yy = 595 + 39 * i
        t(d, 35, yy + 18, title, 18, p[0], 620)
        t(d, 117, yy + 18, bytes_, 16, SLATE, 500, cls="mono")
        length = 397 * sec / 495.050
        d.rect(267, yy, 397, 22, "#edf1ee", r=2)
        d.rect(267, yy, length, 22, p[0], r=2)
        t(d, 680, yy + 18, f"{sec:.3f} s", 18, p[0], 650, cls="mono")
    d.path("M804 581v73", RULE)
    t(d, 821, 606, "计时起点：J4 发送", 17, SLATE)
    t(d, 821, 643, "终点：shell 正确应答", 17, SLATE)
    footer(
        d,
        "同板、同一 bitstream；计时不含 JTAG 配置。",
        "左上为 JSON 字段摘录；下方为独立的一对启动记录。",
    )
    meta(
        d,
        "Hardware acceptance excerpt: https://github.com/EtherealBian/vcu118-rocket-soc/blob/5862e904c97ca7648daaa45c04587dbfe4fa081f/docs/portable-linux-rocket-boot.json ; see work/vcu118-rocket.html for the separate paired measurements.",
    )
    d.save("atlas-09-rocket.svg")


if __name__ == "__main__":
    for draw in [phase, vision, n60, ct, rocket]:
        draw()
