"""Draw the five detailed catalog plates from archived project evidence (Pillow).

Run: python -B tools/draw_project_covers.py. The UAV and compiler covers are
independent originals, deliberately not generated here. Sources: ../ASSETS.md.
"""

import base64
import xml.etree.ElementTree as ET
from html import escape
from io import BytesIO
from math import cos, hypot, pi, radians, sin

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
    t(d, 1046, 91, f"{series}   /   {n:02d}", 15, GREEN, 600, "end", "mono")
    d.path("M34 110H1046", NAVY, 1.6)
    return d


def section(d, x, y, letter, title, tone=GREEN):
    d.rect(x, y - 18, 24, 24, tone, r=3)
    center(d, x + 12, y, letter, 18, WHITE, 650, "serif")
    t(d, x + 35, y + 1, title, 21, tone, 650)


def footer(d, left, right):
    d.path("M34 677H1046", RULE)
    t(d, 34, 703, left, 15, SLATE)
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
        "从正交采样到李萨如轨迹",
        "有线路径用相角校正 DDS；视觉路径从连续画面估计频率与相位。",
        "Phase tracking",
        "竞赛工作台和示波器实拍；相量、两轴波形与李萨如轨迹均为原理示意。",
    )
    section(d, 34, 145, "a", "竞赛工作台", BLUE)
    photo(d, "lissajous-hardware.jpg", 34, 164, 278, 174, (0, 0, 1706, 1135))
    # The magnified screen is the actual screen area in the source photograph.
    d.rect(34, 343, 278, 79, "#eff3f4")
    photo(d, "lissajous-hardware.jpg", 41, 349, 113, 67, (853, 95, 1138, 260))
    t(d, 166, 375, "示波器实拍", 17, BLUE, 650)
    t(d, 166, 403, "双环轨迹局部", 15, SLATE)
    d.rect(331, 128, 715, 294, DARK, r=5)
    grid(d, 351, 182, 674, 206, 26, 26, "#35585b")
    t(d, 355, 160, "X–Y 显示原理", 22, WHITE, 630)
    t(d, 1021, 159, "频率比   1 : 2", 18, MINT, 600, "end")
    # Parametric time-domain components and the corresponding XY trajectory.
    for i, (axis, f, col) in enumerate([("X", 1, GOLD), ("Y", 2, MINT)]):
        yy = 235 + 93 * i
        t(d, 357, yy + 6, axis, 23, col, 650, cls="serif")
        d.path(f"M386 {yy}h195", "#70918d", 0.9)
        line(d, [(388 + j * 1.06, yy - 24 * sin(2 * pi * f * j / 180)) for j in range(181)], col, 2.7)
    d.path("M595 235h13v49h28m-41 44h13v-44", "#9cb3ab", 1.4)
    poly(d, [(635, 280), (643, 284), (635, 288)], MINT)
    d.path("M665 284h332M830 191v185", "#819d98", 1)
    trace(d, 830, 284, 145, 79, 1, 2, 0, "#315952", 6)
    trace(d, 830, 284, 145, 79, 1, 2, 0, MINT, 3)
    t(d, 355, 407, "X：原始输入     Y：DDS 合成", 16, "#cee0d8")
    t(d, 1021, 406, "理论轨迹 · 非采样数据", 15, "#bed4cf", 500, "end")
    section(d, 34, 463, "b", "有线锁相：区分频偏和相位误差", BLUE)
    cx, cy = 118, 558
    d.circ(cx, cy, 59, "#eff4f7", "#aac0cd")
    d.path("M47 558h142M118 490v137", "#96adba", 1)
    for a, col in [(22, BLUE), (64, GREEN)]:
        u, v = cx + 55 * cos(radians(a)), cy - 55 * sin(radians(a))
        line(d, [(cx, cy), (u, v)], col, 2.6)
        d.circ(u, v, 3.6, col)
    d.path("M147 546A32 32 0 0 0 132 529", AMBER, 2)
    t(d, 147, 529, "Δφ", 14, AMBER, 650)
    t(d, 176, 551, "I", 15, SLATE)
    t(d, 124, 497, "Q", 15, SLATE)
    center(d, 118, 646, "相邻采样块的相量", 15, SLATE)
    for i, (label, detail) in enumerate(
        [
            ("I/Q 相关", "由同相、正交分量求块相角"),
            ("相邻块相角差", "估计频偏，先粗扫后细扫"),
            ("绝对相位误差", "校正相位，驱动 48 位 DDS"),
        ]
    ):
        yy = 500 + 57 * i
        d.circ(223, yy - 4, 4, [BLUE, GREEN, AMBER][i])
        t(d, 239, yy, label, 18, NAVY, 640)
        t(d, 239, yy + 23, detail, 16, SLATE)
        if i < 2:
            d.path(f"M223 {yy + 2}v47", RULE, 1.3)
    d.path("M560 446V655", RULE)
    section(d, 586, 463, "c", "视觉估计：从多帧轨迹回推参数", GREEN)
    for i, p in enumerate([0.18, 0.65, 1.13]):
        xx = 588 + 101 * i
        d.rect(xx, 495, 87, 61, "#eef5f1", "#b3ccbe", 2)
        trace(d, xx + 43, 525, 32, 21, 1, 2, p, GREEN, 1.6)
        center(d, xx + 43, 579, ["t − 2", "t − 1", "t"][i], 15, SLATE, 520, "mono")
    d.wire("M877 525h35")
    t(d, 926, 522, "Jetson", 21, GREEN, 650)
    t(d, 926, 547, "Nano", 20, GREEN, 650)
    t(d, 587, 612, "多帧图像估计频率与相位", 20, NAVY, 600)
    t(d, 587, 643, "经 UART 更新视觉方案的 DDS 控制字。", 17, SLATE)
    footer(d, "平台：Mizar Z7 / XC7Z020", "相量与多帧图形为示意；左上两幅来自同一张实拍。")
    d.save("atlas-03-phase.svg")


def sobel(im):
    """Sobel magnitude of the *same* photographed subject, not a board capture."""
    gray = im.convert("L")
    out = Image.new("L", gray.size)
    g = gray.load()
    dest = out.load()
    for y in range(1, gray.height - 1):
        for x in range(1, gray.width - 1):
            a, b, c = [g[x + i, y - 1] for i in [-1, 0, 1]]
            l, r = g[x - 1, y], g[x + 1, y]
            e, f, h = [g[x + i, y + 1] for i in [-1, 0, 1]]
            dest[x, y] = min(
                255, round(hypot(c + 2 * r + h - a - 2 * l - e, e + 2 * f + h - a - 2 * b - c))
            )
    return ImageOps.colorize(out, "#102d36", "#dcf4d8")


def vision():
    d = page(
        4,
        "Pixel stream",
        "摄像头到显示器的像素通路",
        "采集侧写帧，显示侧读帧；控制字跨时钟域，在下一帧开头提交。",
        "FPGA video",
        "实拍与同一区域的 Sobel 离线示意；RGB565、帧缓存、双路输出和换帧控制。",
    )
    section(d, 34, 145, "a", "采集与缓存", BLUE)
    photo(d, "elinx-competition-demo.png", 34, 164, 256, 165)
    t(d, 34, 356, "竞赛现场：开发板与显示端", 17, SLATE)
    t(d, 324, 185, "OV5640", 28, BLUE, 650, cls="serif")
    t(d, 324, 210, "一个 RGB565 像素 / 16 bit", 16, SLATE)
    for i in range(16):
        k = 0 if i < 5 else 1 if i < 11 else 2
        d.rect(324 + i * 12, 232, 11, 25, ("#b65e4e", "#438573", "#557d99")[k])
    for x, s in [(354, "R · 5"), (420, "G · 6"), (486, "B · 5")]:
        center(d, x, 278, s, 15, SLATE, 600, "mono")
    d.wire("M525 243h40")
    for j in range(3):
        xx, yy = 580 + 5 * j, 219 - 8 * j
        d.rect(xx, yy, 150, 65, ["#b0bfc8", "#d5e1e6", "#edf2f4"][j], "#91a8b5", 2)
    center(d, 665, 236, "SDRAM", 23, NAVY, 650, "serif")
    center(d, 665, 259, "帧缓存", 15, SLATE)
    d.wire("M746 236h35")
    d.rect(787, 205, 244, 59, JADE[1], JADE[2], 3)
    center(d, 909, 242, "显示时钟域 · 像素算子", 19, GREEN, 650)
    d.path("M908 264v20H802v12m106-12h83v12", GREEN, 1.5)
    d.circ(908, 284, 3, GREEN)
    center(d, 802, 318, "HDMI 直显", 18, GREEN, 630)
    center(d, 982, 318, "UDP / PyQt6", 17, AMBER, 630)
    t(d, 324, 351, "相机域写入", 16, SLATE)
    t(d, 585, 351, "跨域缓冲", 16, SLATE)
    t(d, 787, 351, "基础版 UDP：1024 × 600", 17, SLATE)
    d.path("M34 375H1046", RULE)
    section(d, 34, 412, "b", "同一画面：3 × 3 Sobel 边缘检测", BLUE)
    with Image.open(ASSETS / "elinx-competition-demo.png") as im:
        patch = im.crop((58, 143, 242, 266))
        edge = sobel(patch)
        for xx, pic in [(34, patch), (378, edge)]:
            embed(d, encode(pic, (336, 224), quality=92), xx, 443, 168, 112)
    for j in range(3):
        for i in range(3):
            val = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]][j][i]
            xx, yy = 241 + 30 * i, 449 + 30 * j
            d.rect(xx, yy, 28, 28, [INDIGO[1], "#eff1ed", "#d0e4db"][i])
            center(d, xx + 14, yy + 19, str(val), 15, BLUE if val < 0 else GREEN, 600, "mono")
    d.wire("M207 501h24")
    d.wire("M334 501h36")
    center(d, 118, 581, "实拍屏幕裁片", 16, SLATE)
    center(d, 285, 581, "水平梯度核 Gx", 16, SLATE)
    center(d, 462, 581, "两向梯度幅值", 16, SLATE)
    t(d, 34, 621, "像素邻域 → 水平 / 垂直梯度 → 边缘响应", 18, NAVY, 620)
    t(d, 34, 648, "右图由左图离线计算，用于解释算子。", 16, SLATE)
    d.path("M575 394V655", RULE)
    section(d, 598, 412, "c", "命令到达与模式生效", GREEN)
    for yy, s in [(474, "串口命令"), (525, "待提交"), (577, "显示模式")]:
        t(d, 599, yy, s, 17, SLATE)
    d.path("M691 470h50v-16h40v16h243", BLUE, 2.2)
    d.path("M691 521h92v-17h83v17h158", AMBER, 2.2)
    d.path("M866 440v151", GREEN, 1.2, False, True)
    for xx, ww, lab, p in [(691, 174, "当前帧 A", INDIGO), (867, 157, "下一帧 B", JADE)]:
        d.rect(xx, 551, ww, 36, p[1], p[2])
        center(d, xx + ww / 2, 575, lab, 17, p[0], 630)
    t(d, 692, 619, "跨域握手", 17, BLUE, 600)
    t(d, 866, 619, "帧首提交", 17, GREEN, 600)
    t(d, 598, 648, "时序仅示意事件先后，不按时钟比例绘制。", 15, SLATE)
    footer(d, "像素面：OV5640 / SDRAM / FPGA", "控制面：串口命令 / 跨域握手 / 帧同步")
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
        "按阵元坐标绘制五组换能器，并将音频通路与参数通路分开标出。",
        "Ultrasonic audio",
        "实拍工作台；按工程标称坐标绘制的阵元斜视图，附控制、音频及 PWM 时序示意，非声场测量。",
    )
    section(d, 34, 145, "a", "阵列实物", BLUE)
    photo(d, "n60-hardware.jpg", 34, 169, 266, 181, (0, 0, 1600, 1090))
    t(d, 34, 379, "换能器、支架与控制板", 17, SLATE)
    t(d, 34, 412, "5 组 × 12 个阵元", 24, BLUE, 650)
    d.rect(325, 127, 721, 303, "#f0f5f3", r=5)
    t(d, 347, 159, "标称阵元坐标 · 斜视", 22, GREEN, 650)
    t(d, 1023, 158, "U0 — U4", 17, SLATE, 550, "end", "mono")

    def pt(theta, lx, ly, depth=0):
        a = radians(theta)
        x = 176.445 * sin(a) + lx * cos(a) + depth * sin(a)
        z = -176.445 * cos(a) + lx * sin(a) - depth * cos(a)
        return 685 + 1.85 * x, 270 - 1.38 * ly + 0.76 * (z + 176.445)

    line(d, [pt(a, 0, -40) for a in range(-51, 52)], "#c5d3cd", 3)
    accents = ["#44698a", "#4b7c87", "#2b7365", "#64816b", "#96774b"]
    for i in [2, 1, 3, 0, 4]:
        a = MODULES[i]
        col = accents[i]

        # Project the circular mounting face and each of the 12 hollow cylinders.
        def disc(cx, cy, r, depth, theta=a):
            count = 56 if r > 8 else 18
            return [
                pt(theta, cx + r * cos(th * 2 * pi / count), cy + r * sin(th * 2 * pi / count), depth)
                for th in range(count)
            ]

        poly(d, disc(0, 0, 44, 7), "#a5b5b0", "#80958e")
        poly(d, disc(0, 0, 44, 0), "#d9e2dd", "#92a69b")
        for lx, ly in sorted(N12, key=lambda v: -v[1]):
            poly(d, disc(lx, ly, 6.2, 0), "#73847f")
            poly(d, disc(lx, ly, 6.1, -5), "#e6ece7", "#7a8b85", 0.8)
            poly(d, disc(lx, ly, 4.2, -5), "#385152")
            poly(d, disc(lx, ly, 2.5, -5), "#657b75")
        u, v = pt(a, 0, -46)
        line(d, [(u, v), (u, 375)], col, 1.1)
        d.circ(u, 375, 2.7, col)
        center(d, u, 401, f"U{i}", 18, col, 660, "mono")
        center(d, u, 420, f"{a:+g}°", 14, SLATE, 500)
    d.path("M34 450H1046", RULE)
    section(d, 34, 484, "b", "两路输入在 FPGA 汇合", BLUE)
    for yy, title, sub, theme in [
        (534, "上位机 / UART", "逐通道相位、幅度", INDIGO),
        (610, "音频 / I²S", "WM8978 音频采样", OCHRE),
    ]:
        d.rect(34, yy - 24, 190, 59, theme[1], theme[2], 3)
        t(d, 46, yy, title, 18, theme[0], 630)
        t(d, 46, yy + 24, sub, 15, SLATE)
    d.wire("M225 538h28v24h30")
    d.wire("M225 609h28v-21h30")
    d.rect(289, 536, 191, 77, JADE[1], JADE[2], 3)
    center(d, 384, 568, "FPGA 调制", 22, GREEN, 650)
    center(d, 384, 596, "60 路 PWM 输出", 17, SLATE)
    d.path("M505 472V651", RULE)
    section(d, 530, 484, "c", "相移在载波时序中的位置", GREEN)
    for i, (tag, off, col) in enumerate([("通道 A", 0, GREEN), ("通道 B", 26, BLUE)]):
        yy = 553 + 62 * i
        t(d, 530, yy + 3, tag, 16, SLATE)
        xx = 641
        pts = [(623, yy), (xx + off, yy)]
        for k in range(3):
            q = xx + off + 107 * k
            pts.extend([(q, yy), (q, yy - 22), (q + 46, yy - 22), (q + 46, yy), (q + 106, yy)])
        line(d, pts, col, 2.4)
    d.path("M641 521v-8h107v8M641 557v67M667 590v34", "#91a39e", 1, False, True)
    t(d, 763, 520, "25 μs / 周期", 17, GREEN, 620)
    d.path("M641 629h26", AMBER, 2)
    t(d, 684, 646, "相对延迟示意", 15, AMBER)
    footer(
        d,
        "载波：40 kHz    ·    每个阵元对应一路输出",
        "斜视图基于工程几何，而非实测声压图；波形不按幅值标定。",
    )
    d.save("atlas-05-array.svg")


def ct():
    d = page(
        7,
        "ConeFDK",
        "CUDA 锥束反投影与逐层核对",
        "720 幅核桃投影重建成 512³ 体素；在同一体数据上与 ASTRA 比较。",
        "DGX Spark / GB10",
        "左为真实核桃轴向切片与冠状、矢状断面；右为锥束和体素列示意；下方保留逐层误差实测曲线。",
    )
    section(d, 34, 144, "a", "核桃 CT / 重建断面", BLUE)
    d.rect(34, 156, 352, 247, "#101315", r=3)
    with Image.open(ASSETS / "conefdk-sweep.gif") as im:
        im.seek(12)
        data = encode(im, (276, 276), quality=93)
    (OUT / "atlas-07-still.webp").write_bytes(data)
    embed(d, data, 95, 164, 230, 230)
    t(d, 43, 183, "XY", 17, "#a5c8bb", 600, cls="mono")
    for x, tag, crop in [(34, "XZ", (310, 34, 620, 344)), (213, "YZ", (620, 34, 930, 344))]:
        d.rect(x, 411, 173, 73, "#16242b")
        photo(d, "conefdk-walnut.png", x + 52, 413, 70, 69, crop)
        t(d, x + 10, 433, tag, 14, "#c0d2d1", 600, cls="mono")
    section(d, 406, 144, "b", "一个线程如何更新一列体素", GREEN)
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
    for vy in [268, 321]:
        uv = 867
        dy = 292 + (vy - 292) * (uv - 443) / (660 - 443)
        line(d, [src, (uv, dy)], "#a06937", 1.15, False, True)
        d.circ(660, vy, 3.2, AMBER)
        d.circ(uv, dy, 3.2, AMBER)
    d.circ(*src, 5, AMBER)
    t(d, 418, 321, "射线源", 16, AMBER, 620)
    t(d, 622, 379, "固定 (x, y)", 16, GREEN, 620)
    t(d, 939, 346, "探测器平面", 16, GREEN, 620)
    # Detail of the four detector samples bracketing one projected point.
    d.path("M870 245h61l18-29h12", AMBER, 1, False, True)
    d.rect(961, 181, 76, 77, "#f7faf7", RULE, 2)
    grid(d, 970, 190, 58, 58, 29, 29, "#b1c6be")
    for xx in (970, 999):
        for yy in (190, 219):
            d.circ(xx, yy, 3.1, GREEN)
    d.path("M970 208h29M988 190v29", AMBER, 0.9, False, True)
    d.circ(988, 208, 3.0, AMBER)
    center(d, 997, 281, "四邻点", 16, GREEN, 610)
    center(d, 997, 301, "插值", 15, SLATE)
    t(d, 411, 423, "逐行加权 → cuFFT / Ram-Lak → 按列反投影", 21, NAVY, 640)
    t(d, 411, 453, "相邻 Z 层共享几何权重；每层从探测器四邻点插值。", 17, SLATE)
    t(d, 411, 479, "每线程至多更新 16 个体素。", 17, GREEN, 610)
    d.path("M34 501H1046", RULE)
    section(d, 34, 541, "c", "CUDA / ASTRA", BLUE)
    t(d, 34, 605, "0.02899%", 48, GREEN, 660, cls="serif")
    t(d, 36, 643, "整卷重建强度的相对 L2 差异", 17, SLATE)
    x0, x1, y0, y1 = 415, 1022, 558, 636
    root = ET.parse(ASSETS / "conefdk-walnut-peak.svg")
    raw = next(n.get("points") for n in root.iter() if n.tag.endswith("polyline")).split()
    assert len(raw) == 512
    points = []
    for pair in raw:
        u, v = map(float, pair.split(","))
        points.append((x0 + (u - 54) / 450 * (x1 - x0), y1 - (130 - v) / 94 * (y1 - y0)))
    t(d, 413, 537, "逐层最大绝对强度差", 19, NAVY, 630)
    t(d, 1023, 537, "首个峰值：z = 256", 16, AMBER, 630, "end")
    for yy in [y0, (y0 + y1) / 2, y1]:
        d.path(f"M{x0} {yy}H{x1}", RULE, 1, False, True)
    poly(d, [(x0, y1), *points, (x1, y1)], "#e7f0f3")
    line(d, points, BLUE, 1.5)
    px, py = points[256]
    d.path(f"M{px} {py}V{y1}", AMBER, 1.1, False, True)
    d.circ(px, py, 4, AMBER)
    for xx, s in [(x0, "0"), (px, "256"), (x1, "511")]:
        center(d, xx, 660, s, 14, SLATE, 550, "mono")
    t(d, 404, y0 + 5, "4.74e−5", 14, SLATE, 500, "end", "mono")
    t(d, 404, y1 + 4, "0", 14, SLATE, 500, "end", "mono")
    footer(
        d,
        "数据：Alexander Meaney / University of Helsinki · CC BY 4.0",
        "比较重建强度，不代表物理尺寸误差。",
    )
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
