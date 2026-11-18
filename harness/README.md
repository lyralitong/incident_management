# 顶层通用 Harness

顶层 harness 只放所有能力都应遵守的运行时能力，不放事故定级专属公式。它负责把模型调用变成可恢复、可审计、可控副作用的 workflow。

## 必须由顶层 harness 保证的能力

### 1. 状态和恢复

每次执行建立一个 `run_id` 和 manifest，状态只能沿允许的 transition 前进：

```text
RECEIVED → NORMALIZED → EVIDENCE_READY → COMPUTED → VALIDATED
         → DRAFTED → APPROVAL_REQUIRED → EXECUTED → VERIFIED
```

失败记录错误、输入摘要、工具调用和重试次数。进程中断后从最后一个 `succeeded` 状态恢复；已产生副作用的状态不能盲目重做。

### 2. 证据和版本

每个结论都绑定 `policy_version`、`source_snapshot`、`tool_call_id`、时间范围、时区和字段口径。模型生成的文字只能引用结构化证据，不能把未验证的推断写成事实。

### 3. Schema 校验

工具入参、模型结构化输出和最终产物都必须通过 Schema。缺失、类型错误、未识别枚举和来源不明的值进入 `NEEDS_INPUT` 或 `BLOCKED`，不能静默修复成猜测值。

### 4. 重试、幂等和外部动作

临时网络、网关、限流和进程中断按退避策略重试。发送 DC、发布文档等外部写操作必须有审批状态和幂等键；只有服务端成功回执并完成回读，才记为 `VERIFIED`。

### 5. 注入时钟

所有“今天”“距截止日期”等逻辑使用 manifest 中的 `execution_date` 和 `timezone`，不能直接依赖模型当前日期。这样定时执行和历史重放才会一致。

## 模型的职责

模型负责意图识别、候选解释、用户澄清、制度正文中的条款抽取和报告叙述。模型不负责决定状态转换、重试次数、收件人、幂等键、计算公式或是否已发送。

重试和副作用的详细约定见 `runtime/retry-policy.md` 和 `runtime/side-effects.md`。

## 状态字段

推荐每个状态至少保存：`status`、`started_at`、`finished_at`、`input_hash`、`output_artifact`、`error_code`、`retry_count`、`source_refs`。结构化契约见 `contracts/run_manifest.schema.json`。
