"""Draw the portfolio overview and the QKV detail from the public SparkFuse reports.

Usage: python tools/draw_sparkfuse.py REPORTS_DIRECTORY ORIGINAL_PHOTO OUTPUT_DIRECTORY
Requires Pillow; see ASSETS.md for the pinned photo, license and rendering instructions.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

PAPER = '#FDFBF7'
PANEL = '#F5EFE5'
INK = '#332922'
SUB = '#6A584A'
HAIR = '#D9CDBD'
RULE = '#977D69'
RUST = '#87432F'
WHITE = '#FFFCF7'
CN = 'Noto Sans SC, Source Han Sans SC, Microsoft YaHei, sans-serif'
DIN = 'Bahnschrift, Segoe UI, Noto Sans SC, sans-serif'
MONO = 'Consolas, Noto Sans SC, monospace'
# Top, edge, ink, output tint. The initials also identify the channels in grayscale.
CHANNELS = (
    ('Q', 'Query', '#E99A85', '#C57662', '#552D23', '#F8E1D8'),
    ('K', 'Key',   '#F3BD89', '#C88E5C', '#50341F', '#F8E8D6'),
    ('V', 'Value', '#E4CC98', '#BBA172', '#4A3C24', '#F2EBD7'),
)


def measured(path):
    cases = json.loads(path.read_bytes())['cases']
    case = next(c for c in cases if (c['depth'], c['m'], c['seed']) == (4, 33, 1981121))
    regions = [r for r in case['metadata']['packed_groups']['regions'] if r.get('kind') == 'packed_int32_projection']
    assert len(regions) == 4
    for r in regions:
        assert r['shape'] == [33, 768, 2304] and r['gemm'] == 'aten._int_mm.default'
        assert [w['packed_column_offset'] for w in r['source_weights']] == [0, 768, 1536]
        assert all(w['shape'] == [768, 768] for w in r['source_weights'])
        assert len(r['branches']) == 3 and all(b['shape'] == [33, 768] and b['narrow_dtype'] == 'bf16' for b in r['branches'])
    checks = case['gates']['packed_groups']['request']['outputs']
    assert len(checks) == 8 and all(len(row) == 8 for row in checks)
    assert all(t['geometry_match'] and t['different_bytes'] == 0 for row in checks for t in row)
    profiles = case['ordinary']['profiles']
    totals = [profiles[k]['count'] for k in ('eager', 'independent', 'shared', 'packed_groups')]
    names = profiles['packed_groups']['kernel_names']; assert sum(names.values()) == totals[-1]
    signatures = ('gemm_s8', 'gemm_bf16', 'layer_norm_kernel', 'softmax_warp', 'token_quant(', 'packed_affine_projection(')
    assert all(sum(k in n for k in signatures) <= 1 for n in names)
    groups = [sum(v for n, v in names.items() if k in n) for k in signatures]
    groups.append(totals[-1] - sum(groups))
    assert totals == [233, 88, 72, 64] and groups == [4, 20, 8, 4, 4, 4, 20]
    return totals, groups


class Plate:
    def __init__(self, w, h, title, description):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">',
                      f'<title id="t">{escape(title)}</title><desc id="d">{escape(description)}</desc>',
                      '<defs><clipPath id="packed"><rect width="660" height="62" rx="12"/></clipPath></defs>']
        self.box(0, 0, w, h, PAPER)

    def put(self, s): self.parts.append(s)

    def group(self, transform): self.put(f'<g transform="{transform}">')

    def end(self): self.put('</g>')

    def box(self, x, y, w, h, fill, r=0, stroke='none', sw=1):
        self.put(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, label, size, fill=INK, weight=500, font=CN, anchor='start'):
        self.put(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family={quoteattr(font)} font-weight="{weight}" font-size="{size}" fill="{fill}">{escape(str(label))}</text>')

    def line(self, d, color=RULE, width=1.5, fill='none'):
        self.put(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')

    def dot(self, x, y, r, color): self.put(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def save(self, path): path.write_text('\n'.join([*self.parts, '</svg>']), encoding='utf-8')


def stage(p, y, title, desc, icon):
    p.box(0, y, 33, 33, '#F0E5D8', 9)
    p.group(f'translate(6 {y+6})')
    for d in (
        ('M10.5 1v19M2.5 6l16 9M2.5 15l16-9','M7.5 3.5l3 2.5 3-2.5M7.5 17.5l3-2.5 3 2.5'),
        ('M2 4h17v13H2zM8 5v11M13 5v11',),
        ('M10.5 2v6M3 15v-4q0-2 2-2h11q2 0 2 2v4M10.5 9v6','M1 18h4M8.5 18h4M16 18h4'),
    )[icon]: p.line(d, '#785B45', 1.5)
    p.end();p.text(43, y+25, title, 24, weight=650);p.text(0, y+60, desc, 18, SUB, 500, MONO)


def diagram(p, x, y, scale=1):
    """A column corresponds to one channel throughout; each connector has one job."""
    p.group(f'translate({x} {y}) scale({scale})')
    centers = (317, 537, 757)
    stage(p, 18, '冻结权重', '768 × 768 / INT8', 0)
    stage(p, 132, '按列打包', '768 × 2304 / INT8', 1)
    stage(p, 233, '分别写回', '每路 33 × 768', 2)
    for cx in centers:
        p.line(f'M{cx} 85V130', '#9A806D', 1.8)
        p.dot(cx, 128, 2.7, '#846B58')
    # Micro-relief: one matte upper surface and a 4 px edge, no wireframe or highlights.
    for cx, (letter, name, face, edge, ink, _) in zip(centers, CHANNELS):
        p.group(f'matrix(1,-.045,-.16,1,{cx-83},20)')
        p.box(2, 8, 180, 70, '#EEE4D7', 13);p.box(0, 4, 180, 70, edge, 13);p.box(0, 0, 180, 70, face, 13)
        p.text(17, 52, letter, 51, ink, 650, DIN);p.text(163, 47, name, 23, ink, 500, DIN, 'end');p.end()
    p.group('translate(207 129)');p.box(1, 6, 660, 62, '#EBE0D1', 12);p.box(0, 3, 660, 62, '#BDA68B', 12)
    p.put('<g clip-path="url(#packed)">')
    for i,(letter, _, face, _, ink, _) in enumerate(CHANNELS):
        p.box(220*i, 0, 220, 62, face);p.text(220*i+17, 41, letter, 31, ink, 700, DIN)
        p.text(220*i+199, 39, f'{768*i}:{768*(i+1)}', 22, ink, 500, MONO, 'end')
        if i: p.box(220*i-2, 0, 4, 62, PAPER)
    p.end();p.end()
    # A single call feeds all three writes; do not draw three independent GEMMs.
    p.line('M537 190V246 M317 246v-7q0-4 4-4h432q4 0 4 4v7', '#9A806D', 1.8)
    p.box(452, 198, 170, 29, PAPER, 14, '#D9CABC')
    p.text(537, 219, '1 × INT8 GEMM', 17, SUB, 600, MONO, 'middle')
    for cx, (letter, _, _, _, ink, tint) in zip(centers, CHANNELS):
        p.box(cx-68, 246, 136, 40, tint, 20);p.text(cx, 273, letter+' / BF16', 23, ink, 600, DIN, 'middle')
    p.end()


def arrow(p, x, y, length=62):
    p.line(f'M{x} {y}h{length}m-13 -11 13 11-13 11', RUST, 4)


def detail(totals, groups):
    p=Plate(1600, 1000, '四层 BERT 的 QKV 投影融合', '左侧显示冻结权重、列区间和独立写回；右侧说明 GPU 执行顺序和逐字节校验；页底列出四种实现的内核启动数及最终构成。')
    p.text(50, 86, '四层 BERT 的 QKV 投影融合', 56, weight=750)
    p.text(52, 132, '同一层共享一次整数矩阵乘法，Q、K、V 各自写回。', 23, SUB)
    p.box(1272, 52, 275, 58, PANEL, 29);p.text(1409, 90, 'NVIDIA DGX Spark', 25, INK, 600, DIN, 'middle')
    p.line('M52 160H1548', HAIR, 1.5)
    p.text(52, 213, '权重如何拼接', 31, weight=700); p.text(998, 211, '每层一组，层间不拼接', 20, SUB, anchor='end')
    diagram(p, 53, 245, 1.085)
    p.box(52, 580, 946, 74, PANEL, 14);p.text(73, 610, '同一份输入激活  ×  拼接权重  →  累加结果', 21, INK, 600)
    p.text(73, 640, '[33, 768] INT8   ×   [768, 2304] INT8   →   [33, 2304] INT32', 20, SUB, 500, MONO)
    p.line('M1030 192V650', HAIR)
    p.text(1065, 213, 'CUDA 执行路径', 31, weight=700)
    rows=[('01','共享输入量化','三个投影读取同一份 INT8 激活。'),('02','一次整数 GEMM','aten._int_mm.default'),('03','缩放、加偏置、写回 BF16','packed_affine_projection')]
    for i,(n,label,code) in enumerate(rows):
        y=273+i*77
        p.text(1065,y,n,22,RUST,600,DIN);p.text(1113,y,label,23,weight=650)
        p.text(1113,y+28,code,19,SUB,500,MONO if i else CN)
    p.line('M1065 479H1548', HAIR)
    p.text(1065,524,'输出校验',27,weight=700);p.text(1065,566,'8 个请求 × 8 个返回张量',22)
    p.text(1065,603,'对照：量化 eager',19,SUB);p.text(1065,636,'差异字节：0',22,RUST,650)
    # Each row is one request and each column one returned tensor.
    for i in range(8):
        for j in range(8):p.box(1436+j*14,527+i*14,10,10, '#AF896B',3)
    p.box(0,682,1600,318,'#F5EEE4');p.line('M52 683H1548',HAIR,1.2)
    p.text(52,744,'一次前向的 GPU 内核启动次数',30,weight=700)
    p.text(52,780,'四层 BERT · 相同的 33 个 token',20,SUB)
    p.text(52,887,totals[0],78,'#685143',550,DIN);arrow(p,199,859,51)
    p.box(278,814,128,89,RUST,15);p.text(342,884,totals[-1],69,WHITE,650,DIN,'middle')
    p.text(55,936,'量化 eager',19,SUB);p.text(342,936,'每层打包',19,SUB,anchor='middle')
    p.line('M490 722V958',HAIR);p.text(524,748,'四种实现',26,weight=700)
    for i,(label,n) in enumerate(zip(('量化 eager','独立量化','共享量化','每层打包'),totals)):
        y=797+i*46;p.text(525,y,label,20,INK,650 if i==3 else 500)
        p.box(638,y-13,240,11,'#E7DBCA',5);p.box(638,y-13,240*n/totals[0],11,RUST if i==3 else '#B29B83',5)
        p.text(946,y+2,n,24,INK,650,DIN,'end')
    p.line('M981 722V958',HAIR);p.text(1016,748,'最后 64 次启动的构成',26,weight=700)
    labels=('INT8 GEMM','BF16 GEMM','LayerNorm','Softmax','输入量化','投影后处理','其他算子')
    for i,(label,n) in enumerate(zip(labels,groups)):
        col,row=divmod(i,4); x=1017+col*279; y=793+row*46
        p.text(x,y,label,20,INK,500,DIN if i<4 else CN);p.text(x+218,y,n,23,INK,650,DIN,'end')
        p.line(f'M{x} {y+13}h218','#DFD1BF',1)
    return p


PHOTO_SHA256 = '6c0e2a9efe3a29fafc07a34d71e7e31903b7b4d4d2a55368b34182a39dc7005a'


def cutout(photo):
    """Keep the physical unit and its front apertures; remove only the desk outside it."""
    from PIL import Image, ImageDraw, ImageFilter, ImageOps

    if hashlib.sha256(photo.read_bytes()).hexdigest() != PHOTO_SHA256:
        raise ValueError('The silhouette belongs to the May 19, 2026 Commons revision; see ASSETS.md')
    # Trace on a 1245 x 768 proxy. Transform at 2x before antialiasing the matte.
    outline = [(211,220),(214,218),(677,64),(683,65),(996,300),(999,305),
               (994,445),(992,450),(510,637),(504,637),(224,361),(221,355)]
    with Image.open(photo) as source:
        rgb = ImageOps.exif_transpose(source).convert('RGB').resize((2490,1536), Image.Resampling.LANCZOS)
    mask = Image.new('L', rgb.size); draw = ImageDraw.Draw(mask)
    draw.polygon([(2*x,2*y) for x,y in outline], fill=255)
    rgb.putalpha(mask.filter(ImageFilter.GaussianBlur(0.95)))
    rgb = rgb.crop((414,120,2008,1284)); rgb.thumbnail((1050,780), Image.Resampling.LANCZOS)
    stream = io.BytesIO(); rgb.save(stream, format='PNG', optimize=True)
    return base64.b64encode(stream.getvalue()).decode('ascii')


def model_results(root):
    def read(name):
        return json.loads((root/name).read_bytes())

    cases = read('qwen32b-fork/timing.json')['cases']
    q = next(r for r in cases if (r['length'], r['prefix_tokens'], r['family']) == (2048, 1536, 1))
    assert q['passes_strict_gate'] and q['byte_identical_full_logit_trajectories'] == q['trajectories_checked'] == 2
    g = read('glm45-355b/timing.json'); ckpt = read('glm45-355b/checkpoint.json')
    assert ckpt['model'] == 'unsloth/GLM-4.5-GGUF' and ckpt['format'] == 'UD-IQ1_S'
    assert read('glm45-355b/runtime.json')['device'] == 'NVIDIA GB10' and g['output_per_request'] == 16
    assert len(ckpt['files']) == 2 and q['owned_kv_bytes'] % (1 << 20) == 0
    wave = q['median_wave_ms']
    qwen = dict(cold=wave['cold']/1000, reuse=wave['snapshot']/1000,
                saved=round(100*(1-wave['snapshot']/wave['cold'])), prefix=q['prefix_tokens'],
                suffix=q['length']-q['prefix_tokens'], mib=q['owned_kv_bytes'] >> 20)
    case = g['cases']['128']
    glm = {name: case[name+'_ms']/1000 for name in ('wall', 'prompt', 'decode')}
    glm.update(generated=g['output_per_request'], quant=ckpt['format'])
    return qwen, glm


def overview(totals, qwen, glm, photo):
    p = Plate(1280, 800, 'PyTorch → CUDA C++：子图编译与单机推理',
              '四层 BERT 的图分区、QKV 打包和四种实现的启动次数；下方是独立的双请求 KV 复用和量化模型 HTTP 请求。DGX Spark 型号照片：Daniel Lu；改编图版 CC BY-SA 4.0。')
    p.put('<metadata>Photo: Daniel Lu (dllu), Nvidia DGX Spark oblique view dllu, Wikimedia Commons. Cut out and resized. Composition: EtherealBian, CC BY-SA 4.0. https://creativecommons.org/licenses/by-sa/4.0/</metadata>')
    p.text(30, 54, 'PyTorch → CUDA C++', 47, INK, 660, DIN)
    p.text(1250, 49, '四层 BERT  ·  batch 1  ·  33 tokens', 22, SUB, 550, anchor='end')
    p.line('M30 74H1250', HAIR)

    # The split is a compiler decision: unsupported operators stay in PyTorch.
    p.box(30, 87, 323, 103, '#F4EADC', 10)
    p.put(f'<image xmlns:xlink="http://www.w3.org/1999/xlink" x="41" y="94" width="120" height="86" xlink:href="data:image/png;base64,{photo}"/>')
    p.text(172, 133, 'DGX Spark', 31, INK, 650, DIN)
    p.text(173, 163, 'NVIDIA GB10', 20, SUB, 530, DIN)
    p.text(30, 223, '从导出图选择子图', 24, INK, 660)
    p.box(30, 240, 159, 36, PANEL, 7)
    p.text(109, 264, 'torch.export', 19, INK, 600, MONO, 'middle')
    p.line('M190 258h31m-6-5 6 5-6 5', RULE, 2)
    p.text(234, 265, '划分子图', 20, INK, 620)
    p.line('M278 279v10H49v56m0-28h19m-19 28h19', RULE, 1.7)
    p.dot(49, 317, 3, RULE)
    p.text(78, 323, '可融合 → 生成 CUDA C++', 19, RUST, 620)
    p.text(78, 352, '其余算子 → PyTorch 执行', 19, SUB, 540)
    p.line('M378 93V352', HAIR)

    # The warm Q/K/V arrangement is shared with the original, larger detail plate.
    p.text(406, 115, '同一层的 Q、K、V 共用一次矩阵乘法', 30, INK, 680)
    diagram(p, 408, 123, .80)
    p.text(1247, 191, '输入只量化一次', 17, RUST, 600, anchor='end')
    p.text(1247, 216, '33 × 768', 19, SUB, 540, MONO, 'end')
    p.text(1247, 271, 'INT32 累加', 18, INK, 590, anchor='end')
    p.text(1247, 301, '缩放 + 偏置', 17, SUB, 540, anchor='end')

    # Equal scales within this band only: counts are for the complete forward pass.
    p.box(0, 373, 1280, 112, '#F0E5D5')
    p.text(30, 417, 'GPU 内核启动次数', 28, INK, 680)
    p.text(30, 451, '一次完整前向 · 同一输入', 18, SUB)
    for i, (title, n) in enumerate(zip(('量化 eager', '独立量化', '共享量化', '每层打包'), totals)):
        x = 350 + 235*i
        color = RUST if i == 3 else '#836953'
        p.text(x, 405, title, 17, SUB, 580)
        p.text(x, 451, n, 46, color, 650, DIN)
        p.box(x, 462, 140, 6, '#DFD1BD', 3)
        p.box(x, 462, 140*n/totals[0], 6, color, 3)
        if i < 3: p.line(f'M{x+157} 434h26m-6-5 6 5-6 5', RULE, 1.7)

    p.box(0, 485, 1280, 315, '#FAF6EF')
    p.box(648, 485, 632, 315, '#F5EADC')
    p.text(30, 518, '独立整模型实验  /  共享 KV 快照', 17, RUST, 610)
    p.text(678, 518, '独立整模型实验  /  llama.cpp CUDA', 17, RUST, 610)
    p.text(30, 561, 'Qwen2.5-32B', 40, INK, 670, DIN)
    p.text(614, 557, 'BF16', 23, SUB, 600, DIN, 'end')
    p.text(678, 561, 'GLM-4.5 355B', 40, INK, 670, DIN)
    p.text(1249, 557, glm['quant'], 23, SUB, 600, DIN, 'end')

    # One prefill snapshot feeds two suffixes; boxes express dependencies, not time.
    p.box(30, 585, 201, 73, '#EFDCCA', 8)
    p.text(43, 614, f"共享 {qwen['prefix']:,} tokens", 20, INK, 620)
    p.text(43, 642, f"KV 快照 · {qwen['mib']} MiB", 17, SUB)
    p.line('M231 622h16m0 0v-21h18m-18 21v21h18', RULE, 2)
    p.dot(247, 622, 3, RUST)
    for i, branch in enumerate(('A', 'B')):
        y = 583 + 42*i
        p.box(268, y, 347, 35, '#F4ECE0', 7, HAIR)
        p.text(280, y+24, f"后缀 {branch} · {qwen['suffix']} tokens", 17, INK, 550)
        p.text(600, y+24, '→ 生成 8 tokens', 17, SUB, 540, anchor='end')
    p.text(30, 723, f"{qwen['cold']:.3f} → {qwen['reuse']:.3f} s", 47, INK, 620, DIN)
    p.box(477, 678, 138, 50, RUST, 9)
    p.text(546, 712, f"省时 {qwen['saved']}%", 24, WHITE, 650, anchor='middle')
    p.text(30, 761, '两条请求总耗时中位数，含快照准备。', 20, SUB)

    # Timings below are server-side phase medians, not components forced to sum to HTTP wall time.
    for i, (title, amount) in enumerate([
        ('处理 128 个输入 token', glm['prompt']),
        (f"生成 {glm['generated']} 个 token", glm['decode']),
    ]):
        x = 678 + i*296
        p.box(x, 583, 274, 77, '#FBF5EC', 8, '#DECDB7')
        p.text(x+14, 610, title, 17, SUB, 540)
        p.text(x+14, 644, f'{amount:.3f} s', 29, INK, 620, DIN)
    p.text(678, 723, f"{glm['wall']:.3f} s", 53, RUST, 660, DIN)
    p.text(1248, 714, '本机 HTTP 请求耗时中位数', 21, INK, 600, anchor='end')
    p.text(678, 761, '模型已加载；计时不含权重载入。', 20, SUB)
    return p


def main():
    args = argparse.ArgumentParser(description=__doc__)
    for name in ('reports', 'photo', 'out'):
        args.add_argument(name, type=Path)
    opts = args.parse_args(); opts.out.mkdir(exist_ok=True, parents=True)
    totals, groups = measured(opts.reports/'stacked-bert-gb10.json')
    qwen, glm = model_results(opts.reports)
    overview(totals, qwen, glm, cutout(opts.photo)).save(opts.out/'sparkfuse-system.svg')
    detail(totals, groups).save(opts.out/'qkv-warm-detail.svg')


if __name__ == '__main__':
    main()
