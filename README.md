# Etherealbian · Hardware Field Notes

Xiangyu Bian 的个人作品集，静态 HTML / CSS / JavaScript。没有构建步骤、CDN 或远程字体。

## 预览与发布

在仓库根目录运行 `python -m http.server 8871 --bind 127.0.0.1`，打开 `http://127.0.0.1:8871/`。现有 GitHub Pages 用户站点从 `main` 根目录发布，保留 `.nojekyll`。本地预览和修改不会自动发布。

## 内容维护

- `index.html`：独立封面用 “Signals. Logic. Quantum.” 搭配原有环形线稿，独立的 About Me 在姓名旁保留原头像，左侧列出简介和教育经历，右侧介绍研究方向。章节依次为 About Me、Experience、Research、Projects、Honors，联系方式在页脚。历史锚点仍在；项目标题通向独立记录页，仓库链接和原图入口分开。
- `work/*.html`：七份可单独访问的静态记录。每份含完整图版、图注、读图笔记、项目特有的对照表，以及相邻项目导航。直接修改相应 HTML 即可，无需重新生成。
- ConeFDK 按编号 07 排在 Projects 的第七位。详情页的实验记录由 `python tools/update_conefdk_measurement.py <ConeFDK 实验分支的 pores/evidence 目录>` 生成；加 `--check` 可验证页面是否与证据一致。核桃 GIF 同时保留静态替代图。
- `style.css`、`dossier.css`：站点通用与工程记录页样式。`portfolio.js` 仅增强首页导航、筛选、标题动效；`viewer.js` 增强标记为 `data-plate` 的原图链接。无 JavaScript 时正文、记录页、原图和目录仍然可用。
- `assets/plates/vitis-hls-architecture.svg`：单图讲解三种算子的原理、微架构与周期，以及决赛频谱仪信号链和真实竞赛界面读数。另有三幅算子微架构与一幅决赛系统图；执行 `python tools/draw_vitis.py` 可重绘五幅 SVG。五个竞赛项目在首页及详情页均显示已核对的荣誉。Yosys 使用仓库原有 `pmux-overview-zh.webp` / `.png`。其他素材来源见 [图像说明](ASSETS.md)。
- 主页的 View CV 和 Download CV 共用 `assets/etherealbian-cv.pdf`（B5 双页 XeLaTeX 版）；`cv.html` 为旧地址保留跳转。替换 PDF 时同步更新链接的版本参数。

## 自检

```sh
python tools/check_site.py
node --check portfolio.js
node --check viewer.js
```

静态检查遍历首页、在线简历和所有记录页，检查本地文件、文件名大小写、跨页锚点及 SVG。浏览器验收应另外覆盖：手机菜单、项目筛选、原图打开与 Esc 返回、无 JS 访问，以及 B5 简历 PDF 的两页版式、字体和链接。
