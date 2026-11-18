# Router + Skill + Harness 迁移状态

更新时间：2026-11-13（Asia/Shanghai）

## 已完成

- [x] 将 `AGENT.md` 收敛为 Router 提示词和能力边界。
- [x] 增加机器可读路由表 `router/routes.yaml`。
- [x] 建立顶层 harness 的 manifest、状态机、重试、审批、幂等和时钟约定。
- [x] 增加事故输入、定级结果和运行 manifest 的 JSON Schema。
- [x] 将原定级长 Skill 保存为版本化迁移政策。
- [x] 将定级 Skill 改为交互层，明确禁止模型自行实现定级算法。
- [x] 将证据 Excel 脚本和说明移动到定级领域 harness。
- [x] 将回升时间、含首尾分钟数、L0S 计算和定级结果 envelope 实现为纯函数并添加测试。
- [x] 为其他 Skill 增加 `kind`、`mode`、副作用和审批元数据。

## 下一阶段

- [ ] 将事故管理映射表从政策 Markdown 转为带版本和校验和的 JSON/YAML catalog。
- [ ] 将各业务定级标准的阈值逐条转换为机器可执行规则；转换前保留 Markdown 作为对照源。
- [ ] 实现 Cooper、监控 MCP 和 DChat 的适配器，将网络重试、字段校验和完整过滤参数接入状态机。
- [ ] 实现持久化 run manifest、断点恢复和真实幂等记录。
- [ ] 用真实或脱敏回放数据增加端到端 golden tests，并验证报告渲染与证据 Excel 一致。
- [ ] 为改进项提醒接入每日调度器和发送回执回读。

## 验证

在定级领域 harness 脚本目录运行：

```bash
python3 -m unittest discover -s . -p 'test_*.py' -v
```

当前结果：14 个测试通过。
