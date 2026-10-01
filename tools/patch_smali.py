#!/usr/bin/env python3
"""第四课靶场 · smali 判定分支 patch 器。

对 apktool 反编译产物打最小补丁：把 MainActivity 里的判定取反，
使无效卡密也被判为有效。仅用于本靶场本地实验。

用法:
    python patch_smali.py <apktool_out_dir> [--dry-run]

输出: 修改的文件、diff、以及回滚用的 .bak
"""

import argparse
import os
import re
import shutil
import sys

# 翻转方向：判定跳转取反，使无效卡密也走"有效"分支
FLIP = {
    "if-eqz": "if-nez",
    "if-nez": "if-eqz",
    "if-eq": "if-ne",
    "if-ne": "if-eq",
}

# invoke-*/move-result 之后的紧邻跳转，才是校验结果的判定点
CALL_RE = re.compile(r"isValidKey|LicenseCheck")
BRANCH_RE = re.compile(r"^\s*(if-\w+)\s")


def find_files(root: str):
    hits = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".smali") and ("MainActivity" in fn or "LicenseCheck" in fn):
                hits.append(os.path.join(dirpath, fn))
    return sorted(hits)


def patch_file(path: str, dry_run: bool):
    """只在调用 isValidKey 的方法体内，翻转调用点之后的第一个条件跳转。"""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    edits = []
    pending = False
    for i, ln in enumerate(lines):
        stripped = ln.strip()

        # 进入新方法，重置状态
        if stripped.startswith(".method"):
            pending = False
            continue

        if CALL_RE.search(stripped) and stripped.startswith("invoke-"):
            pending = True
            continue

        if pending:
            m = BRANCH_RE.match(ln)
            if m and m.group(1) in FLIP:
                edits.append((i, m.group(1), FLIP[m.group(1)]))
                pending = False

    if not edits:
        return None

    if not dry_run:
        bak = path + ".bak"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
        for i, old, new in edits:
            lines[i] = lines[i].replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return edits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", help="apktool 反编译输出目录")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.out_dir):
        print("not a directory:", args.out_dir)
        return 2

    candidates = find_files(args.out_dir)
    if not candidates:
        print("no MainActivity smali found under", args.out_dir)
        return 1

    total = 0
    for path in candidates:
        rel = os.path.relpath(path, args.out_dir)
        edits = patch_file(path, args.dry_run)
        if not edits:
            continue
        total += len(edits)
        print("PATCH", rel)
        for i, old, new in edits:
            print("  line %d: %s -> %s" % (i + 1, old, new))

    if total == 0:
        print("no branch matched; inspect the smali manually")
        return 1

    print("edits:", total, "(dry-run)" if args.dry_run else "(applied)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
