"""Build homepage engineering plates 03–09 from tracked project materials.

Run with Pillow installed: python -B tools/draw_project_covers.py
See ASSETS.md for provenance. All SVGs embed their evidence and open offline.
"""

import base64
import xml.etree.ElementTree as ET
from html import escape
from io import BytesIO
from math import cos, pi, sin

from draw_vitis import INDIGO, JADE, NAVY, NEUTRAL, OCHRE, OUT, SLATE, Plate, letter
from PIL import Image, ImageOps

ASSETS = OUT.parent
WHITE, LINE, MUTED = "#ffffff", "#c4d1d4", "#4b626d"
XLINK = "{http://www.w3.org/1999/xlink}href"


def txt(d, x, y, s, size=21, color=NAVY, weight=550, anchor="start", cls=""):
    d.text(x, y, s, size, 450 if weight == 550 and color == SLATE else weight, color, anchor, cls)


def mid(d, x, y, s, size=20, color=NAVY, weight=550, cls=""):
    txt(d, x, y, s, size, color, weight, "middle", cls)


def figure(n, title, english, desc):
    d = Plate(1080, 720, title, desc)
    txt(d, 32, 67, title, 39, NAVY, 680)
    txt(d, 1048, 38, f"ENGINEERING PLATE   /   {n:02d}", 16, JADE[0], 600, "end", "mono")
    txt(d, 1048, 67, english, 19, SLATE, 500, "end", "serif")
    d.path("M32 86H1048", NAVY, 2)
    return d


def panel(d, x, y, w, h, key, title, p):
    d.rect(x, y, w, h, WHITE, p[2], 3)
    d.rect(x, y, w, 4, p[0])
    letter(d, x + 16, y + 17, key, p[0])
    txt(d, x + 56, y + 40, title, 24, p[0], 650)


def upper(d, a, b):
    panel(d, 32, 105, 356, 331, "a", a, INDIGO)
    panel(d, 404, 105, 644, 331, "b", b, JADE)


def lower(d, label):
    panel(d, 32, 456, 1016, 235, "c", label, OCHRE)


def box(d, x, y, w, h, label, sub="", p=NEUTRAL):
    d.rect(x, y, w, h, p[1], p[2], 4)
    mid(d, x + w / 2, y + h / 2 + (8 if not sub else -1), label, 22, p[0], 630)
    if sub:
        mid(d, x + w / 2, y + h / 2 + 22, sub, 17, SLATE, 450)


def encoded(im, size, crop=None, quality=86):
    if crop:
        im = im.crop(crop)
    im = ImageOps.fit(im.convert("RGB"), size, Image.Resampling.LANCZOS)
    out = BytesIO()
    im.save(out, "WEBP", quality=quality, method=6)
    return out.getvalue()


def embed(d, data, x, y, w, h):
    uri = base64.b64encode(data).decode("ascii")
    d.el.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/webp;base64,{uri}"/>')


def photo(d, name, caption, crop=None):
    with Image.open(ASSETS / name) as im:
        data = encoded(im, (640, 440), crop)
    embed(d, data, 50, 166, 320, 220)
    txt(d, 50, 415, caption, 18, SLATE)


def metadata(d, s):
    d.el.append("<metadata>" + escape(s) + "</metadata>")


def lissajous():
    d = figure(
        3,
        "让两路信号在示波器上成图",
        "Phase tracking & waveform synthesis",
        "有线 DPLL 与视觉估计两条通路。下方三条理论轨迹旁是示波器实拍，屏上可见双环。",
    )
    upper(d, "竞赛工作台", "两种方式确定 DDS 的频率与相位")
    photo(d, "lissajous-hardware.jpg", "实拍：示波器、控制板与摄像头。", (0, 0, 1706, 1173))
    for y, mode, labels, p in [
        (
            202,
            "有线锁相",
            [("ADC 采样", "原始输入"), ("I/Q 相关", "DPLL 跟踪"), ("48 位 DDS", "合成 Y 轴")],
            INDIGO,
        ),
        (
            329,
            "视觉估计",
            [("摄像头", "多帧轨迹"), ("Jetson Nano", "估计频率与相位"), ("UART → DDS", "更新控制字")],
            JADE,
        ),
    ]:
        txt(d, 426, y - 13, mode, 19, p[0], 650)
        for i, (t, s) in enumerate(labels):
            x = 426 + i * 205
            box(d, x, y, 182, 74, t, s, p)
            if i < 2:
                d.wire(f"M{x + 182} {y + 37}h19")
    lower(d, "X–Y 显示：频比和相位决定轨迹形状")
    for i, label in enumerate(
        ("同频同相 · 直线", "同频正交 · 等幅圆", "频率比 1 : 2 · 双环", "实拍屏幕局部")
    ):
        x = 52 + i * 249
        cx, cy = x + 114, 584
        if i:
            d.path(f"M{x - 10} 523v144", LINE)
        if i == 3:
            with Image.open(ASSETS / "lissajous-hardware.jpg") as src:
                detail = encoded(src, (300, 168), (853, 95, 1138, 260))
            embed(d, detail, x + 10, 525, 207, 116)
            mid(d, cx, 669, label, 20, INDIGO[0], 650)
            continue
        d.rect(x + 10, 525, 207, 116, "#f1f6f5", LINE, 3)
        d.path(f"M{x + 20} {cy}h187M{cx} 533v101", "#b6c7c3", 1)
        pts = []
        for j in range(161):
            t = 2 * pi * j / 160
            a = sin(t)
            b = [a, cos(t), sin(2 * t)][i]
            pts.append((cx + (46 if i == 1 else 72) * a, cy - 46 * b))
        d.path("M" + " L".join(f"{u:.1f},{v:.1f}" for u, v in pts), JADE[0], 3)
        mid(d, cx, 669, label, 20, NAVY, 600)
    d.save("atlas-03-phase.svg")


def vision():
    d = figure(
        4,
        "从摄像头像素到双路显示",
        "Frame-synchronous video processing",
        "竞赛实拍及基础版视频路径：帧缓存、像素处理、HDMI 与 UDP 输出。时序图示意在帧边界切换算法。",
    )
    upper(d, "竞赛演示实拍", "基础版视频数据通路")
    photo(d, "elinx-competition-demo.png", "开发板、本地显示器与上位机。")
    for i, (t, s) in enumerate(
        [("OV5640", "RGB565"), ("SDRAM", "跨域帧缓存"), ("像素处理", "显示时钟域")]
    ):
        x = 428 + i * 204
        box(d, x, 178, 175, 75, t, s, INDIGO if i < 2 else JADE)
        if i < 2:
            d.wire(f"M{x + 175} 215h25")
    d.path("M923 253V282H583V308M923 282v26", "#496778", 1.7)
    d.circ(923, 282, 3, "#496778")
    d.wire("M583 303v10")
    d.wire("M923 303v10")
    box(d, 465, 317, 236, 77, "HDMI", "本地显示", JADE)
    box(d, 816, 317, 205, 77, "UDP → PyQt6", "上位机预览", OCHRE)
    lower(d, "帧边界提交：同一帧内不混用两种算法")
    txt(d, 53, 549, "串口命令", 19)
    txt(d, 53, 602, "显示输出", 19)
    x = 177
    d.path("M177 545H330V529H402V545H685", INDIGO[0], 2.5)
    txt(d, 414, 538, "新模式已挂起", 17, INDIGO[0])
    d.path("M468 550v84", JADE[0], 1.5, False, True)
    for xx, w, label, p in [(x, 290, "当前帧 · 模式 A", INDIGO), (469, 216, "下一帧 · 模式 B", JADE)]:
        box(d, xx, 568, w, 52, label, p=p)
    txt(d, 469, 651, "帧同步边界", 18, JADE[0])
    d.path("M714 520v146", LINE)
    txt(d, 739, 548, "UDP 回传图像", 20, SLATE)
    txt(d, 738, 607, "1024 × 600", 43, JADE[0], 650, cls="serif")
    txt(d, 740, 645, "基础版输出尺寸", 18, SLATE)
    d.save("atlas-04-vision.svg")


def array():
    d = figure(
        5,
        "一套音频输入，五组超声子阵",
        "Multichannel ultrasonic audio",
        "实拍阵列、上位机控制与板端音频通路；五组各十二个通道的分组示意。",
    )
    upper(d, "阵列与控制板", "音频与控制参数在 FPGA 汇合")
    photo(d, "n60-hardware.jpg", "实拍：五组子阵与阵列控制板。", (0, 0, 1600, 1100))
    box(d, 427, 178, 202, 76, "上位机", "逐通道相位 / 幅度", INDIGO)
    box(d, 427, 302, 202, 76, "音频输入", "WM8978 / I²S", OCHRE)
    d.wire("M629 215H692V247H737")
    d.wire("M629 340H692V307H737")
    txt(d, 641, 204, "UART", 16, SLATE, 550, cls="mono")
    d.rect(741, 200, 276, 155, JADE[1], JADE[2], 4)
    txt(d, 765, 240, "FPGA", 29, JADE[0], 650)
    txt(d, 765, 278, "多通道 PWM 调制", 23, JADE[0], 620)
    for i in range(4):
        x = 767 + 54 * i
        d.path(f"M{x} 324v-19h{12 + i * 4}v19h{40 - (12 + i * 4)}", JADE[0], 2)
    txt(d, 427, 415, "参数和音频独立输入；输出经驱动级送往阵元。", 19, SLATE)
    lower(d, "通道分组：每个阵元对应一路输出")
    for g in range(5):
        xx = 53 + 132 * g
        d.rect(xx, 532, 120, 102, "#f5f8f6", JADE[2], 4)
        for j in range(12):
            cx, cy = xx + 26 + (j % 4) * 22, 553 + (j // 4) * 21
            d.circ(cx, cy, 6.6, "#639186")
            d.circ(cx, cy, 2.1, "#dbeae2")
        mid(d, xx + 60, 658, f"子阵 {g + 1}", 19, SLATE)
    d.path("M724 520v148", LINE)
    txt(d, 748, 557, "5 × 12 = 60 路", 28, JADE[0], 650)
    txt(d, 747, 612, "40 kHz", 43, NAVY, 650, cls="serif")
    txt(d, 749, 647, "PWM 载波频率", 19, SLATE)
    d.save("atlas-05-array.svg")


def uav():
    d = figure(
        6,
        "同一目标，只在首次确认时计数",
        "Three-frame identity confirmation",
        "左侧是水岸合成示意；右侧按身份跟踪三帧；下方单列半合成视频留出集的真实判读结果。",
    )
    upper(d, "水岸场景示意", "三帧内按身份判断是否新增")
    r = ET.parse(ASSETS / "uavcount-pipeline.svg")
    imgs = {
        n.get("id"): Image.open(BytesIO(base64.b64decode(n.get(XLINK).split(",")[1]))).convert("RGBA")
        for n in r.iter()
        if n.tag.endswith("image")
    }
    im = imgs["waterside"].copy()
    aircraft = imgs["aircraft"]
    for x, y, w in [(128, 46, 33), (298, 73, 20)]:
        a = aircraft.resize((w, round(w * aircraft.height / aircraft.width)), Image.Resampling.LANCZOS)
        im.alpha_composite(a, (x, y))
    embed(d, encoded(im, (576, 254)), 50, 175, 320, 141)
    txt(d, 50, 352, "对齐视频帧 → 检测候选", 22, INDIGO[0], 620)
    txt(d, 50, 388, "以短轨迹关联候选目标。", 19, SLATE)
    txt(d, 50, 417, "场景为合成示意，非测试帧。", 17, SLATE)
    for x, l in [(660, "t − 2"), (755, "t − 1"), (850, "t"), (976, "新增")]:
        mid(d, x, 188, l, 18, SLATE, 550)
    for i, (label, obs, answer, p) in enumerate(
        [
            ("已计目标", [1, 0, 1], "0", INDIGO),
            ("新目标", [1, 1, 1], "+1", JADE),
            ("孤立候选", [0, 1, 0], "0", OCHRE),
        ]
    ):
        y = 226 + i * 66
        txt(d, 429, y + 6, label, 23, p[0], 620)
        d.path(f"M625 {y}h262", LINE)
        if i < 2:
            d.path(f"M660 {y}H850", p[0], 2, False, i == 0)
        for x, o in zip((660, 755, 850), obs):
            d.circ(x, y, 10, p[0] if o else WHITE, p[0] if o else LINE)
        mid(d, 976, y + 9, answer, 29, p[0], 650, "mono")
    d.path("M920 201v181", LINE)
    txt(d, 429, 412, "实心为观测；短时漏检可续接已有身份。", 18, SLATE)
    lower(d, "留出视频：按三帧判读窗核对新增数")
    txt(d, 54, 584, "167 / 184", 57, JADE[0], 650, cls="serif")
    txt(d, 57, 625, "计数正确的留出窗口", 21, SLATE)
    d.path("M357 524v142", LINE)
    txt(d, 384, 562, "90.76%", 36, NAVY, 650, cls="serif")
    txt(d, 385, 600, "窗口计数正确率", 20, SLATE)
    d.rect(385, 621, 225, 9, "#dce2e1", r=3)
    d.rect(385, 621, round(225 * 167 / 184), 9, JADE[0], r=3)
    d.path("M650 524v142", LINE)
    txt(d, 676, 557, "回归材料：156 段半合成视频", 21, NAVY, 600)
    txt(d, 676, 595, "每段预热 10 帧，每 3 帧判读。", 20, SLATE)
    txt(d, 676, 635, "指标按窗口计算，不是逐帧检测率。", 18, SLATE)
    d.save("atlas-06-tracking.svg")


def tomography():
    d = figure(
        7,
        "从 720 幅投影重建一颗核桃",
        "Cone-beam reconstruction on DGX Spark",
        "真实核桃重建切片；CUDA 投影行滤波与按列反投影；512³ 体素与 ASTRA 的相对 L2 差异为 0.02899%。",
    )
    upper(d, "核桃 CT · 轴向切片", "CUDA FDK：先滤波，再按列反投影")
    with Image.open(ASSETS / "conefdk-sweep.gif") as im:
        im.seek(12)
        data = encoded(im, (276, 276), quality=93)
    (OUT / "atlas-07-still.webp").write_bytes(data)
    d.rect(50, 163, 320, 233, "#101315")
    embed(d, data, 95, 164, 230, 230)
    txt(d, 50, 420, "实测投影重建 · 512³ 体素", 19, SLATE)
    for i, (t, s) in enumerate(
        [("锥束加权", "探测器逐行"), ("cuFFT", "Ram-Lak 滤波"), ("反投影", "按列累加")]
    ):
        x = 426 + i * 205
        box(d, x, 177, 183, 78, t, s, INDIGO if i < 2 else JADE)
        if i < 2:
            d.wire(f"M{x + 183} 216h18")
    d.rect(427, 280, 595, 133, "#f5f8f7", JADE[2], 3)
    for j in range(6):
        x = 452
        y = 310 + j * 12
        d.rect(x, y, 57, 10, JADE[1] if j % 2 else "#a6c4b6", JADE[2])
    d.path("M518 311h8v69h-8", JADE[0], 1.7)
    txt(d, 551, 323, "一个线程更新同列至多 16 个体素", 24, JADE[0], 650)
    txt(d, 551, 361, "相邻 Z 层共享列坐标与几何权重，", 20, SLATE)
    txt(d, 551, 389, "分别插值，再累加投影贡献。", 20, SLATE)
    lower(d, "同一颗核桃：原生 CUDA 与 ASTRA 逐体素对照")
    txt(d, 54, 588, "0.02899%", 54, JADE[0], 650, cls="serif")
    txt(d, 56, 628, "整卷重建强度的相对 L2 差异", 21, SLATE)
    txt(d, 56, 658, "比较求解器，不代表实物尺寸误差。", 17, SLATE)
    d.path("M446 521v145", LINE)
    txt(d, 468, 541, "各层最大绝对强度差", 19, NAVY, 600)
    root = ET.parse(ASSETS / "conefdk-walnut-peak.svg")
    pts = next(n.get("points") for n in root.iter() if n.tag.endswith("polyline")).split()
    assert len(pts) == 512
    vals = [tuple(map(float, p.split(","))) for p in pts]
    pts = [(474 + (x - 54) / 450 * 539, 647 - (130 - y) / 94 * 85) for x, y in vals]
    d.path("M474 562v85h539", LINE)
    d.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), INDIGO[0], 1.6)
    x, y = pts[256]
    d.circ(round(x, 1), round(y, 1), 4.6, OCHRE[0])
    txt(d, 797, 554, "z = 256 · 峰值 4.736 × 10⁻⁵", 16, OCHRE[0])
    txt(d, 473, 672, "z = 0", 16, SLATE)
    txt(d, 1012, 672, "511", 16, SLATE, 500, "end")
    metadata(
        d,
        "Walnut data: Alexander Meaney, University of Helsinki, https://doi.org/10.5281/zenodo.6986012 ; CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ . Binned, normalized and reconstructed with ConeFDK; this plate embeds a slice and redraws the measured difference curve.",
    )
    d.save("atlas-07-ct.svg")


def spark():
    d = figure(
        8,
        "把 PyTorch 子图编译成 CUDA",
        "Q/K/V fusion & single-node inference",
        "DGX Spark 型号照片；单层 Q/K/V 共用 INT8 GEMM，四层 BERT 前向从 233 次内核启动减至 64 次。32B 与 355B 为独立整模型实验。",
    )
    upper(d, "单机实验平台", "编译四层 BERT：每层合并三路投影")
    with Image.open(OUT / "sparkfuse-system-full.webp") as im:
        data = encoded(im, (535, 362), (22, 195, 557, 557))
    embed(d, data, 92, 162, 236, 160)
    mid(d, 210, 361, "NVIDIA DGX Spark", 29, NAVY, 650, "serif")
    mid(d, 210, 396, "GB10  /  设备型号图", 19, SLATE)
    colors = [
        ("#874938", "#f4d9cf", "#d3a597"),
        ("#845d29", "#f6e4ca", "#d6b58a"),
        ("#735d38", "#eee3c6", "#cdb98e"),
    ]
    txt(d, 425, 187, "INT8 权重按列打包", 20, SLATE)
    for i in range(3):
        x = 427 + 92 * i
        ink, fill, edge = colors[i]
        d.rect(x, 202, 87, 52, fill, edge, 4)
        mid(d, x + 43, 237, "QKV"[i], 26, ink, 650, "serif")
    d.wire("M704 228h50")
    box(d, 761, 201, 258, 55, "一次 INT8 GEMM", p=JADE)
    txt(d, 426, 283, "权重矩阵 768 × 2304", 18, SLATE)
    txt(d, 762, 283, "三路分别写回 BF16", 18, SLATE)
    d.path("M426 301H1025", LINE)
    txt(d, 427, 338, "GPU 内核启动次数", 21, NAVY, 650)
    txt(d, 426, 402, "233 → 64", 51, JADE[0], 650, cls="serif")
    txt(d, 727, 390, "四层 / 33 tokens / 一次前向", 20, SLATE)
    lower(d, "同机独立实验：长前缀复用与量化模型推理")
    txt(d, 56, 543, "Qwen2.5-32B  /  BF16", 23, INDIGO[0], 650)
    txt(d, 56, 603, "9.443 → 7.659 s", 45, NAVY, 650, cls="serif")
    txt(d, 57, 641, "两请求耗时中位数；各输入 2,048 tokens，", 18, SLATE)
    txt(d, 57, 668, "共享前缀 1,536，各生成 8 个 tokens。", 18, SLATE)
    d.path("M557 518v156", LINE)
    txt(d, 585, 543, "GLM-4.5 355B  /  UD-IQ1_S", 23, OCHRE[0], 650)
    txt(d, 584, 603, "2.588 s", 45, NAVY, 650, cls="serif")
    txt(d, 586, 641, "已加载模型的本机 HTTP 请求中位数；", 18, SLATE)
    txt(d, 586, 668, "输入 128 tokens，生成 16 个 tokens。", 18, SLATE)
    metadata(
        d,
        "Device photo: Daniel Lu (dllu), https://commons.wikimedia.org/wiki/File:Nvidia_DGX_Spark_oblique_view_dllu.jpg . Cropped from the existing composite; this redesigned plate is licensed CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ . Model-identification image, not a photograph of the benchmark run.",
    )
    d.save("atlas-08-compiler.svg")


def rocket():
    d = figure(
        9,
        "在 VCU118 上启动 Rocket Linux",
        "FPGA configuration to a BusyBox shell",
        "左侧是板上验收 JSON 的字段摘录，不是串口屏幕截图。JTAG 配置与 UART 固件装载分开。底部为独立的一对端到端计时。",
    )
    upper(d, "板上验收记录", "从易失配置到 Linux 用户态")
    d.rect(50, 173, 320, 189, "#f2f6f6", INDIGO[2], 3)
    d.rect(50, 173, 320, 33, INDIGO[1], INDIGO[2], 3)
    txt(d, 62, 196, "linux-oscheck  /  JSON 字段摘录", 17, INDIGO[0], 600)
    for i, (s, v) in enumerate(
        [
            ("uart", "115200 8N1"),
            ("slr_done", "[1, 1, 1]"),
            ("slr_crc_error", "[0, 0, 0]"),
            ("shell_challenge_verified", "true"),
        ]
    ):
        txt(d, 62, 233 + 36 * i, s, 16, NAVY, 550, cls="mono")
        txt(d, 359, 233 + 36 * i, v, 17, JADE[0], 650, "end", "mono")
    txt(d, 50, 394, "三个 SLR 配置完成；", 19, SLATE)
    txt(d, 50, 419, "BusyBox 正确回答现场命令。", 19, SLATE)
    txt(d, 426, 186, "配置通路", 19, INDIGO[0], 630)
    box(d, 426, 200, 195, 60, "J106 / JTAG", p=INDIGO)
    d.wire("M621 230h39")
    box(d, 665, 200, 353, 60, "FPGA · 100 MHz 五级 Rocket", p=INDIGO)
    txt(d, 426, 297, "固件与软件启动", 19, JADE[0], 630)
    for i, (t, s) in enumerate(
        [("J4 UART", "Boot ROM"), ("DDR4", "固件 / OpenSBI"), ("Linux 6.6.65", "BusyBox")]
    ):
        x = 426 + i * 204
        box(d, x, 313, 183, 79, t, s, JADE)
        if i < 2:
            d.wire(f"M{x + 183} 353h17")
    lower(d, "同一固件两种传法：从串口开始发送，到 shell 回答")
    for i, (l, v, p) in enumerate([("原始固件", 495.050, INDIGO), ("自解压固件", 194.469, JADE)]):
        yy = 540 + i * 63
        txt(d, 54, yy + 22, l, 22, p[0], 630)
        ww = round(400 * v / 495.050)
        d.rect(202, yy, ww, 26, p[1], p[2], 3)
        d.rect(202, yy, 5, 26, p[0])
        txt(d, ww + 219, yy + 23, f"{v:.3f} s", 25, p[0], 650, cls="mono")
    d.path("M765 522v145", LINE)
    txt(d, 787, 555, "对照条件", 21, NAVY, 650)
    txt(d, 787, 592, "同板、同一 bitstream", 19, SLATE)
    txt(d, 787, 625, "不含 JTAG 配置时间", 19, SLATE)
    metadata(
        d,
        "Record excerpt: https://github.com/EtherealBian/vcu118-rocket-soc/blob/5862e904c97ca7648daaa45c04587dbfe4fa081f/docs/portable-linux-rocket-boot.json . Timing bars are a distinct paired experiment reported on work/vcu118-rocket.html.",
    )
    d.save("atlas-09-rocket.svg")


if __name__ == "__main__":
    for build in (lissajous, vision, array, uav, tomography, spark, rocket):
        build()
