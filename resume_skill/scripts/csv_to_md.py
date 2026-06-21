#!/usr/bin/env python3
"""把「分类,字段名,值」三列的简历 CSV/xlsx 转成 resume.md。

输入格式：
    分类,字段名,值
    基本信息,姓名,库森
    实习经历1,职责描述,1. 参与...\n2. 优化...

值里用 \\n 表示多条（会拆成 Markdown 要点）。
导入只是「搭好骨架」——之后应按 references/writing-principles.md 用 STAR/量化改写要点。

用法：
    python csv_to_md.py 模板.csv -o resume.md
    python csv_to_md.py 模板.xlsx -o resume.md
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import yaml

# 分类前缀 -> 输出节标题（数字后缀如 实习经历1/实习经历2 会合并到同一节）
SECTION_TITLES = {
    "教育背景": "教育背景",
    "本科教育": "教育背景",
    "实习经历": "实习经历",
    "工作经历": "工作经历",
    "项目经验": "项目经验",
    "校园项目": "项目经验",
    "校园活动": "校园经历",
    "技能证书": "专业技能",
    "获奖情况": "荣誉奖项",
    "自我评价": "__summary__",   # 落到 front matter 的 summary
    "求职意向": "__intent__",    # 落到 front matter
    "基本信息": "__meta__",      # 落到 front matter
}

# 基本信息字段名 -> front matter key
META_KEYS = {
    "姓名": "name", "性别": "gender", "出生日期": "birth",
    "手机号": "phone", "电话": "phone", "邮箱": "email", "email": "email",
    "现居住地": "location", "户籍所在地": "hometown",
    "身份证号": "id_number",  # 隐私字段，默认注释掉
}

PRIVATE_KEYS = {"id_number"}
EXCEL_MAX_EXACT_INTEGER = 10 ** 15


def split_lines(value):
    """把 '1. a\\n2. b' 或换行的值拆成要点列表。"""
    if value is None:
        return []
    value = value.replace("\\n", "\n")
    parts = [p.strip() for p in value.split("\n") if p.strip()]
    cleaned = []
    for p in parts:
        # 去掉开头的 '1.' '2、' '- ' 等序号
        p = re.sub(r"^\s*(\d+[.、)]\s*|[-*]\s*)", "", p)
        if p:
            cleaned.append(p)
    return cleaned


def strip_digit_suffix(category):
    return re.sub(r"\d+$", "", category)


def xlsx_cell_to_text(cell):
    """转换 xlsx 单元格；拒绝 Excel 无法精确保存的超长数值。"""
    value = cell.value
    if value is None:
        return ""
    if isinstance(value, (int, float)) and abs(value) >= EXCEL_MAX_EXACT_INTEGER:
        sys.exit(
            f"[csv_to_md] xlsx 单元格 {cell.coordinate} 含 16 位以上数字。"
            "Excel 数值格式可能已丢失精度，请把手机号/身份证号等字段设为“文本”后重新保存。"
        )
    return str(value)


def read_rows(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".xls":
        sys.exit("[csv_to_md] 不支持旧版 .xls，请先另存为 .xlsx 或 CSV。")
    if suffix == ".xlsx":
        try:
            import openpyxl
        except ImportError:
            sys.exit("[csv_to_md] 读取 xlsx 需要 openpyxl：python3 -m pip install openpyxl；"
                     "或先把表格另存为 CSV。")
        wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
        ws = wb.active
        rows = []
        for r in ws.iter_rows(min_col=1, max_col=3):
            if r and any(c.value is not None for c in r):
                rows.append([xlsx_cell_to_text(c) for c in r])
        return rows
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return [row for row in csv.reader(f) if row]


def build(rows):
    meta = {}
    intent_parts = {}
    summary = ""
    # 用 (节标题, 原始分类) 作为分组键，保留条目顺序
    groups = []  # list of (section_title, category, dict(field->value))
    index = {}

    header_skipped = False
    for row in rows:
        if len(row) < 3:
            continue
        category, field, value = row[0].strip(), row[1].strip(), row[2]
        if not header_skipped and category in ("分类", "category"):
            header_skipped = True
            continue
        if not category or not field:
            continue

        base = strip_digit_suffix(category)
        target = SECTION_TITLES.get(base) or SECTION_TITLES.get(category)

        if target == "__meta__":
            key = META_KEYS.get(field)
            if key:
                meta[key] = value.strip()
            continue
        if target == "__intent__":
            intent_parts[field] = value.strip()
            continue
        if target == "__summary__":
            summary = value.strip()
            continue
        if target is None:
            # 未知分类：当作一般经历节，用原分类名
            target = base

        key = (target, category)
        if key not in index:
            d = {}
            index[key] = d
            groups.append((target, category, d))
        index[key][field] = value

    return meta, intent_parts, summary, groups


def fmt_period(d, *names):
    for n in names:
        if d.get(n):
            return d[n].strip()
    return ""


def entry_md(category, d):
    """把一个经历条目 dict 渲染成 ### 标题 + 要点。"""
    base = strip_digit_suffix(category)
    lines = []

    if base in ("教育背景", "本科教育"):
        title_bits = [d.get(k, "") for k in ("学校", "学院", "专业", "学历") if d.get(k)]
        period = f"{fmt_period(d, '入学时间')} – {fmt_period(d, '毕业时间')}".strip(" –")
        lines.append(f"### {' · '.join(title_bits)}" + (f" | {period}" if period else ""))
        bullets = []
        extra = " ".join(x for x in [
            f"GPA {d['GPA']}" if d.get("GPA") else "",
            f"专业排名 {d['专业排名']}" if d.get("专业排名") else "",
        ] if x)
        if extra:
            bullets.append(extra)
        if d.get("主修课程"):
            bullets.append(f"主修课程：{d['主修课程']}")
        for b in bullets:
            lines.append(f"- {b}")

    elif base in ("实习经历", "工作经历"):
        title_bits = [d.get(k, "") for k in ("公司名称", "部门", "职位名称") if d.get(k)]
        period = fmt_period(d, "实习时间", "工作时间")
        loc = fmt_period(d, "实习地点", "工作地点")
        meta = " · ".join(x for x in [period, loc] if x)
        lines.append(f"### {' · '.join(title_bits)}" + (f" | {meta}" if meta else ""))
        for b in split_lines(d.get("职责描述") or d.get("工作描述")):
            lines.append(f"- {b}")

    elif base in ("项目经验", "校园项目"):
        title_bits = [d.get(k, "") for k in ("项目名称", "项目角色") if d.get(k)]
        period = fmt_period(d, "项目时间")
        lines.append(f"### {' · '.join(title_bits)}" + (f" | {period}" if period else ""))
        if d.get("项目描述"):
            lines.append(f"- {d['项目描述'].strip()}")
        for b in split_lines(d.get("责任描述")):
            lines.append(f"- {b}")
        if d.get("项目成果"):
            lines.append(f"- **成果**：{d['项目成果'].strip()}")

    elif base == "校园活动":
        title_bits = [d.get(k, "") for k in ("活动名称", "担任职务") if d.get(k)]
        period = fmt_period(d, "活动时间")
        lines.append(f"### {' · '.join(title_bits)}" + (f" | {period}" if period else ""))
        for b in split_lines(d.get("活动描述")):
            lines.append(f"- {b}")

    elif base == "技能证书":
        # 技能节用纯要点，无 ###
        for field, value in d.items():
            if value and value.strip():
                lines.append(f"- **{field}**：{value.strip()}")

    elif base == "获奖情况":
        period = fmt_period(d, "获奖时间")
        name = d.get("获奖名称", "")
        desc = d.get("获奖描述", "")
        org = d.get("颁发机构", "")
        bits = " · ".join(x for x in [period, name, desc, org] if x)
        lines.append(f"- {bits}")

    else:
        lines.append(f"### {category}")
        for field, value in d.items():
            if value and value.strip():
                for b in split_lines(value):
                    lines.append(f"- {field}：{b}" if len(d) > 1 else f"- {b}")

    return lines


def to_markdown(meta, intent_parts, summary, groups):
    # 使用 YAML 序列化器，避免姓名、岗位、简介中的冒号、井号、换行等破坏 front matter。
    front = {}
    order = ["name", "gender", "birth", "phone", "email", "location", "hometown"]
    for k in order:
        if meta.get(k):
            front[k] = str(meta[k])

    if intent_parts:
        intent = intent_parts.get("期望职位", "")
        if intent:
            front["intent"] = intent
        details = " · ".join(f"{k}：{v}" for k, v in intent_parts.items()
                             if k != "期望职位" and v)
        if details:
            front["intent_detail"] = details
    if summary:
        front["summary"] = summary

    class FrontMatterDumper(yaml.SafeDumper):
        pass

    def represent_string(dumper, value):
        style = "|" if "\n" in value else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)

    FrontMatterDumper.add_representer(str, represent_string)
    front_yaml = yaml.dump(
        front,
        Dumper=FrontMatterDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).rstrip()

    out = ["---", front_yaml]
    for k in sorted(PRIVATE_KEYS):
        if meta.get(k):
            out.append(f"# {k}: {meta[k]}   # 隐私字段，默认不输出，需要时取消注释")
    out.append("---")
    out.append("")

    # 按节聚合输出，保持 SECTION 出现顺序
    seen_sections = []
    for title, category, d in groups:
        if title not in seen_sections:
            seen_sections.append(title)

    for sect in seen_sections:
        out.append(f"## {sect}")
        for title, category, d in groups:
            if title != sect:
                continue
            out.extend(entry_md(category, d))
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="简历 CSV/xlsx -> resume.md")
    ap.add_argument("input", help="CSV 或 xlsx 文件")
    ap.add_argument("--out", "-o", default="resume.md", help="输出 Markdown 路径")
    args = ap.parse_args()

    rows = read_rows(args.input)
    meta, intent_parts, summary, groups = build(rows)
    md = to_markdown(meta, intent_parts, summary, groups)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"[csv_to_md] 已生成：{args.out}")
    print("[csv_to_md] 提示：这是导入骨架，请按 STAR/量化原则改写要点后再渲染。")


if __name__ == "__main__":
    main()
