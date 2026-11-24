# engineering-conventions

把各仓库共用的工程约定收成**一份真源**，写进**每个 harness 都读的那个文件**，并且用**逐字节比对**代替肉眼比对。

## 它防的两个静默故障

**文件选错了，规则等于不存在。** 实测五个 harness 的可执行文件，看它们到底查哪个文件名：

| harness | 版本 | AGENTS.md | CLAUDE.md | GEMINI.md |
|---|---|---|---|---|
| Claude Code | 2.1.331 | 有 | 有 | — |
| codex | 0.166.0 | **只有这个** | 无 | 无 |
| kimi | 2.4.0 | 有 | 有 | — |
| agy | 1.5.2 | 有 | 无 | 有 |
| opencode | 1.19.3 | 有 | 有 | — |

`AGENTS.md` 是唯一被五个全部读取的文件。块放在 `CLAUDE.md` 里，在 Claude Code 下一切正常，而 codex 完全读不到 —— 不报错，agent 只是表现得像从没写过这些规则。

**漂移没有症状。** 两个仓库的块差一句话，评审时看不出来。等到两个 agent 在同类任务上按不同规则干活才会发现。

所以这个插件不让你"读一遍约定然后凭判断照做"，它提供真源文本和一个逐字节比对的脚本。

## 用法

```sh
/engineering-check <仓库> [<仓库> ...]   # 查版本和漂移，ok 表示逐字节一致
/adopt-engineering [<仓库>]              # 写入或更新块
```

`check` 会在 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 三个名字里找，并解析软链接 —— 一个真文件被三个名字指到只算一次。有问题时退出码 1：

| 状态 | 含义 |
|---|---|
| `MISSING` | 没有任何 agent 文件带这个块 |
| `DRIFT` | 块在，但正文和真源不一致 |
| `DUP` | 两个独立真文件都带，读两个文件的 harness 会加载两遍 |
| `NO-CODEX` | 块在，但不经由 `AGENTS.md` 可达，codex 看不到 |

## 一个真文件，多个名字

需要多个文件名时**不要复制文本**，留一个真文件、其余做软链接：

```sh
cd <仓库> && ln -sf CLAUDE.md AGENTS.md && ln -sf CLAUDE.md GEMINI.md
```

`check` 会显示成 `AGENTS.md=CLAUDE.md=GEMINI.md`。

## 结构

```
skills/engineering-conventions/
├── SKILL.md                              5 条 recipe + red flags
├── references/
│   ├── shared-engineering-block.md       唯一真源（v2，28 行）
│   └── scope-and-overlap.md              与用户级 CLAUDE.md 的重叠为何是故意的
└── scripts/
    └── engineering_block.py              render / check / apply，零依赖
```

改约定只改 `references/shared-engineering-block.md`，然后在各仓库跑 `check`（全部报 `DRIFT`）再 `adopt`。**永远不要直接改仓库里的块** —— 那正是漂移的来源。
