"""Refresh the D/E pore measurement ledger from an audited ConeFDK checkout."""

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

CONTROL = (
    "https://github.com/EtherealBian/cone-fdk/blob/ff4d996e3fcc762c00a28ea129272dfca75dd423/pores/SHELL-PILOT.md"
)


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
            raise SystemExit("Published D/E ledger is stale")
    else:
        PAGE.write_text(result, encoding="utf8")
