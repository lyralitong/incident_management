# 事故定级领域 Harness

领域 harness 是定级专用的确定性执行层，位于顶层通用 harness 和 `事故定级` Skill 之间：

```text
Router → 事故定级 Skill → 定级领域 harness → Cooper / 监控 / Excel
```

## 责任范围

| 模块 | 负责内容 | 模型是否可替代 |
|---|---|---|
| `policies/` | 业务映射、术语和定级口径版本 | 不能；模型只可抽取待审核条款 |
| `scripts/grading_core.py` | 回升时间、故障点数、L0S 等纯计算 | 不能 |
| `scripts/grading_workflow.py` | 把已归一化证据组装成稳定的定级结果 envelope | 不能 |
| 取数适配器 | URL 参数、时间范围、字段和重试 | 不能 |
| 证据导出 | 对比表、完整明细、计算依据、回读 | 不能 |
| Skill | 询问、澄清、解释、报告叙述 | 可以 |

## 领域状态

```text
NORMALIZE_INPUT
→ RESOLVE_MAPPING
→ FETCH_STANDARD
→ FETCH_TIMESERIES
→ DETECT_FAULT_WINDOW
→ SELECT_BASELINE
→ COMPUTE_GRADING
→ COMPUTE_L0S
→ EXPORT_EVIDENCE
→ VALIDATE_RESULT
```

每个状态的输出必须是 JSON 产物，并记录 `policy_version`、数据源、窗口、字段、过滤维度和错误。缺失或不一致时状态为 `pending`/`blocked`，不让模型越过校验继续生成确定结论。

## 当前迁移策略

`policies/incident-grading-policy.md` 保存原有完整规则和映射表，作为迁移基线。新代码优先承载通用且高风险的算法；业务标准阈值逐个转换为带版本的机器可读规则后，才从 Markdown 中删除，避免一次迁移造成口径丢失。

`evidence-excel.md` 和 `scripts/export_incident_evidence.py` 属于领域 harness 产物，不再由 Skill 直接决定脚本参数之外的行为。
