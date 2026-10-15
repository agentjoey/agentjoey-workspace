# Legacy sweep prompt

Hand this to the project's own session (it knows the product) once per project, with the parameters filled in. The Owner's standing ruling (2026-10-15): the project's session assesses each leftover Linear issue itself; still-valid work moves into the fixed project, everything else goes back to Notion.

```
任务：清理「{PROJECT}」在迁入 Intake 流程之前遗留的 Linear 和 Notion 内容。Owner 已授权你完成下面全部步骤，包括移动 issue、把无效的 issue 设为 Canceled。范围仅限本项目。

参数
- Project（Notion）：{PROJECT}
- 固定 Linear 项目（新，目前接近空）：{NEW_ID} {NEW_NAME}
- 旧 Linear 项目（遗留 issue 所在，可能在回收站，查询要带 includeArchived）：{OLD_ID} {OLD_NAME}
- 本地仓库：{REPO}
- 补充：{EXTRA}

准备
1. 先 git status。有自己的未提交改动，先按正常流程提交或暂存，再 git pull，确认仓库里的 SHARED-INTAKE v2 块在位。之后按块规则：只读 Project={PROJECT} 的 Requests 行，按数据源 id 查询，不按关键词搜 Notion。
2. 读一次 Intake 页 https://app.notion.com/p/3f98c5850c4380588d3fcfa22d8bc62e 的规则与 Requests 页面模板。这是唯一允许读其他项目内容的例外。

步骤
1. 盘点（只读）：列出旧项目里的全部 issue：id、标题、状态、父子关系、Milestone、有没有验收标准。
2. 逐条评定。「有效」= 范围清楚，有或能补出验收标准，与当前产品方向一致，没有被已完成的工作取代。其余（想法、待拍板的决策、方向已变、重复、已被取代）= 「无效」。拿不准的按无效处理，并在汇报里标出。
3. 有效的 → 搬进固定项目：
   - save_issue 改 project，issue id 不变，父子关系保持。
   - 在新项目里按旧 Milestone 的名字重建需要保留的 Milestone，再把 issue 挂回去（搬移会丢掉旧 Milestone）。
   - 描述首行加来源行：`Confirmed: 2026-10-15 Owner · 迁入前已在做或已计划的工作，自 {OLD_NAME} 搬来`，原描述不改。
4. 无效的 → 放回 Notion：每条在 Requests（data source b20c9483-9aab-42fe-bea0-edafb0ee193d）建一页，Project={PROJECT}。需要 Owner 拍板的 Stage=Pending，其余 Stage=Inbox。正文「讨论记录」写：它是什么、为什么判为无效或待决、原 issue 的关键内容摘要（issue 之后会被 Owner 手动删除，摘要要自足）。然后把原 issue 设为 Canceled，评论里写 Notion 页面链接。不要删除。
5. 已完成或已取消的旧 issue：写成一页 Issue archive 子页（父页 3f98c585-0c43-812c-9939-e5fb05702403，命名「{PROJECT}」），每条只记 id、标题、结果、日期，写完核对条数。
6. 核对：旧项目里开着的 issue 为 0；搬走条数 + 转 Notion 条数 = 盘点时开着的总数；归档页条数 = 已关闭条数。对不上就停下来汇报，不要继续。
7. 不改旧 Linear 项目本身（状态、名称），不删除任何东西。

汇报：一张表，每条 issue 一行：id、标题、判定（搬 / 转 Notion）、一句理由；末尾给汇总数字。
```
