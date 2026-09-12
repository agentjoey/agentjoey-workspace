# 在本仓库里干活的约定

这是一个 **Claude Code skill / plugin 合集**，不是应用仓库。这里没有构建、没有 `node_modules`、没有部署 —— 交付物是 markdown 和少量零依赖脚本。别往里加包管理器。

## 结构规则

- 每个 plugin 一个目录 `plugins/<name>/`，**必须**登记进 `.claude-plugin/marketplace.json`，否则没人能装（校验器会报错）。
- 三处 name 必须完全一致：目录名、`plugin.json` 的 `name`、marketplace 条目的 `name`。skill 同理：目录名 == `SKILL.md` frontmatter 的 `name`。
- 命名一律小写连字符：`linear-roadmap-maintenance`，不要 `LinearRoadmap`。
- 新 plugin 从 `templates/plugin/` 复制，别从零手写。
- 改完跑 `python3 scripts/validate.py -v`，再提交。

## 写 skill 的约定

1. **`description` 是唯一决定 skill 会不会被加载的东西。** 写 agent 能真正观察到的触发条件（文件类型、工具、工作阶段、症状），不要写抽象主题。「Use when …」开头。
2. **SKILL.md 控制在 ~150 行以内。** 细节放 `references/`，让 agent 需要时再读；确定性的计算放 `scripts/`，别让模型去算它算不准的东西。
3. **开头给 core principle**：这个 skill 防的是哪个失败模式、为什么显而易见的做法会失败。放之四海而皆准的原则等于没写。
4. **给 red flags**：agent 能自检的可观察症状，不是泛泛的告诫。
5. **给一组正反例**：❌ 默认做法为什么失败，✅ 同一个 case 用这个 skill 怎么做，差别要看得见。
6. **成本写进步骤里**（几次工具调用、大概多少 token）。agent 会照着权衡。
7. 脚本零依赖、只用标准库（`python3` / `sh`），并且 `chmod +x`。这个仓库要保持 clone 下来即可用。

## 文档语言

仓库级文档（README、CLAUDE.md）用中文；plugin 内部文档和 SKILL.md 用英文 —— 它们是给 agent 读的，也可能被别人复用。

## 提交规范

```
feat: 新增 plugin / skill
fix: 修复
docs: 文档
refactor: 重构
chore: 杂项
```

不要在 commit message、PR、代码注释或任何推到仓库的内容里写模型标识。
