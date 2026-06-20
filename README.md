# resume-builder

一个可直接使用的中文简历生成 Skill。它把简历内容保存在一份可编辑的
`resume.md` 中，再通过 Jinja 模板和 WeasyPrint 输出 A4 PDF。

当前版本优先保证“能用、稳定、容易修改”，没有追求庞大的模板数量或复杂网页界面。

## 特色

- **内容与样式分离**：修改一次 `resume.md`，可切换四套模板重新渲染。
- **中文求职场景优先**：内置校招/社招、STAR/XYZ、量化表达和 JD 定向指导。
- **数据可迁移**：支持对话录入，也支持三列 CSV/xlsx 导入。
- **ATS 与视觉兼顾**：`classic` 适合机器解析，`modern`、`timeline`、`minimal`
  提供不同视觉取向。
- **隐私默认收敛**：身份证号不会自动进入最终简历。

## 当前状态

已验证：

- CSV/xlsx 转 `resume.md`
- 四套模板生成中文 A4 PDF
- 预设配色和自定义 `#rrggbb`
- 可选证件照
- HTML 转义、YAML 特殊字符、标题分隔符等边界输入

能力边界：

- 当前只支持 `.csv` 和 `.xlsx`，不支持旧版 `.xls`
- Markdown 只解析本项目约定的标题、条目和简单行内格式
- JD 匹配和 STAR 润色由调用 Skill 的模型完成，不是独立评分算法
- 不提供网页编辑器、DOCX 导出和在线托管

## 环境

本项目在 macOS Apple Silicon 上使用以下解释器验证：

```bash
/opt/homebrew/bin/python3.13
```

安装依赖：

```bash
/opt/homebrew/bin/python3.13 -m pip install --break-system-packages -r requirements.txt
```

本机不要使用 Anaconda Python 运行 WeasyPrint，已知可能产生 glib/pango 冲突。

## 直接试用

先把示例 CSV 转成 Markdown：

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/csv_to_md.py \
  resume_skill/assets/resume.example.csv \
  -o output/resume.md
```

再渲染 PDF：

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/render.py \
  output/resume.md \
  --template modern \
  --accent orange \
  --out output/resume.pdf
```

也可以直接渲染已经润色好的示例：

```bash
/opt/homebrew/bin/python3.13 \
  resume_skill/scripts/render.py \
  resume_skill/assets/resume.example.md \
  --template classic \
  --out output/resume-classic.pdf
```

模板可选：

- `classic`：单栏黑白，ATS 优先
- `modern`：左侧栏布局，适合互联网岗位
- `timeline`：时间线布局，突出经历顺序
- `minimal`：轻量极简布局

配色可选：

`blue`、`teal`、`wine`、`ink`、`purple`、`green`、`orange`，或六位十六进制颜色。

## 安装为 Codex Skill

在仓库根目录执行：

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/resume_skill" ~/.codex/skills/resume-builder
```

重启 Codex 后，可以这样调用：

```text
使用 $resume-builder，根据我的经历生成一份后端开发校招简历。
```

如果用户提供 JD，Skill 会先分析命中和缺失关键词，再基于真实经历调整内容；不会主动编造经历或数字。

## 输入格式

`resume.md` 的完整约定见
[`resume_skill/references/field-schema.md`](resume_skill/references/field-schema.md)。

CSV/xlsx 使用三列结构：

```csv
分类,字段名,值
基本信息,姓名,库森
求职意向,期望职位,后端开发工程师
实习经历1,公司名称,云杉科技
实习经历1,职责描述,优化接口性能\n完善监控告警
```

导入结果只是内容骨架，建议继续按
[`writing-principles.md`](resume_skill/references/writing-principles.md)
补充背景、行动和可信的结果数据。

## 测试

运行自动化测试：

```bash
/opt/homebrew/bin/python3.13 -m unittest \
  resume_skill/evals/test_resume_skill.py -v
```

基础 Skill 结构检查：

```bash
/opt/homebrew/bin/python3.13 \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  resume_skill
```

PDF 属于视觉产物。修改模板后还应重新渲染四套 PDF，检查中文字体、分页、照片、
侧栏底色和内容截断。

## 目录

```text
resume_skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── csv_to_md.py
│   └── render.py
├── references/
├── assets/
│   ├── resume.example.csv
│   ├── resume.example.md
│   └── templates/
└── evals/test_resume_skill.py
```

`reference/` 和 `template/` 是本地研究素材，不属于发布版 Skill。
