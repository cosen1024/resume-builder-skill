# TODO

## 4. 英文/双语支持不彻底（待设计决策）

- `render.py` 的 `SIDEBAR_KEYWORDS` 只有中文关键词，英文简历的 `Skills` / `Languages`
  等小节不会进入 modern 模板侧栏。
- 模板硬编码中文标签：modern 的「联系方式」「个人简介」、classic/timeline 的
  「求职意向：」、以及所有模板的 `<html lang="zh-CN">`。
- 候选方向：front matter 增加 `lang` 字段，按语言切换标签与侧栏关键词；
  或提供英文版模板。需要先定设计再动手。

## 5. classic 模板长姓名可能与照片重叠（待确认设计）

- `classic/style.css` 中 `.hd.has-photo` 只给 `.intent` / `.contact` / `.summary`
  加了 `padding-right: 88px`，`.name` 没有；长英文名会伸到绝对定位的照片下方。
- 修复前需确认：姓名是否也应该避让照片，还是刻意允许姓名通栏。
