# 独立发布审查结果与修复记录

审查日期：2026-06-21

## 结论

独立审查结论为“修复后发布”。未发现 P0/P1 代码缺陷，发布阻塞项为 remote、LICENSE
和演示头像授权；另有四项 P3 改进建议。

## 已处理

- 配置目标 remote：`https://github.com/cosen1024/resume-builder-skill.git`。
- 添加 MIT License。
- 删除来源不明确的 JPEG 演示头像，替换为仓库原创 `demo-avatar.svg`。
- 将 `allow_implicit_invocation` 设为 `false`，并收紧 Skill 触发描述。
- 标题拆分增加 `・`（U+30FB）和 `•` 支持。
- xlsx 读取遇到 16 位以上数值时明确拒绝，提示将手机号/身份证号设为文本，
  避免 Excel 精度丢失后静默导入。
- 添加 classic 模板不依赖 `--accent` 的自动化回归测试。
- 英文 README 增加隐私默认保护说明。

## 保留的设计边界

- WeasyPrint 允许读取用户在 `photo:` 中指定的本地图片。该工具面向本地、自有输入，
  不作为不可信多租户服务运行。
- `classic` 通过 CSS 不引用 `var(--accent)` 保持黑白，并由测试锁定该约束。

## 验证要求

发布前执行：

```bash
/opt/homebrew/bin/python3.13 -m unittest resume_skill/evals/test_resume_skill.py -v
/opt/homebrew/bin/python3.13 \
  /Users/cosen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  resume_skill
git diff --check
```

并渲染 `compact`、`classic`、`modern`、`timeline`、`minimal` 五套 A4 PDF。
