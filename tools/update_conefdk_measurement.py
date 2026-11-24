"""Refresh the development pore measurement ledger from an audited ConeFDK checkout."""

import argparse
import csv
import json
from pathlib import Path
from statistics import quantiles

PAGE = Path(__file__).resolve().parents[1] / "work/cone-fdk.html"
START = "<!-- measured-pore-ledger:start -->"
END = "<!-- measured-pore-ledger:end -->"
RELEASE = "https://github.com/EtherealBian/cone-fdk/releases/tag/measurement-evidence-3"
REPORT = "https://github.com/EtherealBian/cone-fdk/blob/measurement-evidence-3/pores/RESULTS-E.md"

CONTROL = "https://github.com/EtherealBian/cone-fdk/blob/ff4d996e3fcc762c00a28ea129272dfca75dd423/pores/SHELL-PILOT.md"


def transfer_section(root):
    tag = "boundary-transfer-pilot-1"
    repo = "https://github.com/EtherealBian/cone-fdk"
    rows = []
    decisions = []
    for i in (2, 3, 5):
        r = json.loads(
            (root / "transfer-pilot" / f"sample{i}.json").read_text(encoding="utf8")
        )
        if (
            r["specimen"] != i
            or r["source_xyz"] != [360, 376, 256]
            or r["shape_zyx"] != [96, 256, 256]
            or set(r["trained_on"]) != {str(j) for j in (2, 3, 5) if j != i}
        ):
            raise ValueError("Wrong transfer population or donor leakage")
        t = r["screen"]
        decisions.append(t["decision"])
        n = len(t["shared_ids"])
        title = {
            "fail": "未通过",
            "pass": "通过筛选",
            "insufficient support": "样本不足",
        }[t["decision"]]

        def pct(x):
            return "—" if x is None else f"{x:.2f}%"

        rows.append(
            f'<tr><th scope="row">试件 {i}</th><td>{n} 个<small>{title}</small></td><td>{pct(t["shared_p95_pct"][0])} → {pct(t["shared_p95_pct"][1])}</td></tr>'
        )
    note = (
        "三个试件都通过这轮研究筛选；仍需按原协议验证。"
        if all(v == "pass" for v in decisions)
        else "这项修正没有同时通过三个试件的筛选，保留原算法。"
    )
    w = json.loads(
        (root / "transfer-pilot/sample5-merge.json").read_text(encoding="utf8")
    )
    ids = {v["reference"]: v for v in w["overlaps"]}
    flags = json.loads(
        (root / "transfer-pilot/bridge-review.json").read_text(encoding="utf8")
    )
    hit = next(r for r in flags["5"]["rows"] if r["pred"] == w["pred"])
    if hit["category"] != "tp" or w["reference"] != 42 or set(ids) != {42, 26}:
        raise ValueError("Merge illustration and review flag disagree")
    return f'''<div id="pore-transfer"><h3>用别的试件校准，小孔会量得更准吗？</h3><p>每件另取 96 层作开发实验。先保存三件的原始预测，再用另外两件的完整孔估计边界应移动多少，最后对修正后的掩膜重新测量。下表只比较修正前后都找到的同一批小孔。{note}</p>
<table><caption>新区域 z=256–351 · 64–127 体素的同一批参考孔</caption><thead><tr><th scope="col">目标试件</th><th scope="col">共同小孔</th><th scope="col">体积误差 P95：修正前 → 后</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<figure style="margin:1.5rem 0"><a href="../assets/conefdk-transfer-merge.png"><img src="../assets/conefdk-transfer-merge.png" width="528" height="600" style="display:block;width:min(100%,528px);height:auto" loading="lazy" alt="试件 5 的同一张切片：两个分离的蓝、黄参考孔被绿色预测连在一起；右下标出重叠和多出的背景体素。"></a><figcaption>试件 5 · 第 {w["source_z"]} 层。参考孔 42 有 {w["reference_voxels"]} 个体素，预测为 {w["predicted_voxels"]} 个，其中 {ids[26]["overlap_voxels"]} 个属于旁边的参考孔 26。一次测量既高估了一个孔，又漏报了另一个孔。</figcaption></figure>
<p>离线阅片器能在没有参考标注时提示这种粘连。它在这三段切片中提示了这一个案例；规则是在看到案例后设计的。后面的新切片实验专门检验它是否认错了孔。</p>
<p>这批切片不替代上方正式开发区的评分。离线包能逐层对照原图、数字标注和两种掩膜，也能定位未匹配的预测。<a href="{repo}/blob/{tag}/pores/RESULTS-TRANSFER.md">查看逐件结果和修正幅度的极限 ↗</a></p><div class="bench-links"><a href="{repo}/releases/tag/{tag}">下载跨试件实验的离线复核包 ↗</a></div></div>'''


def spatial_section(root):
    repo = "https://github.com/EtherealBian/cone-fdk"
    tag = "measurement-evidence-4"
    rows = []
    records = {}
    for i in (2, 3, 5):
        e, f, s = [
            json.loads((root / folder / f"sample{i}.json").read_text(encoding="utf8"))
            for folder in ("candidate-e", "candidate-f", "split-pilot")
        ]
        if (
            e["source"] != f["source"]
            or f["role"] != "development"
            or f["specimen"] != i
            or f["evaluation_z"] != [400, 528]
            or len(f["final_gates"]) != 11
            or s["origin_xyz"] != [360, 376, 552]
            or s["specimen"] != i
        ):
            raise ValueError("Incompatible development evidence")
        a, b = e["objects"], f["objects"]
        gates = sum(f["final_gates"].values())
        rows.append(
            f'<tr><th scope="row">试件 {i}</th><td>{b["matches"]} / {b["eligible_reference"]}<small>通过 {gates} / 11 项</small></td><td>{a["p95_abs_volume_error_pct"]:.2f}% → {b["p95_abs_volume_error_pct"]:.2f}%</td></tr>'
        )
        records[i] = s["ledger"]
    alerts = [r for r in records[2]["parents"] if r["single_split"]]
    missed = [r for r in records[2]["parents"] if r["event"] and not r["flagged"]]
    if (
        len(alerts) != 1
        or len(missed) != 1
        or any(r["counts"]["rescued"] for r in records.values())
    ):
        raise ValueError("Split evidence no longer supports the counterexample")
    err = alerts[0]
    left, right = err["proposed_daughter_volumes"]
    return f'''<div id="pore-spatial"><h3>换成卷积模型，同一个孔量得更准了吗？</h3><p>候选 F 在每件原有的 24 张校准切片上训练，再用自写 CUDA 卷积处理正式区域的 128 张切片。试件 3 多找回一个参考孔，但三个试件的逐孔体积误差 P95 仍超过 15%。</p>
<table><caption>正式区域 z=400–527 · 所有匹配孔，按试件计算</caption><thead><tr><th scope="col">开发试件</th><th scope="col">F 匹配 / 参考</th><th scope="col">体积误差 P95：E → F</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<p><b>新切片推翻了自动拆孔的依据。</b>另取每件的第 552–679 层，先封存预测再核对标注。在试件 2，算法漏掉了一个真正的粘连，却把原本匹配的 {err["voxels"]} 体素孔拆成 {left} 和 {right} 两块；小块没有对应的参考孔。试件 3、5 没有发生拆分。这个规则不进入正式测量。</p>
<p>保留试件 4、6 尚未用于确认。原图切片、逐孔表和失败案例均可离线复核。</p><div class="bench-links"><a href="{repo}/blob/{tag}/pores/RESULTS-F.md">查看同一批孔的配对结果 ↗</a><a href="{repo}/releases/tag/{tag}">下载 F 与拆孔实验复核包 ↗</a></div></div>'''


def ledger(root):
    rows = []
    common = []
    for i in (2, 3, 5):
        old, new = (
            json.loads(
                (root / f"candidate-{stage}" / f"sample{i}.json").read_text(
                    encoding="utf8"
                )
            )
            for stage in ("d", "e")
        )
        if (
            any(r["role"] != "development" or r["specimen"] != i for r in (old, new))
            or old["source"] != new["source"]
        ):
            raise ValueError("Cannot compare these records")
        a, b = old["objects"], new["objects"]
        n = b["eligible_reference"]
        rows.append(
            f'<tr><th scope="row">试件 {i}</th><td>{a["matches"]} → {b["matches"]}<small>共 {n} 个参考孔</small></td><td>{a["p95_abs_volume_error_pct"]:.2f}% → {b["p95_abs_volume_error_pct"]:.2f}%</td></tr>'
        )
        with (root / "candidate-e" / f"sample{i}-paired-d-e.csv").open(
            encoding="utf8", newline=""
        ) as f:
            pairs = list(csv.DictReader(f))
        shared = [r for r in pairs if r["status"] == "shared"]
        gained = sum(r["status"] == "gained" for r in pairs)
        lost = sum(r["status"] == "lost" for r in pairs)
        if (
            len(pairs) != n
            or len(shared) + gained != b["matches"]
            or len(shared) + lost != a["matches"]
        ):
            raise ValueError("Incomplete pair ledger")
        v = [
            quantiles(
                [
                    100
                    * abs(int(r[f"{m}_signed_delta_vox"]))
                    / int(r["reference_voxels"])
                    for r in shared
                ],
                n=100,
                method="inclusive",
            )[94]
            for m in ("d", "e")
        ]
        common.append(
            f'<tr><th scope="row">试件 {i}</th><td>{len(shared)} 个<small>新增 {gained}，丢失 {lost}</small></td><td>{v[0]:.2f}% → {v[1]:.2f}%</td></tr>'
        )

    census = json.loads((root / "shell-pilot/census.json").read_text(encoding="utf8"))
    small = []
    for i in (2, 3, 5):
        record = json.loads(
            (root / "shell-pilot" / f"sample{i}.json").read_text(encoding="utf8")
        )
        row = census[str(i)]
        if row["segmented_sha256"] != record["reference_sha256"] or record[
            "calibration_z"
        ] != [160, 184]:
            raise ValueError("Different calibration population")
        small.append(str(row["whole"]["complete_64_127"]))

    def table(title, body, col):
        return f'<table><caption>{title}</caption><thead><tr><th scope="col">开发试件</th><th scope="col">{col}</th><th scope="col">体积误差 P95（D → E）</th></tr></thead><tbody>{"".join(body)}</tbody></table>'

    return (
        START
        + f'''\n<section class="pore-ledger" id="pore-errors" aria-labelledby="pore-errors-title"><span class="section-label">实验记录 <i>/</i> D → E</span><h3 id="pore-errors-title">换一种边界算法，同一个孔测准了吗？</h3>
<p>候选 E 按局部纹理选取相似图像块，并在校准时给小孔边界加权。下面逐件比较两种算法：先看全部匹配孔，再看两种算法都找到的同一批孔。验收要求体积绝对相对误差的第 95 百分位（P95）不超过 15%；三个开发试件均未达标。</p>
{table("各方法的全部匹配孔", rows, "匹配数（D → E）")}
<details><summary>只比较两种算法都匹配到的孔</summary>{table("相同参考孔的配对比较", common, "共同匹配数")}<p>新增和丢失的匹配没有放进这一行的百分位；它们仍计入正式验收的覆盖率。</p></details>
<p>再回到每件的 24 张校准切片：试件 2、3、5 分别只有 {"、".join(small)} 个体积在 64–127 体素之间、且没有被裁切的小孔。试件 5 并非没有孔，而是这段校准图像里没有可完整测量的该尺寸小孔。<a href="{CONTROL}">查看边界放宽、收紧的对照结果 ↗</a></p>
{transfer_section(root)}
{spatial_section(root)}
<div class="bench-links"><a href="{REPORT}">逐孔误差、漏检与失败项 ↗</a><a href="{RELEASE}">下载三个试件的离线复核包 ↗</a></div></section>\n'''
        + END
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("evidence", type=Path)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = PAGE.read_text(encoding="utf8")
    before, rest = text.split(START)
    _, after = rest.split(END)
    result = before + ledger(a.evidence) + after
    if a.check:
        if text != result:
            raise SystemExit("Published pore ledger is stale")
    else:
        PAGE.write_text(result, encoding="utf8")
