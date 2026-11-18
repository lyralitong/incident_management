---
name: incident-grading
version: 2
kind: skill
harness: ./harness
policy: ./harness/policies/incident-grading-policy.md
description: 通过定级 harness 完成事故指标取数、故障窗口识别、基线比较、等级计算、L0S 判断和证据 Excel 交付；Skill 只负责用户交互、歧义澄清和结果解释。
---

# 事故定级 Skill

## 职责边界

本 Skill 是 Router 调用定级 workflow 的交互层，不自行实现定级算法。所有确定性逻辑必须通过 `harness/` 执行：

- 业务方、指标、时间和时区归一化；
- 大盘映射、完整维度参数解析和监控取数；
- 历史同分钟基线候选、事故开始、开始回升、完全恢复时间识别；
- A/B/I/C、下跌比例、累计影响、等级和 L0S 公式；
- 缺失、重复、非法值、权限失败和证据完整性检查；
- Excel 生成、回读校验和结构化结果输出。

政策原文和现行口径保存在 `harness/policies/incident-grading-policy.md`。政策升级必须产生新的 `policy_version`，不能只编辑本文件中的提示语。

## 启动输入

用户只需要提供：

1. 受影响业务方；
2. 带日期和分钟的事故发生参考时间；
3. 可选的影响指标。

业务方或指标无法唯一匹配时，列出候选并等待选择。用户不知道影响指标时，展示候选后让 harness 计算全部可自动取数指标，不能要求用户手工填写监控数值、基线、故障时长或恢复时间。

## 调用协议

Router 创建 `run_manifest` 后调用领域 harness，输入至少包含：

```json
{
  "run_id": "run-...",
  "business": "货运",
  "incident_time": "2026-10-12 14:41",
  "timezone": "Asia/Shanghai",
  "impact_metrics": [],
  "execution_date": "2026-11-13",
  "policy_version": "2026-11-12"
}
```

领域 harness 按以下阶段执行并为每阶段保存产物：

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

任一指标取数失败时，记录错误和大盘链接，继续处理其他互不依赖指标。全部指标不可计算时返回 `status=blocked` 或 `final_grade=null`，不得推测等级。

## Skill 的交互规则

- 输入不完整：只询问当前阶段最小缺口。
- 业务方和用户时间相差超过 10 分钟：展示两者和判定依据，等待用户选择；不得静默覆盖。
- 数据缺失、基线不稳定或政策条款无法核验：明确标记 `待定/待核验`，不以估算值补齐。
- 模型输出必须引用 harness 返回的结构化字段，不得自行重新计算或改写时间端点。
- 定级报告开头固定写“事故定级报告（智能体计算结果，供参考，最终以评审裁定为准）”和“最终定级：Px/待定”。
- 定级完成后可提示继续进行定责、通报或复盘，但不得把这些能力隐式执行。

## 结构化结果到报告的映射

harness 返回的 `grading_result.schema.json` 是唯一事实来源。报告渲染顺序固定为：最终定级、受影响业务方、影响指标、影响指标量级、故障时段、故障时长、下跌比例及同比日期、累计影响、不可用时长扣除、定级标准、故障数据源、计算依据和不确定性。

“开始恢复”必须使用 harness 返回的候选分钟；谷底分钟和后续确认分钟只能作为计算依据，不能替换开始恢复时间。Excel 必须链接到真实生成且回读通过的文件。

## 不允许的行为

- 不从模型记忆臆造标准阈值、业务映射、指标字段或大盘维度。
- 不把最终等级代替核心指标路径等级计算 L0S。
- 不把确认回升分钟顺延成开始回升分钟。
- 不把已生成草稿、已调用发送接口描述成已发布或已发送。
