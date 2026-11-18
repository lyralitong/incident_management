# 通用状态机约定

## 状态

| 状态 | 含义 | 允许的下一步 |
|---|---|---|
| `RECEIVED` | 收到用户请求 | `NORMALIZED` |
| `NORMALIZED` | 输入已归一化，歧义已消解 | `EVIDENCE_READY` 或 `NEEDS_INPUT` |
| `EVIDENCE_READY` | 所需证据已取回并登记 | `COMPUTED` |
| `COMPUTED` | 领域计算完成 | `VALIDATED` |
| `VALIDATED` | 结构和证据校验通过 | `DRAFTED` |
| `DRAFTED` | 已生成草稿或待执行计划 | `APPROVAL_REQUIRED`、`VERIFIED` |
| `APPROVAL_REQUIRED` | 等待用户或策略授权 | `EXECUTED` 或 `CANCELLED` |
| `EXECUTED` | 外部动作已调用 | `VERIFIED` 或 `FAILED` |
| `VERIFIED` | 回读确认完成 | 终态 |
| `NEEDS_INPUT` | 需要用户补充最小输入 | `NORMALIZED` |
| `BLOCKED` | 外部依赖或权限阻断 | `EVIDENCE_READY` 或 `NEEDS_INPUT` |
| `FAILED` | 非临时错误且重试耗尽 | `BLOCKED` 或终止 |
领域 harness 可以减少状态，但不能绕过 `VALIDATED` 和外部动作的审批/回读规则。
