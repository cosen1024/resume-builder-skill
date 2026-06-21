# resume-builder 发布前独立审查包

本文给另一个 AI、代码审查者或发布维护者使用。请独立检查源码和产物，不要只依据本文结论。

当前维护者验证快照（2026-06-21）：

- 20 项 unittest 通过。
- Skill `quick_validate.py` 通过。
- `git diff --check` 通过。
- 五套示例均为单页 A4，已人工检查首屏渲染。
- 独立审查已完成，结果和修复记录见 `docs/RELEASE_REVIEW_RESULT.md`。

## 1. 审查目标

确认 `resume-builder` 是否可以作为 Codex / Claude Code Skill 公开发布，重点检查：

- Skill 触发描述和工作流是否清晰、不过度触发。
- Markdown、CSV/xlsx 输入是否可靠且向后兼容。
- HTML 转义、模板选择、颜色输入和文件路径处理是否安全。
- 五套模板是否能稳定输出可搜索的 A4 PDF。
- 字体、字号、照片、分页和 ATS 友好性是否合理。
- 文档、示例、依赖和安装说明是否完整。
- 是否存在第三方版权、隐私数据或不应提交的本地文件。

## 2. 产品范围

发布产品是 `resume_skill/`：

```text
resume_skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── csv_to_md.py
│   └── render.py
├── evals/test_resume_skill.py
├── references/
│   ├── field-schema.md
│   ├── role-presets.md
│   ├── templates-guide.md
│   ├── visual-design-system.md
│   └── writing-principles.md
└── assets/
    ├── resume.example.csv
    ├── resume.example.md
    ├── examples/demo-avatar.svg
    ├── styles/resume-base.css
    └── templates/{compact,classic,modern,timeline,minimal}/
```

根目录的 `reference/`、`template/` 和 `output/` 是研究素材或生成产物，不属于发布产品，
且已由 `.gitignore` 排除。

## 3. 当前实现

```text
resume.md
  -> python-frontmatter + 自定义 Markdown 子集解析
  -> 数据字典
  -> Jinja HTML 模板 + 共享离线 CSS + 模板 CSS
  -> WeasyPrint
  -> 可搜索 A4 PDF
```

- Front matter 保存姓名、联系方式、求职意向、简介和可选照片路径。
- `##` 表示章节，`###` 表示经历条目，`-`/`*` 表示要点。
- `compact`、`modern`、`timeline`、`minimal` 支持主色；`classic` 固定黑白。
- `compact`、`classic`、`modern`、`minimal` 支持照片；`timeline` 不显示照片。
- 润色、JD 匹配和防止编造由 `SKILL.md` 及 references 指导调用模型完成。

## 4. 运行约束

本机所有 Python 和渲染验证必须使用：

```bash
/opt/homebrew/bin/python3.13
```

不要使用 Anaconda Python 运行 WeasyPrint，也不要改成 Chrome headless PDF。

## 5. 必跑命令

```bash
/opt/homebrew/bin/python3.13 -m unittest \
  resume_skill/evals/test_resume_skill.py -v

/opt/homebrew/bin/python3.13 \
  /Users/cosen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  resume_skill

git diff --check
git status --short
```

五套视觉回归：

```bash
mkdir -p /tmp/resume-builder-review

for template in compact classic modern timeline minimal; do
  /opt/homebrew/bin/python3.13 \
    resume_skill/scripts/render.py \
    resume_skill/assets/resume.example.md \
    --template "$template" \
    --out "/tmp/resume-builder-review/$template.pdf"
done
```

检查每个 PDF：

- A4 尺寸是否正确。
- 示例是否保持 1 页。
- 中文是否正常且文本可复制、可搜索。
- 联系方式、照片、日期和正文是否重叠或越界。
- 长内容是否自然分页，而不是截断。
- `modern` 多页侧栏底色是否连续。
- `classic --accent orange` 是否仍保持黑白。

## 6. 重点代码审查

### `scripts/render.py`

- `inline_md()` 是否可能产生未转义 HTML 或错误嵌套标签。
- `parse_entry_heading()` 对 ASCII/全角竖线、间隔点和空字段是否稳健。
- `photo` 和输入文件的相对路径是否按照 `resume.md` 所在目录解析。
- 自定义颜色是否只接受严格的六位十六进制。
- 模板发现是否只包含真正可渲染的目录。
- 输出 HTML 与 PDF 路径创建是否安全、错误信息是否清晰。

### `scripts/csv_to_md.py`

- CSV/xlsx 单元格中的冒号、换行、数字字符串和空值是否正确保留。
- 分类和字段映射是否遗漏常见简历栏目。
- 旧 `.xls` 是否给出明确错误。
- 身份证号等隐私字段是否不会进入最终 front matter。

### Skill 与 references

- `SKILL.md` 是否控制在必要工作流范围内，并正确链接详细 references。
- 是否明确禁止编造经历、数字、学历和技能。
- JD 匹配是否区分“已命中”“可改写”“真实缺失”。
- 模板、照片和岗位选择是否有足够清晰的默认策略。

## 7. 发布治理状态

- Git remote：目标为 `https://github.com/cosen1024/resume-builder-skill.git`。
- 项目许可证：MIT License。
- 演示头像：仓库原创 `demo-avatar.svg`，随项目按 MIT License 发布。
- 独立审查提出的代码 P3 已处理：显式调用、扩展标题分隔符、Excel 超长数字保护、
  classic 黑白回归测试和中英文隐私说明。

## 8. 给另一个 AI 的审查提示词

复制下面内容，并让对方直接读取仓库：

```text
请对 /Users/cosen/research/code/recruit/resume 做一次发布前独立审查。

这是一个 Codex / Claude Code 中文简历 Skill。发布产品是 resume_skill/，根目录
reference/、template/、output/ 不是发布内容。请先读 AGENTS.md、README.md、
README.en.md、RELEASE_REVIEW.md、resume_skill/SKILL.md，再按需读取 scripts、
references、templates 和 tests。

要求：
1. 当前只审查，不修改文件，不提交，不 push。
2. 所有 Python/渲染命令必须使用 /opt/homebrew/bin/python3.13。
3. 执行 RELEASE_REVIEW.md 的自动化与五模板测试。
4. 检查功能正确性、安全性、Markdown/CSV 解析、照片路径、分页、A4、中文字体、
   ATS 友好性、Skill 触发描述、README 中英文一致性和第三方版权边界。
5. 不要因为已有测试通过就默认实现正确，要直接阅读源码。

请按严重程度输出 findings，优先列阻止发布的问题，并为每项标注文件与行号。
若没有代码问题，也要单独列出发布阻塞项、残余风险和实际执行过的测试。
最后给出明确结论：可以发布 / 修复后发布 / 不建议发布。
```

## 9. 预期审查输出格式

```text
结论：

阻止发布：
- [P0/P1] 问题 — 文件:行号

一般问题：
- [P2/P3] 问题 — 文件:行号

测试：
- 命令
- 结果

版权与发布：
- remote
- LICENSE
- demo avatar

最终建议：
```
