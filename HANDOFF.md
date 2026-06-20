# resume-builder skill — 交接 & Review 文档

给维护者：这是一个可供 Codex/Claude 调用的「中文简历生成」skill。下面记录架构、关键约束、设计取舍和 review/测试清单。

## 1. 这个 skill 做什么
输入个人信息（CSV 导入或对话采集）→ 生成 `resume.md`（内容源）→ 按 STAR/量化原则润色 → 选模板渲染成 PDF；可按目标岗位 JD 做定向改写与匹配度分析。

## 2. 架构（数据驱动，内容与样式分离）
```
resume.md (front matter + ## 分节)
   │  scripts/render.py 解析
   ▼
数据 dict ── Jinja 模板(assets/templates/<style>/resume.html.j2 + style.css) ──▶ HTML
   │  WeasyPrint
   ▼
resume.pdf  (A4)
```
- 内容源 = `resume.md`：YAML front matter 放原子字段（姓名/联系方式/intent/summary/可选 photo），正文用 `## ` 分节、`### ` 表条目、`- ` 要点。
- 4 套布局：`classic`(单栏黑白/ATS) `modern`(侧栏色块) `timeline`(时间线) `minimal`(极简纯白)。
- 配色 `--accent`：blue/teal/wine/ink/purple/green/orange 或 `#rrggbb`（classic 恒黑白）。
- 证件照 `photo:` 字段，默认不填；classic/modern/minimal 会渲染。

## 3. ⚠️ 关键约束（最容易踩坑，务必先读）
**渲染必须用 Homebrew 的 Python：`/opt/homebrew/bin/python3.13`。**
- 本机 anaconda 的 Python 运行 WeasyPrint 会 **SIGBUS 崩溃**（glib/pango 冲突）。
- 本机 **Chrome 无头打印 PDF 完全不可用**（输出空白 PDF），已废弃该路线，不要尝试。
- 依赖安装：`/opt/homebrew/bin/python3.13 -m pip install --break-system-packages weasyprint jinja2 python-frontmatter pyyaml openpyxl`（已装）。
- 已通过软链安装到 `~/.claude/skills/resume-builder` 和 `~/.codex/skills/resume-builder`。

## 4. 文件清单（skill 根 = `resume_skill/`）
```
resume_skill/
├── SKILL.md                         # 四步工作流 + 触发描述
├── scripts/
│   ├── csv_to_md.py                 # 「分类,字段名,值」CSV/xlsx → resume.md
│   └── render.py                    # resume.md + 模板(+accent) → HTML → PDF (WeasyPrint)
├── agents/openai.yaml               # Codex UI 元数据
├── references/
│   ├── writing-principles.md        # STAR/XYZ、量化、动词、校招vs社招、ATS、隐私、常见错误
│   ├── field-schema.md              # resume.md 格式约定 + CSV 字段映射（含 photo）
│   ├── templates-guide.md           # 4 模板 + 配色 + 证件照怎么选
│   └── role-presets.md              # 各岗位推荐小节顺序/侧重/技能线（JD 定向用）
└── assets/
    ├── resume.example.csv           # 可直接验证导入链路的三列表格
    ├── resume.example.md            # 按最佳实践写好的范例（gold standard）
    └── templates/{classic,modern,timeline,minimal}/  (resume.html.j2 + style.css)
```
参考素材（非 skill 一部分）：`reference/`（其它 3 个简历 skill）、`template/`（mujicv/markdown-resume 原始模板）。

## 5. 设计取舍（已和用户确认）
- **不采用** mujicv 的 `:::`/`icon:` DSL，也不换渲染器——保留数据驱动引擎（ATS 友好、STAR 润色、CSV 导入、一份数据源）。
- 红/深/蓝等配色变体做成 `--accent` 选项，而非每色一个模板。
- 岗位差异（算法/前端/产品…）做成 `role-presets.md` 内容参考，而非 37 个视觉模板。

## 6. 已验证（我这边）
- 4 套模板渲染 PDF 均成功、中文正常；accent 覆盖生效（如 timeline+purple、modern+wine）；photo 生效。
- 当前示例在四套模板中均应保持 1 页 A4。

## 7. Review / 测试清单（请 Codex 执行）
用 `BP=/opt/homebrew/bin/python3.13` 跑：
1. **自动化回归**：`$BP -m unittest resume_skill/evals/test_resume_skill.py -v`。
2. **四套渲染**：对 `resume_skill/assets/resume.example.md` 分别 `--template classic/modern/timeline/minimal`，打开 PDF 核对：中文不乱码、布局正确、A4 分页合理。
3. **配色**：`--template modern --accent orange`、`--accent "#1f6feb"` → 主色是否随之变化；`classic` 加 `--accent` 应无变化（预期）。
4. **证件照**：front matter 加 `photo: <某图>` → classic/modern/minimal 是否显示，删字段是否消失。
5. **通用润色**：丢一段"负责/参与"流水账，验证是否被改写成 STAR/XYZ + 量化、动词开头（依据 writing-principles.md）。
6. **JD 定向**：贴一份 JD → 是否输出匹配度小结（命中/缺失关键词）+ 按 role-presets 调整结构与措辞，且不编造。

### 可重点审查的点
- `render.py` 的 Markdown 解析（`parse_entry_heading` 对 ` | ` / ` · ` 的拆分、inline `**bold**` 转义）是否稳健。
- `csv_to_md.py` 对各「分类」的映射、`\n`/序号拆分是否有遗漏分类。
- 模板的打印 CSS：跨页（`page-break-inside: avoid`）、modern 侧栏底色跨页、`-webkit-print-color-adjust: exact` 是否都正常。
- SKILL.md 触发描述是否会过/欠触发。

## 8. 可继续扩展（按需）
- 中英双语版；更多 role-presets 岗位；把"校招1页"做成自动篇幅压缩检查；真·深色主题（注意打印耗墨与 ATS）。
