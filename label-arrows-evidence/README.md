# 居中标签方向标记：实现与验证

冻结候选：`c4f28b89e6ee39edb1e0a09db96998bda27670f1`。实现提交：`2c1cf45f`，后续提交仅澄清自动避碰文档并刷新 ZIP。2026-11-04 通过 GitHub API 复核最新 dev 为 `63c9263e84bd3993cab8e09b3d69888857858635`；一次 Git HTTPS 查询遇到 SSL 连接失败，未将该失败当成版本验证。

## 用户选定的行为

- 不同请求与结果保留两条有向关系、独立 ID、标签与查询身份。
- 可显式选择同一路径；居中标签在线的两侧，小三角指明各自方向，省去重复端点箭头。
- `both` 仍是一条同义、对称关系，使用一个标签与两端箭头；`none` 仍是无向关联。
- `arrowPosition: "label"` 是 Architecture 可选呈现字段，只接受有非空标签的 `forward` 关系；默认仍是 `endpoints`。
- 自动配对、合并语义、自动改成共享路径均不在范围内。折线优先最长线段中点，几何位置打破等长平局；自动避碰可能移动未固定标签。

[浅色图](browser/label-arrows-light.png) · [深色图](browser/label-arrows-dark.png) · [交互 HTML](browser/label-arrows.html) · [窄屏图](browser/label-arrows-mobile.png) · [SVG](browser/label-arrows-light.svg) · [PNG 导出](browser/label-arrows-export-light.png)

窄屏维持项目既有的可横向平移画布，不声称一屏容纳全图。Desktop 1440×900；窄屏 390×844；原生 viewport 截图，`captureBeyondViewport:false`。

## 验证与失败记录

| 检查 | 结果与证据 |
| --- | --- |
| 定向测试 | 10 通过；[日志](focused-latest.log)。含往返、垂直、折线、固定标签、schema、Delta、Story。 |
| 浏览器 | 7 通过，0 跳过；[日志](browser-final.log)。Route 两方向选中不同 ID，Reach 保留两条，低细节下仍显示方向，浅／深色 SVG、PNG 导出和窄屏查询。 |
| 核心冒烟 | 19 通过；[日志](core.log)。 |
| 扩展影响检查 | 1,118 通过、80 条无 Chrome 的浏览器检查跳过，2 项待刷新产物失败；[原始日志](affected.log)。Checkout Delta 与 Gallery 刷新后专项 41 通过；[复测](artifact-followup.log)。不把跳过当成通过。 |
| 生成产物 | 模板、validators、品牌、版本及 golden 全通过；[日志](generated-final.log)。早期检查曾发现 31 份旧产物，随后正常再生成。 |
| 原图一致性 | 十类图的 15 份原有 SVG 与上一候选逐字节一致；[记录](legacy-svg-replay.json)。HTML 新增 locale／CSS，不声称 HTML 字节一致。 |
| 打包 | 官方 Node 22.23.2 / zlib 1.3.1-e00f703 构建；[最终日志](zip-final.log)。第二次构建与提交 ZIP 逐字节一致；[日志](zip-reproducibility.log)。在仓库外解包后运行 deliver，通过并保留[交付收据](package-delivery.json)。 |

实现过程中曾把标签小三角写成 SVG path，Viewer 将该图形误当作第二个可绘制边片段，Route 快照返回空。浏览器测试暴露后改用 polygon，保留现有关系身份算法；没有添加 Viewer 身份例外。此前失败输出仅在工具事件中，本目录没有伪造原始测试日志。

## 消融与简化

按仓库 simplify-codebase 的 Focused Change 范围，仅检查本次新增定位、图形和公开选项。尝试去掉专用标签定位、复用旧算法后，折线标签不再围绕同一段线路居中，10 项中 1 项失败；[消融日志](ablation-legacy-placement.log)。恢复该定位逻辑。保留局部切线与完整标签占位，分别负责方向准确和避碰边界；不引入配对状态、第二套关系图或新的路由引擎。

原图与默认合同保持不变。撤销本轮两个本地提交可恢复此前实现，无外部发布或数据迁移。

## 独立复核

按 impeccable 技能要求进行新的只读 finish review，结论为 **ship**，覆盖给出的浅／深／窄屏截图、SVG、源码与测试证据；不是独立浏览器重跑或维护者批准。检测器全文件产生 196 项既有提示，改动行上 0 项；[范围核查](design-detect-scope.json)，[原始输出](design-detect.json)。

文档复核指出“总是中点”的文字忽略了自动避碰，已改成优先中点并完成复查。DESIGN.md、PRODUCT.md 未改；已有 PRODUCT 结构漂移、缺少 design sidecar 不在本次范围。

## 新一轮真实生成

已完成官方 10 次与补充 2 次生成，逐例源码／业务审查、最终产物截图和两版原字节回放均保留在[完整报告](../benchmark-label-arrows-20261104/REPORT.md)。12 次都交付完成，但不宣称质量全面通过：标题遮住普通连线、Hive 基线事实错误和 SkillRoster 候选文字偏小已记入[问题及复现](../benchmark-label-arrows-20261104/ISSUES.md)。

Hive／MCO／Squad 自然采用 20 个标签箭头，补充场景采用 2 个。22 条关系的独立 Route 身份和浅／深色导出经核查，未发现本轮新样式回归；其余两项目未使用新呈现。官方两组修订轮次为 8／7，未缓存输入 token 为 356,730／492,357，输出为 44,730／45,596；不同内容和布局下的一组样本不能证明节省轮次或 token。[224 项证据完整性核对](../benchmark-label-arrows-20261104/audit-summary.json)均通过，不替代语义和视觉结论。原生会话与失败保留在[本地证据包](../benchmark-label-arrows-20261104/bundle-notes.md)，尚未公开上传。

[冻结计划](../benchmark-label-arrows-20261104/plan.json)：项目官方五项目 Architecture × base/candidate = 10 次，另加 2 次合成共享请求／返回场景。Codex CLI 0.144.0，`gpt-6.1-sol`、`medium`，每次 20 分钟，最多两场并发；保留全部失败与修复。费用按用户要求暂不统计，不做耗时提升结论。此前 benchmark 目录与历史失败记录保持原样，不能算作新候选运行。

前一轮的无向关联、对称同步与不同消息三份候选 JSON 已在本轮候选上原字节重放：均交付通过，canonical SVG 与原产物一致，见[重放摘要](../benchmark-label-arrows-20261104/reused-semantic-replay/summary.json)。这是确定性回放，不是新增 Agent 会话。
