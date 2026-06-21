# 模板选择指南

五套**布局**模板 + 一个**配色**选项 + 可选**证件照**。同一份 `resume.md` 可随时切换重渲染。
字体、字号、页边距和新模板验收标准见 `visual-design-system.md`。

## 布局（`--template`）

| 模板 | 风格 | 最适合 | 备注 |
|------|------|--------|------|
| `compact` | Markdown 文档流、单栏紧凑、细分隔线 | 中文技术岗、校招、希望稳定生成并保持一页 | **优先推荐**；结构简单、分页可预测、支持照片和配色 |
| `classic` | 单栏、黑白、工整 | 海投、不确定对方是否用 ATS、国企/银行、保守行业 | **解析最稳**，默认值。纯黑白，不受 `--accent` 影响 |
| `modern` | 左侧栏(联系/简介/技能) + 右主体、色块标题 | 互联网/产品岗，想要现代观感 | 视觉最突出；侧栏底色跨页自动铺满 |
| `timeline` | 单栏 + 左侧时间线竖轴、日期高亮 | 实习/项目密集、想强调成长脉络的应届/转行者 | 经历越多越出彩 |
| `minimal` | 极简纯白、大留白、字距拉开的小节标签 | 追求干净/设计感，内容精炼者 | 留白多、密度低，内容多时易到 2 页；ATS 友好 |

**怎么选**：希望稳定紧凑 → `compact`；拿不准/海投 → `classic`；想出彩、互联网 → `modern`；
经历多、强调时间线 → `timeline`；精炼、设计感 → `minimal`。

## 配色（`--accent`）

`compact / modern / timeline / minimal` 的主色可换。`classic` 始终黑白（保证 ATS）。

预设：`blue`(蓝) `teal`(青绿) `wine`(酒红) `ink`(墨黑) `purple`(紫) `green`(绿) `orange`(焦橙)；也可直接传 `#rrggbb`。
> 这些预设覆盖了常见的「蓝灰/沉稳/酒红/极客/暖色」等风格，无需为每种颜色单独建模板。

```bash
... render.py resume.md --template modern --accent wine
... render.py resume.md --template modern --accent orange
... render.py resume.md --template minimal --accent ink --out resume.pdf
```

## 证件照（可选，默认不放）

在 `resume.md` front matter 加 `photo: 路径/头像.jpg`（相对 resume.md 的路径即可）。
`compact`(右上角)、`classic`(右上角)、`modern`(侧栏顶部)、`minimal`(头部)会自动显示；
不加该字段就没有照片。`timeline` 为保持时间线完整，不显示照片。
- 国内岗位常用；**投外企/北美一般不放照片**，删掉 `photo` 字段即可。

## 篇幅控制
- 校招默认压到 **1 页**：精简要点、合并次要经历、收紧 summary。
- 社招允许 1–2 页。某模板超 1 页一点点，可调其 `style.css` 的 `font-size` / `margin` / `margin-bottom`。
- 模板差异位于各自目录的 `style.css`，共享离线字体与打印基线位于
  `assets/styles/resume-base.css`。
- 不要加入远程字体、在线图标或浏览器专属插件；这会降低离线渲染稳定性。

## 渲染命令
```bash
# 使用已安装依赖的 Python 3；虚拟环境用户替换为对应解释器路径
python3 scripts/render.py resume.md --template modern --accent teal --out resume.pdf
python3 scripts/render.py resume.md --template compact --accent teal --out resume-compact.pdf
python3 scripts/render.py resume.md --template minimal   # 默认配色
python3 scripts/render.py resume.md --html-only          # 只出 HTML，调样式时用
```
改完 `resume.md` 或某模板的 CSS 后重跑即可。想快速对比，分别渲染到不同文件名再看。
