#!/usr/bin/env python3
"""把 resume.md 渲染成 HTML，并用 WeasyPrint 输出 A4 PDF。

resume.md 的约定（详见 references/field-schema.md）：
- YAML front matter：放姓名、联系方式、求职意向、个人简介等原子字段。
- 正文用 `## ` 分节（教育背景 / 实习经历 / 项目经验 / 专业技能 / 荣誉奖项 …）。
- 每节内用 `### ` 表示一条「经历条目」，标题里用 ` | ` 分隔正标题与时间/地点等元信息，
  正标题内可用 ` · `、`・` 或 `•` 分隔（如「沧澜智算 · 基础架构部 · 后端开发实习生」）。
- `- ` 开头的行是要点（bullet）。没有 `### ` 的节（如技能）直接由要点组成。

渲染后端用 WeasyPrint（纯 Python，无需浏览器，对中文与打印 CSS 支持好）。
请使用已安装 WeasyPrint 等依赖的 Python 3 解释器运行。

用法：
    python render.py resume.md --template modern --out resume.pdf
    python render.py resume.md            # 默认 classic，输出 resume.pdf
    python render.py resume.md --html-only  # 只产出 HTML，便于调试
"""
import argparse
import difflib
import html
import re
import sys
from pathlib import Path
from markupsafe import Markup

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"
BASE_STYLE_PATH = SKILL_DIR / "assets" / "styles" / "resume-base.css"
MIN_PYTHON = (3, 10)
SUPPORTED_META_FIELDS = {
    "name",
    "gender",
    "birth",
    "phone",
    "email",
    "location",
    "hometown",
    "photo",
    "intent",
    "intent_detail",
    "summary",
}
META_FIELD_ALIASES = {
    "姓名": "name",
    "性别": "gender",
    "出生日期": "birth",
    "电话": "phone",
    "手机号": "phone",
    "邮箱": "email",
    "现居住地": "location",
    "户籍所在地": "hometown",
    "照片": "photo",
    "头像": "photo",
    "求职意向": "intent",
    "期望职位": "intent",
    "求职详情": "intent_detail",
    "个人简介": "summary",
    "自我评价": "summary",
}


def die(msg):
    print(f"[render] 错误：{msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg):
    print(f"[render] 警告：{msg}", file=sys.stderr)


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def require_python_version(version_info=None):
    version_info = version_info or sys.version_info
    if tuple(version_info[:2]) < MIN_PYTHON:
        current = ".".join(str(v) for v in version_info[:3])
        die(
            f"需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 或更高版本，"
            f"当前为 Python {current}"
        )


def warn_unused_meta(meta):
    for key in sorted(set(meta) - SUPPORTED_META_FIELDS):
        suggestion = META_FIELD_ALIASES.get(key)
        if suggestion is None:
            matches = difflib.get_close_matches(
                str(key),
                sorted(SUPPORTED_META_FIELDS),
                n=1,
                cutoff=0.72,
            )
            suggestion = matches[0] if matches else None
        suffix = f"；是否想写 `{suggestion}`？" if suggestion else ""
        warn(f"front matter 字段 `{key}` 不会被模板使用{suffix}")


def validate_resume(meta, sections):
    if not str(meta.get("name", "")).strip():
        die("resume.md 缺少必填字段 name")
    warn_unused_meta(meta)
    if not str(meta.get("intent", "")).strip() and not str(
        meta.get("intent_detail", "")
    ).strip():
        warn("简历头部没有求职意向；如需展示，请填写 intent 或 intent_detail")


def require_deps(need_pdf=True):
    missing = []
    try:
        import frontmatter  # noqa: F401
    except ImportError:
        missing.append("python-frontmatter")
    try:
        import jinja2  # noqa: F401
    except ImportError:
        missing.append("jinja2")
    if need_pdf:
        try:
            import weasyprint  # noqa: F401
        except ImportError:
            missing.append("weasyprint")
        except OSError as exc:
            die(
                "WeasyPrint 已安装，但系统图形库加载失败："
                f"{exc}\n"
                "请按 WeasyPrint 官方安装文档补齐系统依赖，"
                "或先使用 --html-only 生成 HTML 后通过浏览器打印 PDF"
            )
        except Exception as exc:
            die(
                "WeasyPrint 初始化失败："
                f"{exc}\n"
                "可先使用 --html-only 生成 HTML 后通过浏览器打印 PDF"
            )
    if missing:
        die("缺少依赖：\n"
            "    python3 -m pip install "
            + " ".join(missing))


# ---------- Markdown 解析 ----------

def inline_md(text):
    """最小行内 Markdown -> HTML：转义后处理 **加粗**、*斜体*、`代码`。"""
    text = html.escape(text)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return Markup(text)


def parse_entry_heading(line):
    """`### 沧澜智算 · 后端实习生 | 2025.08 – 2025.12 · 南京`
    -> {title_parts: ["沧澜智算", "后端实习生"], meta: "2025.08 – 2025.12 · 南京"}
    """
    line = line.lstrip("#").strip()
    heading_parts = re.split(r"\s*[|｜]\s*", line, maxsplit=1)
    left = heading_parts[0]
    meta = heading_parts[1] if len(heading_parts) > 1 else ""
    parts = [p.strip() for p in re.split(r"\s*[·・•]\s*", left) if p.strip()]
    return {"title_parts": parts, "meta": meta.strip()}


def parse_resume(md_path):
    import frontmatter

    post = frontmatter.load(str(md_path))
    meta = dict(post.metadata)
    body = post.content

    sections = []
    current_section = None
    current_entry = None

    def flush_entry():
        nonlocal current_entry
        if current_entry is not None:
            current_section["entries"].append(current_entry)
            current_entry = None

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("## ") and not line.startswith("### "):
            flush_entry()
            current_section = {"title": line[3:].strip(), "entries": [], "bullets": []}
            sections.append(current_section)
        elif line.startswith("### "):
            if current_section is None:
                continue
            flush_entry()
            current_entry = parse_entry_heading(line)
            current_entry["bullets"] = []
        elif line.lstrip().startswith(("- ", "* ")):
            text = line.lstrip()[2:].strip()
            target = current_entry if current_entry is not None else current_section
            if target is not None:
                target["bullets"].append(inline_md(text))
        else:
            # 自由段落：归到当前条目或节的 bullets
            target = current_entry if current_entry is not None else current_section
            if target is not None:
                target["bullets"].append(inline_md(line.strip()))

    flush_entry()
    return meta, sections


# ---------- 渲染 ----------

SIDEBAR_KEYWORDS = ("技能", "证书", "求职", "意向", "语言", "联系")

# 配色预设：覆盖模板里的 --accent。对应几款常见风格主色。
ACCENT_PRESETS = {
    "blue": "#2456a6",    # 清新蓝灰（默认偏蓝）
    "teal": "#0a7d6b",    # 沉稳青绿
    "wine": "#8a2433",    # 典雅酒红
    "ink": "#2b2b2b",     # 极客墨黑
    "purple": "#5b3b8c",  # 紫
    "green": "#2e7d32",   # 绿
    "orange": "#c65d21",  # 沉稳焦橙
}


def available_templates():
    """返回真正可渲染的模板目录，忽略辅助目录和零散文件。"""
    return sorted(
        p.name
        for p in TEMPLATES_DIR.iterdir()
        if p.is_dir() and (p / "resume.html.j2").is_file()
    )


def render_html(meta, sections, template_name, accent=None):
    import jinja2

    tdir = TEMPLATES_DIR / template_name
    if not (tdir / "resume.html.j2").exists():
        avail = ", ".join(available_templates())
        die(f"找不到模板 '{template_name}'。可用模板：{avail}")

    base_css = BASE_STYLE_PATH.read_text(encoding="utf-8") if BASE_STYLE_PATH.exists() else ""
    template_css = (tdir / "style.css").read_text(encoding="utf-8") if (tdir / "style.css").exists() else ""
    css = f"{base_css}\n{template_css}"

    # 配色覆盖：把 --accent 重定义追加到 css 末尾（后定义生效）
    if accent:
        color = ACCENT_PRESETS.get(accent)
        if color is None:
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
                die("配色必须是 blue/teal/wine/ink/purple/green/orange 或 #rrggbb")
            color = accent
        css += f"\n:root {{ --accent: {color}; }}\n"

    # 给模板一个便捷分类：哪些节适合放到侧边栏（modern 用）
    def is_sidebar(title):
        return any(k in title for k in SIDEBAR_KEYWORDS)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(tdir)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["is_sidebar"] = is_sidebar
    tpl = env.get_template("resume.html.j2")
    sidebar = [s for s in sections if is_sidebar(s["title"])]
    main = [s for s in sections if not is_sidebar(s["title"])]
    return tpl.render(meta=meta, sections=sections, sidebar=sidebar, main=main, css=Markup(css))


def html_to_pdf(html_string, pdf_path, base_url):
    from weasyprint import HTML
    HTML(string=html_string, base_url=str(base_url)).write_pdf(str(pdf_path))


def html_output_path(md_path, template_name):
    return md_path.with_suffix(f".{template_name}.html")


def main():
    ap = argparse.ArgumentParser(description="resume.md -> HTML -> PDF (WeasyPrint)")
    ap.add_argument("md", help="resume.md 路径")
    ap.add_argument(
        "--template",
        "-t",
        default="classic",
        help="模板名 (" + "/".join(available_templates()) + ")",
    )
    ap.add_argument("--accent", "-a", default=None,
                    help="配色：预设名 (blue/teal/wine/ink/purple/green/orange) 或 #rrggbb。classic 为纯黑白，不受影响")
    ap.add_argument("--out", "-o", default=None, help="输出 PDF 路径")
    ap.add_argument("--html-only", action="store_true", help="只产出 HTML（调试用）")
    args = ap.parse_args()

    require_python_version()
    require_deps(need_pdf=not args.html_only)
    md_path = Path(args.md)
    if not md_path.exists():
        die(f"找不到文件：{md_path}")

    meta, sections = parse_resume(md_path)
    validate_resume(meta, sections)
    html_out = render_html(meta, sections, args.template, accent=args.accent)

    html_path = html_output_path(md_path, args.template)
    ensure_parent(html_path)
    html_path.write_text(html_out, encoding="utf-8")
    print(f"[render] 已生成 HTML：{html_path}")

    if args.html_only:
        return

    pdf_path = Path(args.out) if args.out else md_path.with_suffix(".pdf")
    ensure_parent(pdf_path)
    html_to_pdf(html_out, pdf_path, base_url=md_path.parent)
    print(f"[render] 已生成 PDF：{pdf_path}（模板：{args.template}）")


if __name__ == "__main__":
    main()
