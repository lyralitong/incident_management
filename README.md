# 事后管理 Agent

本项目采用 **Router + Skill + Harness** 架构：

```text
Router（总 Agent：意图识别、路由、最小澄清）
  ├─ 顶层 harness（状态、证据、重试、权限、审批、幂等、时钟）
  └─ Skills（领域沟通与判断）
       ├─ 问题答疑
       ├─ 事故定级 ── 定级 harness（取数、窗口、基线、公式、Excel）
       ├─ 事故定责
       ├─ 事故通报
       ├─ 事故复盘
       └─ 改进项提醒 ── 定时 workflow
```

## 目录

- `AGENT.md`：Router 的系统提示词和能力边界。
- `router/routes.yaml`：可机器读取的意图、输入、输出和副作用路由表。
- `harness/`：所有能力共享的运行时契约、状态机、重试、审批和证据规则。
- `harness/contracts/`：运行 manifest、事故输入和定级结果的 Schema。
- `skills/`：面向用户的领域 Skill。
- `skills/事故定级/harness/`：只服务事故定级的领域 harness、政策文件、证据说明和确定性脚本。

## Agent 拆分建议

问题答疑、定级、定责、通报和复盘先保留在同一个事后管理 Agent 内，以共享事故上下文和统一权限边界。改进项提醒应作为独立的定时 workflow，而不是每次依赖聊天模型被唤醒。定级虽然有独立 harness，但不等于必须拆成独立 Agent；先让 Router 调用结构化定级 workflow，等到需要独立发布、独立权限或独立扩缩容时再拆。

## 稳定性目标

同一份输入、同一份数据快照、同一版政策和同一执行日期，必须得到相同的结构化计算结果。模型只负责意图识别、歧义澄清、制度条款抽取和自然语言解释；窗口识别、公式、输出校验和外部副作用由 harness 决定。

## 兼容与迁移

原来的长定级 Skill 已保存为 `skills/事故定级/harness/policies/incident-grading-policy.md`，作为现行口径的迁移来源。新的 `skills/事故定级/SKILL.md` 只保留交互协议和 harness 调用契约，后续规则应写入版本化政策或代码，不再把算法继续堆回 Skill。
