# 本轮生成中发现的问题

这里保留适合后续单独开 issue 的事实，不修改原始 Agent 产物。10 次官方项目与 2 次补充生成均已完成并逐项审查，完整状态见 [REPORT.md](REPORT.md)。未发布 GitHub issue。

## Architecture 边界标题遮住连接线，交付检查仍通过

建议标题：`Architecture: boundary title masks connection routes while validation passes`

本轮 OpenPI candidate 又自然出现：子会话上方的 `Separate context · not an OS sandbox` 标题背景遮住两条进出线。图的主体可读，但此局部不应作为没有遮挡的合格图。

SVG 几何证据：标题 mask 为 `x=856..1060.4, y=350..366`，`create-child` 的垂直线位于 `x=995.05`，`child-events` 位于 `x=980`，均在 `y=136..370` 之间穿过标题背景。标题绘制在连接线之上。

- [最终 JSON](runs/openpi-candidate/workspace/output/openpi-subagent.architecture.json) · [HTML](runs/openpi-candidate/workspace/output/openpi-subagent.html) · [原始会话](runs/openpi-candidate/evidence/session.jsonl)
- [1440×900 原生截图](captures/openpi-candidate/viewport.light.png) · [全页截图](captures/openpi-candidate/fullpage.light.png)
- [同 JSON 交叉回放](replay/summary.json)：dev `63c9263e` 与候选 `c4f28b89` 都交付通过，布局、canonical SVG 完全相同。该图没有 `both`、`none` 或 `arrowPosition: label`，因此不是此次新标记机制特有的回归。

复现：在任一冻结包上运行 `node archify/bin/archify.mjs deliver architecture <该 JSON> <输出 HTML> --repo-root <OpenPI 677b495 checkout> --json`，查看子会话节点上方的边界标题。

预期：标题背景避开连接线，或者诊断指出实际遮挡。当前仅有交付成功不足以证明视觉无冲突。已有[前一轮最小复现及调查](../benchmark-20261104/ISSUES.md)可继续使用，本轮是新的自然输入证据，不宣称模型每次必现。

## 前一轮语义风险的状态

此前 Squad 将命令与返回结果合并为 `both` 的失败仍保留在[旧报告](../benchmark-20261104/ISSUES.md)。本轮 Squad 两边都没有采用 `both`；候选通过两条 forward 关系和标签箭头表达命令／返回。它是在首次验证后主动补全了两条返回关系。旧失败不被覆盖，一次新成功也不能证明模型以后不再误用。

本轮 Squad 候选另有上面的边界标题问题：`Workspace persistence · shared by CLI invocations` 遮住普通 `session-io` 连接进入 Session token files 的线段与箭头附近。该图采用 4 个新标记，但被遮挡的是另一个普通端点箭头。已保留[原图](captures/squad-candidate/viewport.light.png)、[三节点最小输入](issues/squad-boundary-title-mask/minimal.json)、[两版比较](issues/squad-boundary-title-mask/comparison.json)。缩减时保留涉事节点、线路与边界的几何，去掉其余关系和源码引用；两版都通过交付且 SVG 相同。该缩减是诊断回放，不计入 Agent 会话或首稿指标。

## Hive 基线生成图误称 task-scoped progress 会通过 PTY 推送给 orchestrator

建议标题：`Benchmark semantics: Hive task-scoped progress is incorrectly drawn as a PTY push`

这是官方真实生成任务产生的语义错误，不是新增箭头渲染问题，也不意味着布局校验应当能自动理解任意仓库的业务代码。

- Hive 源码固定 `f8f1343da6595a232f0baba7f0ea5b5a58fe0e9c`；错误产物来自 dev `63c9263e`、Codex `gpt-6.1-sol / medium` 的 base 会话。
- [原 JSON](runs/hive-base/workspace/output/hive-task-path.json) 的 `return-to-team` 被标为 `5 · PTY progress / result`，卡片又写 `Structured: progress messages / final report → team state + orchestrator PTY`。
- 同一图的 Worker 说明明确把进度定义成 `team message --dispatch ... --kind progress`。源码 [dispatch-message-store.ts:193](https://github.com/tt-a1i/hive/blob/f8f1343da6595a232f0baba7f0ea5b5a58fe0e9c/src/server/dispatch-message-store.ts#L193) 则仅为非 progress 消息建立 delivery outbox；给 orchestrator 的 report outbox 同样排除 progress。任务内进度是记录／查询，不触发该 PTY 投递。
- 适用范围限定为这里的 task-scoped progress；不能推广成所有 status 或非 progress 消息都不投递。

打开[最终 HTML](runs/hive-base/workspace/output/hive-task-path.html) 或[截图](captures/hive-base/viewport.light.png)查看 Team API → Orchestrator 线即可复查。源 JSON 在两版均交付通过且 SVG 相同，证明换 renderer 不会修正该错误事实。[完整会话](runs/hive-base/evidence/session.jsonl)保留两次布局失败与后续修复；修好布局后这个事实错误仍然存在。

预期：分别说明实时终端输出、可查询的任务进度和最终 report 投递。候选本次正确保留此区别，但一次模型对照不能证明新呈现字段造成了语义改进，也不能保证以后不会再错。适合补充为来源核对／生成评估的失败例，不建议按某个英文标签硬编码 schema 拒绝规则。

## SkillRoster 候选达到最低字号检查，但原生视口的上下文文字仍偏小

这是可读性改进候选，不能称作违反现有硬门槛。当前文档把 6px 定为失败底线、约 7.5px 定为桌面目标，两者有意区分。

- [原生 1440×900 截图](captures/skillroster-candidate/viewport.light.png)中，连线文字和部分上下文文字约 6.67px；[测量](captures/metrics.json)的 `minimumProjectedEdgeTextPx` 为 6.66897。没有观测到明显重叠，但比大图中的文字难读。
- 首稿实际触发了 5.47px 的投影字号失败。Agent 修紧布局后通过检查，再主动调整一条线路与 Apply/Undo 说明；[原会话](runs/skillroster-candidate/evidence/session.jsonl)保留了失败和修订。
- [全页截图](captures/skillroster-candidate/fullpage.light.png)使用更高的视口，会重新排版并放大图；不能拿这张图替代原生桌面可读性判断。
- 最终 JSON 没有新字段，两版回放布局和 SVG 相同。不是此次标签箭头的特有回归，也不能仅凭这一组不同布局证明候选让文字变小。

可讨论的后续方向：区分可交付底线与舒适阅读目标，让 Agent 收到未达到目标的非阻断反馈，或调整既有自适应画布策略。需要另行约定验收，不在本次功能内直接提高硬门槛。
