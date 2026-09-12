# agentjoey-workspace

**agentjoey 的个人 Claude Code skill / plugin 合集。**

这个仓库本身就是一个 [plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins)：clone 下来零依赖、不需要 `npm install`，加进 Claude Code 就能直接装。

## 安装

```bash
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install <plugin-name>@agentjoey-workspace
```

只想要其中某个 skill，不装整个 plugin：

```bash
cp -R plugins/<plugin>/skills/<skill> ~/.claude/skills/
```

## 收录的 plugin

| Plugin | 解决的问题 |
|---|---|
| [**behavior-driven-testing**](plugins/behavior-driven-testing) | 门禁全绿但 bug 照样上线 —— 因为测试打在了方便的内部边界上、喂的是 happy synthetic data。规定**在哪里**测、以及什么才算「真的能跑」：真实边界 + 真实数据形状/量级，加上对运行中系统的探针。 |
| [**linear-roadmap-maintenance**](plugins/linear-roadmap-maintenance) | agent 写完代码没人更新 Linear，而事后用定时任务从 60 个 commit 重建状态要 8–40k token 还容易猜错。把 Linear 变成**任务队列**：按优先级取单 → 做 → 同一 session 关单，维护成本压到一次任务的 ~3%。 |

## 仓库结构

```
.claude-plugin/marketplace.json   # marketplace 清单 —— 新 plugin 必须登记在这里
plugins/<name>/                   # 每个 plugin 一个目录
  .claude-plugin/plugin.json      #   名字/版本/描述（name 必须与目录名一致）
  README.md                       #   这个 plugin 解决什么问题
  skills/<skill>/SKILL.md         #   带 YAML frontmatter，name 必须与目录名一致
              references/*.md     #   按需加载的细节，保持 SKILL.md 精简
              scripts/*           #   确定性的部分交给脚本，别让模型去算
  commands/*.md                   #   斜杠命令（可选）
templates/plugin/                 # 新 plugin 的骨架，复制即用
scripts/validate.py               # 一致性校验，CI 也跑它
CLAUDE.md                         # 在本仓库里干活的约定
```

## 加一个新 plugin

```bash
cp -R templates/plugin plugins/my-plugin
mv plugins/my-plugin/skills/skill-name plugins/my-plugin/skills/my-skill
# 改 plugin.json / SKILL.md 里的 name，登记进 .claude-plugin/marketplace.json，在上表加一行
python3 scripts/validate.py -v
```

写 skill 的具体约定见 [CLAUDE.md](CLAUDE.md)。

## 校验

```bash
python3 scripts/validate.py      # 只报错误
python3 scripts/validate.py -v   # 连通过的检查一起列出
```

检查 marketplace 登记项与磁盘上的目录是否对得上、`plugin.json` / `SKILL.md` 的 name 是否与目录名一致、description 是否缺失或超长、有没有「躺在 plugins/ 里但没人能装」的孤儿 plugin，以及 skill 脚本能否编译。纯标准库，无依赖；每次 push 和 PR 由 GitHub Actions 跑。

## License

Private — All rights reserved.
