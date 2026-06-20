---
name: resume-builder
description: >-
  根据个人信息生成美观的中文简历（校招/社招通用），支持 classic/modern/timeline/minimal 四套可切换模板、多种配色与可选证件照，
  以 Markdown 为内容源、渲染成 PDF 导出；并能按 STAR/量化等最佳实践润色，或针对目标岗位 JD 做定向改写与匹配度分析。
  Use whenever the user wants to 写简历/做简历/生成简历/制作简历/简历模板/简历润色/优化简历/改简历/简历排版/导出简历PDF,
  build/write/polish/tailor a resume or CV, convert resume info to PDF, or adapt a resume to a job description (JD/岗位/招聘要求)——
  在求职、岗位申请或简历语境中，即使用户只说"帮我整理一下我的经历""这段经历怎么写更好""按这个岗位改改"也应触发。
---

# 简历生成器 resume-builder

帮用户把个人信息做成一份**美观、可量化、与岗位对齐**的中文简历，并渲染成 PDF。
内容源是 `resume.md`（Markdown），渲染后端是 WeasyPrint（HTML/CSS → PDF），提供四套模板 + 配色 + 可选证件照。

## 环境要求（重要）

渲染必须用 **Homebrew 的 Python**：`/opt/homebrew/bin/python3.13`。
本机 anaconda 的 Python 会让 WeasyPrint 崩溃（glib 冲突），Chrome 无头打印也不可用，都不要用。
首次缺依赖时：
```bash
/opt/homebrew/bin/python3.13 -m pip install --break-system-packages weasyprint jinja2 python-frontmatter pyyaml openpyxl
```

## 四步工作流

### 第 1 步：录入信息 → 生成 `resume.md`

- **已有表格**（「分类,字段名,值」格式的 CSV/xlsx）：
  ```bash
  /opt/homebrew/bin/python3.13 scripts/csv_to_md.py 用户的表格.csv -o resume.md
  ```
  可先用 `assets/resume.example.csv` 验证导入链路。
- **没有表格**：按 `references/field-schema.md` 的结构对话采集。采集经历时用 **STAR 思路追问**——
  不要只问"做了什么"，要追问"背景是什么、解决了什么问题、带来什么可量化的结果"，
  这样第 2 步才有料可写。把信息整理成 `resume.md`（front matter + `## ` 分节）。

明确了目标岗位时，先看 `references/role-presets.md` 决定**小节顺序与侧重**（如算法岗把项目/论文靠前、后端岗强调高并发与性能）。
字段约定、CSV 映射规则详见 `references/field-schema.md`。证件照、隐私字段（身份证号等）默认不输出。

### 第 2 步：按最佳实践起草/润色要点

通读 `references/writing-principles.md`，对每条经历：
- 用 **STAR / XYZ 句式**改写："通过做 Z，达成 X，量化为 Y"。
- **量化优先**：补数字（规模/百分比/从多少到多少/排名/时间）。没有数字就引导用户回忆，或换成具体事实。
- **强动词开头**（主导/重构/优化/落地…），删掉"负责/参与"流水账。
- 按**校招 vs 社招**调整顺序与详略（校招重教育/竞赛/潜力；社招重成果/职责深度）。
- 守**一页原则**（校招原则 1 页）。

`assets/resume.example.md` 是一份按这些原则写好的范例，可作为措辞与密度的参照。

### 第 3 步：选模板渲染 PDF

参考 `references/templates-guide.md` 选模板（拿不准 → classic）：
```bash
/opt/homebrew/bin/python3.13 scripts/render.py resume.md --template modern --accent teal --out resume.pdf
/opt/homebrew/bin/python3.13 scripts/render.py resume.md --template modern --accent orange --out resume-orange.pdf
```
- `classic`：单栏黑白、ATS 最稳、海投首选（默认；纯黑白不受配色影响）。
- `modern`：侧栏 + 色块标题，现代观感，互联网岗。
- `timeline`：左侧时间线竖轴，适合经历密集者。
- `minimal`：极简纯白、大留白，适合精炼/设计感。
- 配色 `--accent`：blue/teal/wine/ink/purple/green/orange 或 `#rrggbb`（仅 modern/timeline/minimal 生效）。
- 证件照：在 front matter 加 `photo: 路径`，默认不放（投外企建议不放）。

调样式：`--html-only` 先出 HTML 看效果，或直接改对应模板的 `style.css`（主色 `--accent`、字号、留白都在里面）重渲染。
渲染后**务必打开 PDF 检查**：中文是否正常、是否一页、有无溢出或截断。

### 第 4 步：（可选）针对岗位定向润色

用户给了目标岗位 **JD** 时：
1. 从 JD 抽取硬技能关键词与软要求。
2. 对照现有 `resume.md` 做**匹配度小结**：命中哪些关键词、缺失哪些、哪些经历该上移/加重。
3. 在用户**真实具备**的前提下，把相关经历改写得更贴 JD 语言、调整顺序，重渲染。
   绝不编造经历或数字——面试会被追问。
没有 JD 时，就按第 2 步的通用最佳实践润色即可。

## 产出物
- `resume.md`：内容源（用户可继续手改）。
- `resume.pdf`：最终交付。
- `resume.html`：渲染中间产物（调样式时有用）。

## 目录速览
- `scripts/csv_to_md.py` — 表格 → resume.md
- `scripts/render.py` — resume.md + 模板 → HTML → PDF（WeasyPrint）
- `references/writing-principles.md` — STAR/量化/动词/校招vs社招/ATS/隐私/常见错误
- `references/field-schema.md` — resume.md 格式（含 photo 字段）与 CSV 映射
- `references/templates-guide.md` — 四套模板 + 配色 + 证件照怎么选
- `references/role-presets.md` — 各岗位推荐的小节顺序/侧重/技能线（录入与 JD 定向时用）
- `assets/templates/{classic,modern,timeline,minimal}/` — 模板（`resume.html.j2` + `style.css`）
- `assets/resume.example.md` — 写好的范例
