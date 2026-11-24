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


def latent_section(root):
    repo = "https://github.com/EtherealBian/cone-fdk"
    tag = "measurement-evidence-5"
    rows = []
    replay = json.loads((root / "candidate-g/raw-weight-replay.json").read_text(encoding="utf8"))
    for i in (2, 3, 5):
        g, f = (json.loads((root / name / f"sample{i}.json").read_text(encoding="utf8")) for name in ("candidate-g", "candidate-f"))
        rr = replay["specimens"][str(i)]
        if (g["role"] != "development" or g["specimen"] != i or g["source"] != f["source"] or g["evaluation_z"] != [400, 528] or len(g["final_gates"]) != 11 or replay["pipeline_id"] != g["pipeline_id"] or rr["mask"] != g["seal"]["mask"] or rr["decision_disagreements"] != 0):
            raise ValueError("Mismatched G replay or development ROI")
        a, b = f["objects"], g["objects"]
        rows.append(f'<tr><th scope="row">试件 {i}</th><td>{b["matches"]} / {b["eligible_reference"]}<small>通过 {sum(g["final_gates"].values())} / 11 项</small></td><td>{a["p95_abs_volume_error_pct"]:.2f}% → {b["p95_abs_volume_error_pct"]:.2f}%</td></tr>')
    return f'''<div id="pore-latent"><h3>先校正灰度，再找孔边界</h3><p>候选 G 只用每件的 24 张校准切片学习灰度修正，再用固定的局部阈值划出孔。2 号仅差体积误差 P95，3 号却比 F 少匹配了 6 个孔。不能按试件挑表现最好的模型。</p>
<table><caption>同一正式区域 · 全部匹配孔的体积误差 P95，目标 ≤15%</caption><thead><tr><th scope="col">开发试件</th><th scope="col">G 匹配 / 参考</th><th scope="col">体积误差 P95：F → G</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<p>从原始灰度和已封存权重重算，三件的 CPU 与 CUDA 在正式区域均给出完全相同的孔掩膜。3 号的量化中间图有 4 处数值不同，最终二值结果没有改变。算法仍未过关，4、6 号继续封存。</p>
<p>把去噪权重拟合得更细，也没有解决误差。2 号在拟合区的 Dice 从 0.91177 升到 0.92562，换到隔开的检查区却从 0.94405 降到 0.93890。<a href="{repo}/blob/55e4d40d4a1b204aefef8876971dbcf27d43a046/pores/INVERSE-WEIGHT-PILOT.md">三件试件的对照记录 ↗</a></p><div class="bench-links"><a href="{repo}/blob/{tag}/pores/RESULTS-G.md">查看原图重放与全部失败项 ↗</a><a href="{repo}/releases/tag/{tag}">下载 G 的逐层阅片器、权重和结果 ↗</a></div></div>'''


def shared_section(root):
    repo = "https://github.com/EtherealBian/cone-fdk"
    tag = "measurement-evidence-6"
    folder = root / "candidate-h"
    read = lambda name: json.loads((folder / name).read_text(encoding="utf8"))
    manifest = read("predictions.json")
    replay = read("raw-weight-replay.json")
    if set(manifest["specimens"]) != {"2", "3", "5"} or len({v["weights"] for v in manifest["specimens"].values()}) != 1:
        raise ValueError("H requires one set of weights for all development specimens")
    rows = []
    for i in (2, 3, 5):
        h = read(f"sample{i}.json")
        rr = replay["specimens"][str(i)]
        if not (h["role"] == "development" and h["specimen"] == i and h["origin_xyz"] == [360, 376, 400] and h["evaluation_z"] == [400, 528] and h["seal"] == manifest["specimens"][str(i)] and h["pipeline_id"] == replay["pipeline_id"] == manifest["pipeline_id"] and rr["mask"] == h["seal"]["mask"] and rr["voxels"] == 8388608 and rr["decision_disagreements"] == 0 and len(h["final_gates"]) == 11):
            raise ValueError("H report, raw replay and sealed predictions do not agree")
        o = h["objects"]
        rows.append(f'<tr><th scope="row">试件 {i}</th><td>{o["matches"]} / {o["eligible_reference"]}<small>通过 {sum(h["final_gates"].values())} / 11 项</small></td><td>{o["p95_abs_volume_error_pct"]:.2f}%</td></tr>')
    with (folder / "sample5-paired-g-h.csv").open(encoding="utf8", newline="") as f:
        pairs = list(csv.DictReader(f))
    lost = {r["reference_id"]: r for r in pairs if r["status"] == "lost"}
    shared = [r for r in pairs if r["status"] == "shared"]
    if set(lost) != {"21", "92", "105"} or len(shared) != 7:
        raise ValueError("Wrong paired reference population")
    a,b = (quantiles([100*abs(int(r[f"{k}_signed_delta_vox"]))/int(r["reference_voxels"]) for r in shared], n=100, method="inclusive")[94] for k in ("g", "h"))
    g5 = json.loads((root / "candidate-g/sample5.json").read_text(encoding="utf8"))["objects"]
    hit = lost["21"]
    return f'''<div id="pore-shared"><h3>三个试件共用一套权重，小孔量准了吗？</h3><p>候选 H 用每件原有的 24 张校准切片联合训练，增加了对完整小孔体积的监督。试件 5 只有一个符合训练条件的小孔；重复抽取它 150 次，仍然只有一个独立样本。</p>
<table><caption>共享权重 H · 已匹配孔的体积误差 P95，目标 ≤15%</caption><thead><tr><th scope="col">开发试件</th><th scope="col">匹配 / 参考</th><th scope="col">体积误差 P95</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<p><b>少找到三个孔，也能让误差看起来更小。</b>试件 5 的总体 P95 从 G 的 {g5["p95_abs_volume_error_pct"]:.2f}% 降至 H 的 {b:.2f}%；只比较都找到的七个孔，误差却从 {a:.2f}% 升至 {b:.2f}%。例如参考孔 21 有 {hit["reference_voxels"]} 个体素，G 找到 {hit["g_pred_voxels"]} 个，H 只找到 {hit["h_miss_best_iou_pred_vox"]} 个，没达到 64 体素的匹配门槛。</p>
<p>原始档和封存权重可以重放，但三件都没有通过全部精度指标。保留试件 4、6 尚未开启。</p><div class="bench-links"><a href="{repo}/blob/{tag}/pores/RESULTS-H.md">查看逐孔反例和独立重放 ↗</a><a href="{repo}/releases/tag/{tag}">下载 H 的三件离线复核包 ↗</a></div></div>'''


def section_followup(root):
    study = root / "section-area"
    row = json.loads((study / "sample5.json").read_text(encoding="utf8"))
    trace = json.loads((study / "trace-5-15.json").read_text(encoding="utf8"))
    fiji = json.loads((root / "bernsen-check.json").read_text(encoding="utf8"))
    ipol = json.loads((root / "ipol-check.json").read_text(encoding="utf8"))
    if any(v["implementation_disagreements"] for v in fiji.values()) or any(v["advance"] for v in ipol.values()):
        raise ValueError("Published denoising conclusion has changed")
    decisions = sum(sum(v["strict"][k] for k in ("tp", "tn", "fp", "fn")) for v in fiji.values())
    before, after = row["screen"]["shared_p95"]
    lost = trace["arms"]["area"][0]
    if lost["unclipped"] or row["arms"]["area"]["references"]["15"]["voxels"] is not None:
        raise ValueError("Reference 15 is no longer a clipped miss")
    base = "https://github.com/EtherealBian/cone-fdk/blob/d02f9837e6b235a0fb0602c8d6b4e72c27e795e6/pores"
    return f'''<div id="pore-sections"><h3>多认出了孔里的体素，为什么反而漏掉了这个孔？</h3>
<p>在另一段 96 层的开发图像上，试件 5 的两种方法都找到了 {len(row["screen"]["shared_ids"])} 个孔。加入截面面积监督后，这些孔的体积误差 P95 从 {before:.2f}% 降至 {after:.2f}%。但有一个原来能单独测量的孔，共 {trace["reference_voxels"]} 个体素，其中 {lost["intersection"]} 个被连进一个触及边界的 {lost["voxels"]:,} 体素对象，无法再单独匹配。试件 2、3 的同孔误差也上升，因此没有升级算法。</p>
<p>换成历史 Fiji 插件，在相同去噪图像上的 {decisions:,} 个判定与本项目全部一致。再换用论文引用的原版 IPOL 去噪器，三件开发切片的 Dice 都没有提高。</p>
<div class="bench-links"><a href="{base}/RESULTS-SECTION-AREA.md">逐孔数据、权重与封存掩膜 ↗</a><a href="{base}/RESULTS-BERNSEN.md">Fiji 对照 ↗</a><a href="{base}/RESULTS-IPOL.md">去噪器对照 ↗</a></div></div>'''


def context_followup(root):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf8"))
    bound = read("byte-radius/coverage-bounds.json")["3"]["2"]
    trace = read("axial-raw/trace-5-15.json")
    records = [read(f"axial-raw/sample{i}.json") for i in (2,3,5)]
    wide = read("window-units/check.json")
    if (not bound["coverage_gate_impossible"] or any(r["screen"]["advance"] for r in records)
        or any(v["wide"]["dice"] >= v["control"]["dice"] for v in wide.values())):
        raise ValueError("Development evidence changed; review interpretation")
    before, after = [trace["arms"][k][0] for k in ("plane", "axial")]
    base = "https://github.com/EtherealBian/cone-fdk/blob/2e35689367af16b4d09cae921ade1a3c701b3951/pores"
    tails = [r["screen"]["shared_p95"] for r in records]
    return f'''<div id="pore-context"><h3>一个孔重新分开了，体积量得有多准？</h3>
<p>试件 5 的同一个 {trace["reference_voxels"]} 体素孔，在新的平面对照里与一个触边对象连在一起，共 {before["voxels"]:,} 体素。给网络加入前后原始切片后，这个孔被单独测为 {after["voxels"]} 体素，交并比 {after["iou"]:.3f}，体积仍低估 {100*(1-after["voxels"]/trace["reference_voxels"]):.2f}%。</p>
<p>三件开发迁移区的 Dice 都提高了，但只比较两臂都找到的同一批孔，体积误差 P95 在试件 2 降至 {tails[0][1]:.2f}%，在试件 3、5 却分别升至 {tails[1][1]:.2f}%、{tails[2][1]:.2f}%。单纯扩大去噪窗口也没能改善这三件的校准检查结果。</p>
<p>在另一段正式开发区，只允许固定基线改变 ±2 个灰度级时，即使每个体素都选最有利的结果，试件 3 的参考孔匹配数上限也只有 {bound["match_count_upper"]}/{bound["reference_count"]}，低于要求的 90%。这是数学上限，不是算法测得的覆盖率。</p>
<div class="bench-links"><a href="{base}/RESULTS-AXIAL-RAW.md">相邻切片与逐孔配对 ↗</a><a href="{base}/RESULTS-BYTE-RADIUS.md">灰度扰动上限 ↗</a><a href="{base}/RESULTS-WINDOW-UNITS.md">窗口宽度对照 ↗</a></div></div>'''


def source_followup(root):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf8"))
    reg = read("figure-locator/registration.json")
    ck = read("figure-gray/check.json")
    results = [read(f"census-train/sample{i}.json")["screen"] for i in (2, 3, 5)]
    if not reg["advance"] or ck["advance"] or [r["advance"] for r in results] != [True, False, False]:
        raise ValueError("Source comparison or coverage experiment changed")
    m = ck["partitions"]["check"]["methods"]
    rms = [m[k]["all"]["change_rmse"] for k in ("median", "r10h30", ck["selected"])]
    a, b = results[0]["shared_p95"]
    trace = read("census-train/trace-5-15.json")["arms"]["census"][0]
    base = "https://github.com/EtherealBian/cone-fdk/blob/83775b0c15fdf6383e14343f1aa5625239a23f77/pores"
    return f'''<div id="pore-source-check"><h3>能在原始扫描中找到论文里的那一层吗？</h3>
<p>在试件 2 的 900 张原图中找到了第 {reg["z"]} 层。只对齐原图，再用同一映射核对论文的中值图，未参与拟合的右侧相关系数为 {reg["test_right_median"]["ncc"]:.4f}。比较去噪前后的灰度变化，右侧误差从不加去噪的 {rms[0]:.2f} 降到固定去噪的 {rms[1]:.2f}；调整参数后为 {rms[2]:.2f}，仅比固定方法再降 {100*(1-ck["check_ratios"]["r10h30"]):.2f}%，没有达到预定的 10%。</p>
<p>另一次训练遍历了全部校准体素。试件 2 的 {len(results[0]["shared_ids"])} 个共同匹配孔，体积误差 P95 从 {a:.2f}% 降到 {b:.2f}%；试件 3、5 的同孔误差却上升。试件 5 有 {trace["intersection"]} 个属于同一参考孔的体素被连进 {trace["voxels"]:,} 体素的触边对象，不能再单独测量。两项实验都未升级正式候选。</p>
<div class="bench-links"><a href="{base}/RESULTS-FIGURE-GRAY.md">截面定位、灰度对照与独立重算 ↗</a><a href="{base}/RESULTS-CENSUS-TRAIN.md">遍历训练的逐孔结果 ↗</a></div></div>'''


def filter_followup(root):
    def read(name):
        return json.loads((root / name).read_text(encoding="utf8"))
    local = [read(f"local-connectivity/sample{i}.json") for i in (2, 3, 5)]
    patch = read("patch-profile/check.json")
    med = read("median-source/check.json")
    if any(r["screen"]["advance"] for r in local) or patch["advance"] or med["advance"]:
        raise ValueError("Research screen changed; review page text")
    a, b = local[2]["screen"]["shared_p95"]
    c, d = local[1]["screen"]["shared_p95"]
    before, after = [local[2]["arms"][k]["objects"] for k in ("census", "critical")]
    right = med["partitions"]["check"]
    m, n = [right[k]["all"]["change_rmse"] for k in ("cube27", med["selected"])]
    q = patch["paper"]
    u, v = [q["parts"]["check"]["methods"][k+str(q["selected"][k])]["all"]["change_rmse"] for k in ("uniform", "binomial")]
    if not all(r["binomial"]["dice"] < r["uniform"]["dice"] for r in patch["specimens"].values()):
        raise ValueError("Check-slice result changed")
    base = "https://github.com/EtherealBian/cone-fdk/blob/c4e69d07024dab63b62454d351d0da86de491d48/pores"
    return f'''<div id="pore-filter-review"><h3>体积误差小了，怎么还会多报三个孔？</h3>
<p>在开发迁移区给连接与间隙增加训练权重后，试件 5 的 {len(local[2]["screen"]["shared_ids"])} 个共同匹配孔，体积误差 P95 从 {a:.2f}% 降至 {b:.2f}%。但预测中能与参考孔一一配对的比例从 {before["matches"]}/{before["eligible_prediction"]} 降到 {after["matches"]}/{after["eligible_prediction"]}；试件 3 的同孔误差则从 {c:.2f}% 升到 {d:.2f}%。因此保留原方法。</p>
<p>对照论文截面的两步灰度变化，把 27 点中值改为 19 点，右区误差从 {m:.2f} 升到 {n:.2f}；改变去噪补丁内的权重，从 {u:.2f} 升到 {v:.2f}。后者在三个试件各自的校准检查区也都降低了 Dice。这里没有使用保留试件。</p>
<div class="bench-links"><a href="{base}/RESULTS-LOCAL-CONNECTIVITY.md">逐孔误差与触边反例 ↗</a><a href="{base}/RESULTS-FILTER-PROFILE.md">两步灰度对照与校准数据 ↗</a></div></div>'''


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
{latent_section(root)}
{shared_section(root)}
{section_followup(root)}
{context_followup(root)}
{source_followup(root)}
{filter_followup(root)}
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
