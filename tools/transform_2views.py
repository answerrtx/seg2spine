#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from dataclasses import dataclass
from typing import List


@dataclass
class SpineData:
    cent_x: float
    cent_y: float
    width: float
    height: float
    ang: float


def read_spine_txt(path: str) -> List[SpineData]:
    out: List[SpineData] = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 5:
                raise ValueError(f"{path}:{ln} need 5 floats, got {len(parts)} -> {line}")
            cx, cy, w, h, ang = map(float, parts[:5])
            out.append(SpineData(cx, cy, w, h, ang))
    return out


def gen_17x9_txt_driven(
    pa: List[SpineData],
    lat: List[SpineData],
    templ_w: float,
    templ_h: float,
    templ_d: float,
    fit_uniform: bool = False,
) -> List[List[float]]:
    """
    
    [sx, sy, sz, ang1, ang2, ang3, tx, ty, tz]

    sx/sy/sz：把 template 的 bbox (templ_w/h/d) 形变到 txt 的目标宽高厚（归一化单位）
    t*：同一归一化单位下的平移
    """
    if len(pa) != 17:
        raise ValueError(f"PA must have 17 lines, got {len(pa)}")
    if len(lat) != 17:
        raise ValueError(f"LAT must have 17 lines, got {len(lat)}")
    if templ_w <= 0 or templ_h <= 0 or templ_d <= 0:
        raise ValueError("template bbox dims must be > 0")

    base_pa = pa[8]      # T9
    base_lat = lat[8]    # 用 LAT 的 T9 当 z 基准更自然
    scale = base_pa.height
    if scale == 0:
        raise ValueError("pa[8].height == 0, cannot normalize")

    convertt = (lat[8].cent_x > lat[15].cent_x)

    rows: List[List[float]] = []
    for i in range(17):
        # --- translation（归一化，只保比例）---
        tx = (pa[i].cent_x - base_pa.cent_x) / scale
        ty = (base_pa.cent_y - pa[i].cent_y) / scale

        tz = (base_lat.cent_x - lat[i].cent_x) / scale
        if not convertt:
            tz = (lat[i].cent_x - base_lat.cent_x) / scale

        # --- txt-driven target dims（归一化）---
        target_w = pa[i].width / scale
        target_h = pa[i].height / scale
        target_d = lat[i].width / scale   # thickness from LAT width

        # --- scale factors: deform template bbox -> target dims ---
        sx = target_w / templ_w
        sy = target_h / templ_h * 0.95
        sz = target_d / templ_d

        # --- rotations---
        ang1 = lat[i].ang
        if convertt:
            ang1 = -ang1
        ang2 = 0.0
        ang3 = -pa[i].ang

        rows.append([sx, sy, sz, ang1, ang2, ang3, tx, ty, tz])

    if fit_uniform:
        # 可选：统一等比例缩放整条 spine（不会改变比例），便于显示在某个范围内
        # 这里用“最大平移跨度”做归一化，把最大的 span 缩到 1
        xs = [r[6] for r in rows]
        ys = [r[7] for r in rows]
        zs = [r[8] for r in rows]
        span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        S = (1.0 / span) if span > 0 else 1.0
        for r in rows:
            # scale 和 translation 一起乘同一个 S，比例不变
            r[0] *= S; r[1] *= S; r[2] *= S
            r[6] *= S; r[7] *= S; r[8] *= S

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pa", required=True, help="pa txt (17 lines, cx cy w h ang)")
    ap.add_argument("--lat", required=True, help="lat txt (17 lines, cx cy w h ang)")
    ap.add_argument("--out", required=True, help="output 17x9 txt")
    ap.add_argument("--templ_w", type=float, required=True, help="template bbox width (local units)")
    ap.add_argument("--templ_h", type=float, required=True, help="template bbox height (local units)")
    ap.add_argument("--templ_d", type=float, required=True, help="template bbox depth (local units)")
    ap.add_argument("--fit_uniform", action="store_true", help="uniformly scale whole spine for display (keeps ratios)")
    args = ap.parse_args()

    pa = read_spine_txt(args.pa)
    lat = read_spine_txt(args.lat)

    rows = gen_17x9_txt_driven(
        pa, lat,
        templ_w=args.templ_w,
        templ_h=args.templ_h,
        templ_d=args.templ_d,
        fit_uniform=args.fit_uniform,
    )

    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(" ".join(f"{x:.6f}" for x in r) + "\n")

    print(f"Saved 17x9 (txt-driven) transforms -> {args.out}")


if __name__ == "__main__":
    main()


"""
python3 transform_2views.py \          
  --pa pa_tmp.txt --lat lat_tmp.txt \
  --templ_w 1.0 --templ_h 0.45 --templ_d 0.7 \
  --out transforms.txt
"""
