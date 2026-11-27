# 图像与来源

原站基线：`1b77a3832f730435245b787ccb25bc0b1f26c315`。保留当前主页仓库内所有原始照片、中文/英文架构图、矢量流程图和品牌图。为适配浏览器新增的图版不会回写源项目或替换原始实验材料。

| 新图版（`assets/plates/`） | 依据与处理 |
|---|---|
| `scope.webp`、`array.webp`、`vision.webp` | 由本站原有 `lissajous-hardware.jpg`、`n60-hardware.jpg`、`elinx-competition-demo.png` 派生：缩放、轻微对比与锐化、WebP 压缩。卡片取景不影响原图入口。 |
| `../pmux-overview-zh.webp`、`../pmux-overview-zh.png` | 高清 PNG 与 [Yosys 项目机制图](https://github.com/EtherealBian/yosys-pmux-opt/blob/main/docs/pmux-overview-zh.png) 一致；1360 × 917 的无损 WebP 由该 PNG 等比缩小，不裁切。 |
| `uavcount-counting.svg` | 按原图 `assets/uavcount-pipeline.svg` 的算法步骤、输出样例和回归统计，以及 `work/uavcount.html` 的计数判据重绘。三条身份轨迹只用于说明规则，不是实拍观测；统计来自 156 段半合成视频，不代表实景检测准确率。原图保留。 |
| `vitis-hls-architecture.svg` | 为本次改版绘制的五面板工程图。初赛三算子的机制和固定测试负载周期按 [Vitis 项目说明](https://github.com/EtherealBian/vitis-hls-kernel-optimization)；决赛频谱仪另列。 |
| `kernels.webp` | 由本站三算子架构原图 `vitis-hls-kernel-optimization.png` 压缩，保留完整图形和数值。 |
| `spectrum.webp` | 来自 [Vitis HLS 项目运行截图](https://github.com/EtherealBian/vitis-hls-kernel-optimization/blob/177cd62badb31cd49874cee63ad8f9e81079a383/docs/competition-app.jpg)。仅作竞赛期间应用界面的图证，未重绘数据曲线。 |
| `dpll.webp` | 来自 [李萨如项目有线 DPLL 架构](https://github.com/EtherealBian/fpga-lissajous-controller/blob/d28a09db401a55449636eb1bcb8951629dd83aec/docs/wired-dpll.png)，保留完整信号处理流程。 |
| `geometry.webp` | 来自 [N60 阵元分布图](https://github.com/EtherealBian/n60-ultrasonic-phased-array/blob/05a0002d54e6c3cd4d754f1168ba83c06418adcf/docs/images/fig_array_top.png)，保留坐标与图例。 |
| `cnn.webp` | 来自 [eLinex FPGA 数字识别流水线](https://github.com/EtherealBian/elinx-vision-stream/blob/11b7c3dd3abe4609ec54cea3117e6ea57d33084b/docs/cnn-pipeline.png)，保留完整流程。 |

- `assets/harmonic-study.svg` / `harmonic-study-small.svg`：沿用之前的三叶环面结线稿，小屏使用笔画较粗的版本；仅为封面图形，不是实验数据。
- `assets/portfolio-cover.jpg`：从独立扉页的三个英文词、原有环形线稿及研究方向导出的 1200 × 630 社交分享图。首页不请求这张图片。
- `assets/orbit.svg`：原创轨道标志，用在导航和 favicon。About Me 的姓名旁使用原有 `assets/avatar.jpg`，右侧研究方向只用文字。
- 论文旁的点阵和扫描线是标为“概念示意”的视觉辅助，**不是荧光实验图或重建结果**。原站未提供论文原图、作者表或公开全文地址。
- 太一量生品牌图仍链接回原站保留的品牌图来源。学校邮箱经本人确认，统一使用 `EtherealBian@njust.edu.cn`。

本地保留的 WebP 预览对应以下原始文件：`wired-dpll.png`、`cnn-pipeline.png`、`fig_array_top.png` 和 `competition-app.jpg`。来源分别与上表四个项目链接一致。

### Vitis 多面板图版

`tools/draw_vitis.py` 输出五幅独立 SVG。主图是一张可独立保存的五面板图：a–c 为算法原理、数据通路、固定用例总周期与验证条件；d 为独立的决赛整机数据流；e 内嵌竞赛应用截图的幅度谱区域，保留原始曲线和标记。e 的采样率 1 kHz、1,024 点与 d 的 48 kHz、4,096 点演示配置分开标注。`vitis-sha.svg`、`vitis-lz4.svg`、`vitis-cholesky.svg` 及 `vitis-zynq-system.svg` 按[项目归档](https://github.com/EtherealBian/vitis-hls-kernel-optimization/tree/177cd62badb31cd49874cee63ad8f9e81079a383)的算子说明、协同仿真记录与决赛 PL/PS 接口重绘，详细出处位于各图旁边。

制图参考：[Nature Research Figure Guide](https://research-figure-guide.nature.com/) 的可读性原则，以及 [FINN（ACM FPGA 2017）](https://arxiv.org/abs/1612.07119) 图 5、6 分开表达并行单元和内部数据流的方法。仅参考图版组织，不使用论文图片、实验数据或商标。

- `assets/conefdk-walnut.png`: three orthogonal slices reconstructed by ConeFDK from Alexander Meaney's University of Helsinki walnut projections (https://doi.org/10.5281/zenodo.6986012), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Binned, normalized and reconstructed; no endorsement.
- `assets/conefdk-sweep.gif`: animated axial slice sweep of the same reconstruction; same Meaney / Helsinki CC BY 4.0 source and attribution as the static three-plane image above.
- `assets/conefdk-walnut-peak.svg`: all 512 measured-walnut plane maxima from ConeFDK versus ASTRA, without smoothing. Derived from the same Meaney / Helsinki CC BY 4.0 data; color and coordinates added by ConeFDK.

- `assets/conefdk-pore-pair.png`: same 29 × 29 pixel crop of `set1sample3raw_0455.tif` in four panels, derived from Felix H. Kim et al., NIST, [10.18434/M32162](https://doi.org/10.18434/M32162). On 2026-11-24, contrast-windowed, enlarged and overlaid with the published labels or ConeFDK C/D predictions; no NIST endorsement. See the [rendering script](https://github.com/EtherealBian/cone-fdk/blob/measurement-lab/scripts/pore_example.py).

- `work/cone-fdk.html#pore-errors`: D/E measurements are generated from [per-specimen development records and paired reference IDs](https://github.com/EtherealBian/cone-fdk/tree/measurement-evidence-3/pores/evidence) with `tools/update_conefdk_measurement.py`. The comparator is the NIST digital segmentation.

- `assets/conefdk-transfer-merge.png`: specimen 5, axial slice 280 of the NIST CoCr data (Felix H. Kim et al., [10.18434/M32162](https://doi.org/10.18434/M32162)). ConeFDK contrast-windowed and enlarged the same crop in four panels, with digital-reference and experimental prediction overlays. See the [coordinates and 3D overlap counts](https://github.com/EtherealBian/cone-fdk/blob/boundary-transfer-pilot-1/pores/evidence/transfer-pilot/sample5-merge.json); no NIST endorsement.

- `assets/plates/vcu118-rocket-boot.svg`：本站原创启动路径图。根据 VCU118 Rocket 工程的入口地址和流水级绘制，非板上实拍或实测时序。

<a id="sparkfuse-artwork"></a>

### SparkFuse：实物与推理实测

- `assets/plates/sparkfuse-system.webp`（1200 × 750）与 `assets/plates/sparkfuse-system-full.webp`（2080 × 1300）是同一张总览。实物照片：[Nvidia DGX Spark oblique view dllu](https://commons.wikimedia.org/wiki/File:Nvidia_DGX_Spark_oblique_view_dllu.jpg)，Daniel Lu（dllu），Wikimedia Commons，[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。改动：去除桌面背景、缩放、添加投影和实验图解。合成图版由 EtherealBian 按同一许可发布。照片用于识别设备型号，不是本次实验现场照。
- `assets/plates/sparkfuse-qkv-atlas.webp` 是原创 CUDA 工程剖面图。颜色区分 Q/K/V 三组权重，区间标的是列索引。总览与剖面共用一套绘图代码。数据分别来自[四层 BERT](https://github.com/EtherealBian/spark-fuse/blob/dcc775fb960986ed85d16b217ec17e3d295a058b/reports/stacked-bert-gb10.json)、[Qwen 双请求](https://github.com/EtherealBian/spark-fuse/blob/dcc775fb960986ed85d16b217ec17e3d295a058b/reports/qwen32b-fork/timing.json)和[GLM 固定长度请求](https://github.com/EtherealBian/spark-fuse/blob/dcc775fb960986ed85d16b217ec17e3d295a058b/reports/glm45-355b/timing.json)。
- 重绘：安装 Pillow 后，运行 `python tools/draw_sparkfuse.py <上述提交的reports目录> <原始照片.jpg> <输出目录>`。使用照片页 2026-05-19 20:07 UTC 版的原尺寸文件（SHA-256 `6c0e2a9efe3a29fafc07a34d71e7e31903b7b4d4d2a55368b34182a39dc7005a`）。生成器校验照片和报告，输出含照片的 `sparkfuse-system.svg` 与独立的 `qkv-warm-detail.svg`。在已安装 Noto Sans SC、Bahnschrift、Consolas 的环境，使用 Sharp 以 180 dpi 读取总览 SVG，先渲染为 2080 × 1300，再分别按两档宽度导出 WebP（quality 91、smartSubsample、effort 6）。

### 首页工程图版 03–09

安装 Pillow 后运行 `python -B tools/draw_project_covers.py`，即可从本站素材重建 03、04、05、07、09 五张独立 SVG 和核桃扫层静帧。01、02 保留原图；06、08 直接引用原作品，不经这套生成器转绘。

| 图版 | 素材、数据与图示范围 |
|---|---|
| 03 李萨如 | 工作台与示波器局部取自 `lissajous-hardware.jpg`。两路时域信号与主 X–Y 图采用同一对 1:2 正弦信号。其余波形、相量与连续帧为示意；控制流程依据同一版归档的 [DPLL RTL](https://github.com/EtherealBian/fpga-lissajous-controller/blob/d28a09db401a55449636eb1bcb8951629dd83aec/rtl/continuous_iq_dpll.sv) 与 [Jetson 视觉流程](https://github.com/EtherealBian/fpga-lissajous-controller/blob/d28a09db401a55449636eb1bcb8951629dd83aec/vision/README.md)。 |
| 04 图像处理 | `elinx-competition-demo.png` 为竞赛实拍；右侧边缘图由同一屏幕裁片离线计算（两向 Sobel 梯度绝对值之和 > 80），非板上截图。串口、双路输出及跨域依据[工程协议](https://github.com/EtherealBian/elinx-vision-stream/blob/11b7c3dd3abe4609ec54cea3117e6ea57d33084b/docs/ARCHITECTURE.md)，波形仅示意事件先后。`vision-density-3.png` 保存从独立 CNN 的[归档 RAW8 样本](https://github.com/EtherealBian/elinx-vision-stream/blob/11b7c3dd3abe4609ec54cea3117e6ea57d33084b/fpga/cnn_standalone/new_capture/3/raw8_digit_3_20260622_155426_733_0018.raw)导出的 32 × 32 特征值：取 (320, 104) 起的 640 × 512 ROI，每格统计像素值 ≤ 112 的数量并右移三位。墨绿色仅表示密度，不表示预测类别。 |
| 05 超声阵列 | `n60-hardware.jpg` 实拍。换能器斜视图投影自 [N60 工程的 12 个局部坐标、5 个子阵朝向与碗面半径](https://github.com/EtherealBian/n60-ultrasonic-phased-array/blob/05a0002d54e6c3cd4d754f1168ba83c06418adcf/generate_n60_csv.py)，仅表示标称几何。串口帧与校验后整组提交见[协议解析器](https://github.com/EtherealBian/n60-ultrasonic-phased-array/blob/05a0002d54e6c3cd4d754f1168ba83c06418adcf/adc_capture/adc_capture.srcs/sources_1/new/uart_protocol_parser.sv)；音频处理见[顶层](https://github.com/EtherealBian/n60-ultrasonic-phased-array/blob/05a0002d54e6c3cd4d754f1168ba83c06418adcf/adc_capture/adc_capture.srcs/sources_1/new/top_ultrasound_array.sv)。三行波形按[PWM 模块](https://github.com/EtherealBian/n60-ultrasonic-phased-array/blob/05a0002d54e6c3cd4d754f1168ba83c06418adcf/adc_capture/adc_capture.srcs/sources_1/new/pwm60_generator.sv)对同一周期分别改变中心和脉宽，是逻辑示意，非示波器或声场实测。 |
| 06 UAVCount | 原始 `assets/uavcount-pipeline.webp` / `assets/uavcount-pipeline.svg`，原样展示水岸检测与计数四步流程。水岸画面是合成示意；回归基于 156 段半合成视频。三帧判据另见 `uavcount-counting.svg`。 |
| 07 ConeFDK | 上述 Helsinki 核桃数据（Alexander Meaney，CC BY 4.0）。轴向静帧取自 `conefdk-sweep.gif`，冠状与矢状断面取自 `conefdk-walnut.png`。逐层强度差折线保留 `conefdk-walnut-peak.svg` 的全部 512 个点；射线几何与插值局部是示意。 |
| 08 推理编译器 | 直接使用上述 `sparkfuse-system.webp`，点击放大读取 `sparkfuse-system-full.webp`。同一张原图，含 Daniel Lu 的 DGX Spark 型号照片（CC BY-SA 4.0）；详见上节。 |
| 09 Rocket Linux | 左上摘录[板上验收 JSON](https://github.com/EtherealBian/vcu118-rocket-soc/blob/5862e904c97ca7648daaa45c04587dbfe4fa081f/docs/portable-linux-rocket-boot.json)，不是终端照片。主图是功能连接，不是器件布局；下方是[另一组同板、同 bit 的配对启动记录](work/vcu118-rocket.html)，不含 JTAG 配置时间。 |
