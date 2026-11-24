# 图像与来源

原站基线：`1b77a3832f730435245b787ccb25bc0b1f26c315`。保留当前主页仓库内所有原始照片、中文/英文架构图、矢量流程图和品牌图。为适配浏览器新增的图版不会回写源项目或替换原始实验材料。

| 新图版（`assets/plates/`） | 依据与处理 |
|---|---|
| `scope.webp`、`array.webp`、`vision.webp` | 由本站原有 `lissajous-hardware.jpg`、`n60-hardware.jpg`、`elinx-competition-demo.png` 派生：缩放、轻微对比与锐化、WebP 压缩。卡片取景不影响原图入口。 |
| `../pmux-overview-zh.webp`、`../pmux-overview-zh.png` | Yosys 保留网站仓库的原图。首页完整展示原有 WebP，高清入口是原始 4080 × 2751 PNG，不裁切、不叠标。 |
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
- 太一量生品牌图仍链接回原站保留的品牌图来源。邮箱拼写沿用原站的 `EtheralBian@njust.edu.cn`。

记录页的 WebP 用作页内预览，放大链接指向保留在本地的对应原始文件：`wired-dpll.png`、`cnn-pipeline.png`、`fig_array_top.png` 和 `competition-app.jpg`。来源分别与上表四个项目链接一致。

### Vitis 多面板图版

`tools/draw_vitis.py` 输出五幅独立 SVG。主图是一张可独立保存的五面板图：a–c 为算法原理、数据通路、固定用例总周期与验证条件；d 为独立的决赛整机数据流；e 内嵌竞赛应用截图的幅度谱区域，保留原始曲线和标记。e 的采样率 1 kHz、1,024 点与 d 的 48 kHz、4,096 点演示配置分开标注。`vitis-sha.svg`、`vitis-lz4.svg`、`vitis-cholesky.svg` 及 `vitis-zynq-system.svg` 按[项目归档](https://github.com/EtherealBian/vitis-hls-kernel-optimization/tree/177cd62badb31cd49874cee63ad8f9e81079a383)的算子说明、协同仿真记录与决赛 PL/PS 接口重绘，详细出处位于各图旁边。

制图参考：[Nature Research Figure Guide](https://research-figure-guide.nature.com/) 的可读性原则，以及 [FINN（ACM FPGA 2017）](https://arxiv.org/abs/1612.07119) 图 5、6 分开表达并行单元和内部数据流的方法。仅参考图版组织，不使用论文图片、实验数据或商标。

- `assets/conefdk-walnut.png`: three orthogonal slices reconstructed by ConeFDK from Alexander Meaney's University of Helsinki walnut projections (https://doi.org/10.5281/zenodo.6986012), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Binned, normalized and reconstructed; no endorsement.
- `assets/conefdk-sweep.gif`: animated axial slice sweep of the same reconstruction; same Meaney / Helsinki CC BY 4.0 source and attribution as the static three-plane image above.

- `assets/conefdk-pore-pair.png`: same 29 × 29 pixel crop of `set1sample3raw_0455.tif` in four panels, derived from Felix H. Kim et al., NIST, [10.18434/M32162](https://doi.org/10.18434/M32162). On 2026-11-24, contrast-windowed, enlarged and overlaid with the published labels or ConeFDK C/D predictions; no NIST endorsement. See the [rendering script](https://github.com/EtherealBian/cone-fdk/blob/measurement-lab/scripts/pore_example.py).

- `work/cone-fdk.html#pore-errors`: D/E measurements are generated from [per-specimen development records and paired reference IDs](https://github.com/EtherealBian/cone-fdk/tree/measurement-evidence-3/pores/evidence) with `tools/update_conefdk_measurement.py`. The comparator is the NIST digital segmentation.
