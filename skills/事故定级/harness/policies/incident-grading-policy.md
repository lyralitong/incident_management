---
name: incident-grading
description: 根据受影响业务、发生时间和可选影响指标自动取数并计算事故等级，输出结论、L0S扣除结果及故障日与对比日的分钟级Excel证据。用于事故定级，不执行定责或对外通报。
---

# 事故定级 Skill

## 触发条件

用户要求「事故定级」「判断事故等级」「这个事故是 P 几」等，或用户提供了受影响业务方、事故发生时间等定级线索。

## 启动输入（两项必填，影响指标可选）

| 输入 | 说明 | 示例 |
|---|---|---|
| 受影响业务方 | 须与下方「事故定级大盘映射表」中的业务方可匹配 | 网约车 |
| 事故发生时间 | **参考值**：使用者认为的大盘指标开始下降时刻（即故障起点）。实际以核心指标大盘曲线判定为准（见 Step 3），二者偏差大时需使用者确认（精确到分钟） | 2026-08-27 14:30 |
| 影响指标（可选） | 用户明确知道受影响指标时填写；未填写时由智能体列出该业务方支持的指标供选择 | 发单数 |

定级启动入口和指标选择规则：

1. **受影响业务方**：须能与映射表匹配；“两轮车”“能源”等模糊名称必须让用户选择具体业务。
2. **事故发生时间**：必须包含日期和分钟，默认时区为 `Asia/Shanghai`；这是用户提供的参考锚点，最终以大盘曲线核实。
3. **影响指标为可选输入**：
   - 用户已填写影响指标时，仅计算用户指定且能与映射表匹配的指标；无法匹配时列出候选并要求确认。
   - 用户未填写影响指标时，先列出该业务方在映射表中的全部支持指标，请用户选择。
   - 用户表示无法确认、不知道或要求智能体判断时，自动计算该业务方的全部可自动取数指标，最终等级取所有已计算指标中的最高等级；不得再次要求用户提供指标名称。
   - 映射表中没有大盘指标的指标仍须列出并标记“无法自动取数/需人工核实”，不影响其他可取数指标的计算。

## 自动取数原则（不得把计算数据反向要求用户填写）

- 事故影响指标（当用户未指定或无法确认时）：按上述规则从业务方映射表自动确定计算范围。
- 事故开始止损时间：由大盘曲线自动识别指标开始回升时刻。
- 事故完全恢复时间：由大盘曲线自动识别业务回到正常水平时刻。
- 事故期间实际值、正常基线、下降比例、完全不可用时段及持续时间：全部优先通过监控 MCP/大盘接口自动读取并计算。
- 用户只需提供受影响业务方、事故发生时间，以及可选的影响指标；不得要求用户补充上述指标数值、基线、影响开始/恢复时间或不可用时长。
- 仅当指标映射不存在、监控 MCP 不可用/无权限、返回无数据或数据无法形成可审计结论时，才报告具体自动取数缺口；同时给出大盘链接和缺口字段，不得把自动取数失败描述成用户输入缺失。

收集输入时的注意事项：
- 业务方名称模糊（如「两轮车」）时，列出映射表中的候选（两轮车-海棠湾 / 两轮车-黑马）让用户选择。
- 用户给的时间若为相对时间（「下午两点半」），确认具体日期。
- 影响指标让用户从映射表中该业务方支持的指标里确认；若用户未填写、无法确认或要求智能体判断，先展示候选并自动计算全部可取数指标，不要求其凭空填写指标数据。
- **时间只作参考锚点：最终事故/止损/恢复时间以核心指标大盘曲线判定为准，并与用户提供的事故发生时间核对。**

## 一、事故定级大盘映射表（全量数据，已内嵌）

以下映射已从 Cooper 协同表格 `2209747621081` 重新读取（字段：业务方、定级标准链接、定级标准指标、大盘指标、大盘指标名、大盘链接、接口人、备注）。大盘链接是唯一取数口径；链接中的全部维度参数必须按 Step 1 解析并传入 MCP。

### 网约车

定级标准：《国内网约车出行线上异常定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505816885

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 呼叫量 | 订单呼叫量(火眼链路) | huoyan_biface_platform_order_call_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&area=0&cluster_id=1%3D1&daqu=0&id=2621320590245496829&_is_pressure=%270%27 | — | — |
| 完单量 | 订单完成量(火眼链路) | huoyan_biface_platform_order_deal_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&area=0&cluster_id=1%3D1&daqu=0&id=2621320590245496829&_is_pressure=%270%27 | — | — |
| 乘客日活 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | 杨天骄 | — |
| 司机日活 | 网约车司机在线数(火眼链路) | huoyan_biface_wyc_driver_online_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&_is_pressure=%270%27&area=0&cluster_id=1%3D1&daqu=0&id=2621320590245496829 | — | — |
| 客服进线 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 花小猪

定级标准：《花小猪出行线上异常定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505760688

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 呼叫量 | 火眼——花小猪大聚合发单数 | huoyan_biface_kf_union_complete_order | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&area=0&channel_name=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E7%99%BE%E5%BA%A6%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E5%90%8C%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%87%BA%E8%A1%8C%27&channel_name=%27%E6%90%BA%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E7%89%B9%E6%83%A0%E8%81%94%E7%9B%9F%27&channel_name=%27%E5%85%A8%E9%83%A8%27&channel_name=%27%E5%A6%82%E7%A5%BA%E5%87%BA%E8%A1%8C%27&cityGroup=0&id=2598779361704281086&platform_mode=%27API%E6%8E%A5%E5%85%A5%27&platform_mode=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%E8%87%AA%E8%90%A5%27&platform_mode=%27%E5%AE%8F%E9%B9%84%27&platform_mode=%27-999%27&platform_mode=%27%E6%BB%B4%E6%BB%B4%E8%87%AA%E8%90%A5%27&platform_mode=%27%E7%81%B5%E7%8A%80%27&platform_mode=%27%E5%85%A8%E9%83%A8%27&product_id=%270%27&_is_pressure=%270%27 | — | — |
| 完成量 | 火眼——花小猪大聚合完成订单数 | huoyan_biface_kf_union_finish_order | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&area=0&channel_name=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E7%99%BE%E5%BA%A6%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E5%90%8C%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%87%BA%E8%A1%8C%27&channel_name=%27%E6%90%BA%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E7%89%B9%E6%83%A0%E8%81%94%E7%9B%9F%27&channel_name=%27%E5%85%A8%E9%83%A8%27&channel_name=%27%E5%A6%82%E7%A5%BA%E5%87%BA%E8%A1%8C%27&cityGroup=0&id=2598779361704281086&platform_mode=%27API%E6%8E%A5%E5%85%A5%27&platform_mode=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%E8%87%AA%E8%90%A5%27&platform_mode=%27%E5%AE%8F%E9%B9%84%27&platform_mode=%27-999%27&platform_mode=%27%E6%BB%B4%E6%BB%B4%E8%87%AA%E8%90%A5%27&platform_mode=%27%E7%81%B5%E7%8A%80%27&platform_mode=%27%E5%85%A8%E9%83%A8%27&product_id=%270%27&_is_pressure=%270%27 | — | — |
| 乘客日活 | 无（需人工核实） | huoyan_biface_kf_union_bubble_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&area=0&channel_name=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E7%99%BE%E5%BA%A6%E5%9C%B0%E5%9B%BE%27&channel_name=%27%E5%90%8C%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E8%85%BE%E8%AE%AF%E5%87%BA%E8%A1%8C%27&channel_name=%27%E6%90%BA%E7%A8%8B%E6%97%85%E8%A1%8C%27&channel_name=%27%E7%89%B9%E6%83%A0%E8%81%94%E7%9B%9F%27&channel_name=%27%E5%85%A8%E9%83%A8%27&channel_name=%27%E5%A6%82%E7%A5%BA%E5%87%BA%E8%A1%8C%27&cityGroup=0&id=2598779361704281086&platform_mode=%27API%E6%8E%A5%E5%85%A5%27&platform_mode=%27%E8%8A%B1%E5%B0%8F%E7%8C%AA%E8%87%AA%E8%90%A5%27&platform_mode=%27%E5%AE%8F%E9%B9%84%27&platform_mode=%27-999%27&platform_mode=%27%E6%BB%B4%E6%BB%B4%E8%87%AA%E8%90%A5%27&platform_mode=%27%E7%81%B5%E7%8A%80%27&platform_mode=%27%E5%85%A8%E9%83%A8%27&product_id=%270%27&_is_pressure=%270%27 | — | — |
| 司机日活 | 司机在线量(火眼链路) | huoyan_biface_hh_duse_driver_online_num | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2621218788783163389&area=0&odin_leaf=-1&__time=MINUTE | — | — |
| 客服进线 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 企业级

定级标准：《企业级线上异常定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505753440

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 呼叫量 | 火眼—实时订单呼叫量 | huoyan_biface_es_realtime_order_call_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&company_id=0&id=2406374407841776638&order_source=-1&use_car_type=0 | — | — |
| 应答量 | 火眼—实时订单应答量 | huoyan_biface_es_realtime_order_answer_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&company_id=0&id=2406374407841776638&order_source=-1&use_car_type=0 | — | — |
| 接驾量 | 火眼—企业级实时订单接驾量 | huoyan_biface_es_realtime_order_pick_up_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&company_id=0&id=2406374407841776638&order_source=-1&use_car_type=0 | — | — |
| 乘客日活 | 火眼—实时订单呼叫量 | huoyan_biface_es_realtime_order_call_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&company_id=0&id=2406374407841776638&order_source=-1&use_car_type=0 | — | — |
| 客服进线 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 两轮车-海棠湾

定级标准：《两轮车线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505766002

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 发单数 | 火眼——海棠湾发单数 | huoyan_biface_htw_order_pub | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&channel=-1&cityId=0&id=2431799840066241534 | — | — |
| 结束订单数 | 火眼——海棠成单数 | huoyan_biface_htw_order_sent | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&channel=-1&cityId=0&id=2431799840066241534 | — | — |
| 用户数 | 火眼——海棠发单用户数 | huoyan_biface_htw_order_user | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&channel=-1&cityId=0&id=2431799840066241534 | — | — |

### 两轮车-黑马

定级标准：《两轮车线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505766002

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 发单数 | 黑马发单数（确认开锁量） | bh_order_cnt | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city_id=0&id=2426530157859701758&zchannel=-1 | — | — |
| 结束订单数 | 黑马成单数（订单结束量） | bh_order_finish_cnt | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city_id=0&id=2426530157859701758&zchannel=-1 | — | — |
| 用户数 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 代驾

定级标准：《代驾线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205506035018

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 呼叫量 | 代驾实时订单呼叫量(包含报单) | daijia_order_publish_total_new | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&biz_type=-1&city_id=-1&from_channel=-1&id=2470672912604988414&send_type=-1&type=-1 | — | — |
| 完成成功量/完成量 | 代驾订单实时成单量(包含报单) | daijia_order_accept_total_with_place_order | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&biz_type=-1&city_id=-1&from_channel=-1&id=2470672912604988414&send_type=-1&type=-1 | — | — |
| 乘客日活 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 司机日活 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| GMV | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 货运

定级标准：《货运线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205506034112

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 发单数 | 货运实时发单成功量(预付成功+无预付发单成功) | freight_order_create_and_dispatch_cnt | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&freight_biz_type=-1&freight_business_mode=0&freight_car_type=0&freight_carpool_type=-1&freight_channel=0&freight_city_id=0&freight_service_level=-1&freight_sub_channel=-1&freight_transport_id=-1&id=2623203888307637245 | — | — |
| 结束订单数 | 货运实时完单量 | freight_order_finish_cnt | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&freight_biz_type=-1&freight_business_mode=0&freight_car_type=0&freight_carpool_type=-1&freight_channel=0&freight_city_id=0&freight_service_level=-1&freight_sub_channel=-1&freight_transport_id=-1&id=2623203888307637245 | — | — |
| 货主日活 | 无（需人工核实） | freight_estimate_item_nospider_cnt | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&freight_biz_type=-1&freight_business_mode=0&freight_car_type=0&freight_carpool_type=-1&freight_channel=0&freight_city_id=0&freight_service_level=-1&freight_sub_channel=-1&freight_transport_id=-1&id=2623203888307637245 | — | — |
| 司机日活 | 在线司机数(上班)(freight_work_driver) | freight_online_free_driver | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&freight_biz_type=-1&freight_business_mode=0&freight_car_type=0&freight_carpool_type=-1&freight_channel=0&freight_city_id=0&freight_service_level=-1&freight_sub_channel=-1&freight_transport_id=-1&id=2623203888307637245 | — | — |

### 能源-加油

定级标准：《能源线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505768457

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 订单支付量 | 加油核心指标-订单支付量(新) | huoyan_bi_monitor_chefu_platform_trade_qpm_new | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2560390331979793406 | — | — |
| 放行量 | 加油核心指标-放行量 | huoyan_bi_monitor_cf_amc_epower_order_release_num | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2560390331979793406 | — | — |
| 下单 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 支付 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 油站列表 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 油站详情 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 客服进线 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 能源-充电

定级标准：《能源线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505768457

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 订单创建量 | 充电核心指标-有效订单量 | huoyan_bi_monitor_amc_epower_operator_effective_order | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2560390331979793406 | — | — |
| 启动充电 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 桩站列表 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 设备扫码 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 桩站详情 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 客服进线 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 滴滴支付

定级标准：《滴滴支付线上故障定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505769149

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 支付成功量 | 滴滴支付交易成功总量（入金+出金+分账） | ddpay_success_count | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2511663864655905790&businessId=%27000%27&merchantId=%27000%27&tradeFilter=0&tradeType=0 | — | — |
| 支付成功GMV | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 绑卡成功量 | 绑卡成功次数 | huoyan_biface_ddpay_bind_card_success_count | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2604634440437075966 | — | — |
| 支付 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 绑卡 | 绑卡成功次数 | huoyan_biface_ddpay_bind_card_success_count | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2604634440437075966 | — | — |
| 免密开通 | 免密签约成功人数 | huoyan_biface_ddpay_agreement_success_total_user | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2604634440437075966 | — | — |
| 一键付款曝光/绑定 | 一键付款成功次数 | huoyan_biface_ddpay_success_count_quickpay | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&businessId=%27000%27&id=2673177088000791549&merchantId=%27000%27&tradeType=%270%27 | — | — |
| 影响用户量 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |
| 客服进线量 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 滴滴信贷

定级标准：《滴滴信贷线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505765780

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 借款提交量 | 火眼—支用订单数 | huoyan_biface_trade_bill_wirhdraw_amount | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&funds_channel_id=0&funds_plan_code=%270%27&funds_source_id=0&id=2540990764641422334&product_id=0&step=%270%27&t_status=0&trade_flag=-1&trade_mode=-1 | — | — |
| 放款 | 火眼—支用订单数 | huoyan_biface_trade_bill_wirhdraw_amount | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&funds_channel_id=0&funds_plan_code=%270%27&funds_source_id=0&id=2540990764641422334&product_id=0&step=%270%27&t_status=1&trade_flag=-1&trade_mode=-1 | — | — |
| 分发 | 支用分发结果(manhattan_loan_withdraw_dispatch_result) | manhattan_loan_withdraw_dispatch_result | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2510486414404092926&fundsSourceNum=100&__time=FIVE_MINUTE&dispatchModel=0&funds_source_id=0&trigger_rule=%270%27 | — | — |
| 授信 | 火眼—授信成功数 | huoyan_biface_loan_market_credit_key_node | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=FIVE_MINUTE&funds_channel_id=0&funds_source_id=0&id=2446250113652232190&product_id=0&scene=%270%27 | — | — |
| 客服进线工单量 | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 数据

定级标准：《数据故障定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505734124

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 无（需人工核实） | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 监控报警异常

定级标准：《监控报警异常定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505701775

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 无（需人工核实） | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### ESE（体验技术）

定级标准：《ESE（体验技术）线上服务异常定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505757911

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 进线 | 客服-进线渠道-客服中心进线总数 | kefu_call_in_channel_all_count | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2527994559749686270&tenantId=%27didi%27 | — | — |
| 工单关闭 | 工单关闭 | monitor_worksheet_upgrade_without_batch_close | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2527994559749686270&tenantId=%27didi%27 | — | — |
| 工单升级 | 工单升级 | monitor_worksheet_upgrade_without_batch_create | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2527994559749686270&tenantId=%27didi%27 | — | — |
| 工单创建 | 工单创建 | monitor_worksheet_upgrade_without_batch_create | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&id=2527994559749686270&tenantId=%27didi%27 | — | — |

### EP

定级标准：《EP（效能）事故定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505665179

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 无（需人工核实） | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 滴滴保险

定级标准：《滴滴保险线上问题定级标准》 https://cooper.didichuxing.com/knowledge/2204014852542/2207231296684

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 非车险受影响GMV | 无（需人工核实） | 无（需人工核实） | 未提供 URL | — | — |

### 国际化出行

定级标准：《国际化出行线上问题定级标准及处理流程规范》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505733180

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 呼叫-稳定性国家 | No_of_Calls_With_Anycar | huoyan_biface_ue_monitor_global_order_stat_with_anycar_stable | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&id=2620196007819872253&pressure_type=%27%27&product_id=0&ue_stable_country_list=%27PA%27 | — | 稳定性国家：巴西、墨西哥、哥伦比亚、阿根廷、智利、埃及、澳大利亚 |
| 呼叫-非稳定性国家 | No_of_Calls_With_Anycar | huoyan_biface_ue_monitor_global_order_stat_with_anycar_no_stable | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2620218839866017789&ue_no_stable_country_list=%27JP%27%2C%27PA%27%2C%27CR%27%2C%27PE%27%2C%27NZ%27%2C%27DO%27%2C%27EC%27 | — | — |
| 完成-稳定性国家 | No_of_Rides | huoyan_biface_ue_monitor_global_order_stat_with_anycar_stable | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&city=0&id=2620196007819872253&pressure_type=%27%27&product_id=0&ue_stable_country_list=%27PA%27 | — | — |
| 完成-非稳定性国家 | No_of_Rides | huoyan_biface_ue_monitor_global_order_stat_with_anycar_no_stable | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2620218839866017789&ue_no_stable_country_list=%27JP%27%2C%27PA%27%2C%27CR%27%2C%27PE%27%2C%27NZ%27%2C%27DO%27%2C%27EC%27 | — | — |

### 国际化外卖

定级标准：《国际化外卖线上问题定级规则及处理流程规范》 https://cooper.didichuxing.com/knowledge/2204014852542/2205505812333

| 定级标准指标 | 大盘指标 | 大盘指标名 | 大盘链接 | 接口人 | 备注 |
|---|---|---|---|---|---|
| 下单-Global | Called Orders Num（下单数） | huoyan_biface_us_Global_soda_order_channel_called_orders_num | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2696558540994137085&city_id=0&country=All&pay_channel=All&status=All&__time=MINUTE | — | — |
| 下单-MX | Called Orders Num（下单数） | huoyan_biface_us_MX_order_called_orders_num_new | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2693964156335298557 | — | — |
| 下单-BR | Called Orders Num（下单数） | huoyan_biface_us_New_BR_order_called_orders_num_new | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2693965036803591165&city_id=0&ka_id=0&__time=FIVE_MINUTE | — | — |
| 下单-CO | Called Orders Num（下单数） | huoyan_biface_us_CO_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2694914424292008957&city_id=0&__time=MINUTE | — | — |
| 下单-CR | Called Orders Num（下单数） | huoyan_biface_us_CR_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=MINUTE&channel_id=0&city_id=0&id=2694913708106236925&ka_id=0 | — | — |
| 下单-PE | Called Orders Num（下单数） | huoyan_biface_us_PE_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?__time=FIVE_MINUTE&city_id=0&id=2694914824797705213 | — | — |
| 完单-Global | Completed Orders Num（完单数） | huoyan_biface_us_Global_soda_order_channel_completed_orders_num | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2696558540994137085&city_id=0&country=All&pay_channel=All&status=All&__time=MINUTE | — | — |
| 完单-MX | Completed Orders Num（完单数） | huoyan_biface_us_MX_order_completed_orders_num_new | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2693964156335298557 | — | — |
| 完单-BR | Completed Orders Num（完单数） | huoyan_biface_us_New_BR_order_completed_orders_num_new | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2693965036803591165&city_id=0&ka_id=0&__time=FIVE_MINUTE | — | — |
| 完单-CO | Completed Orders Num（完单数） | huoyan_biface_us_CO_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2694914424292008957&city_id=0&__time=MINUTE | — | — |
| 完单-CR | Completed Orders Num（完单数） | huoyan_biface_us_CR_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2694913708106236925&city_id=0&ka_id=0&__time=MINUTE&channel_id=0 | — | — |
| 完单-PE | Completed Orders Num（完单数） | huoyan_biface_us_PE_order_metrics | https://monitor.xiaojukeji.com/#/woater/dashboard?id=2694914824797705213&city_id=0&__time=FIVE_MINUTE | — | — |

### 仅定级标准、暂无大盘指标的业务方（无法自动取数，需人工核实）

| 业务方 | 定级标准 | 说明 |
|---|---|---|
| 数据 | https://cooper.didichuxing.com/knowledge/2204014852542/2205505734124 | 按定级标准人工评定；核心数据产品可用性参考 https://cooper.didichuxing.com/knowledge/2207920780763/2207988901247 |
| 监控报警异常 | https://cooper.didichuxing.com/knowledge/2204014852542/2205505701775 | 按定级标准人工评定 |
| EP | https://cooper.didichuxing.com/knowledge/2204014852542/2205505665179 | 按定级标准人工评定 |
| 滴滴保险 | https://cooper.didichuxing.com/knowledge/2204014852542/2207231296684 | 指标：非车险受影响GMV，无大盘指标，需人工核实 |
## 二、名词定义（口径，已内嵌）

以下名词定义已按 Cooper 表格最新内容同步；用户此前明确的报告格式、完整大盘参数传递、字段校验和责任属性约束继续有效。

| 名词 | 解释 | 备注 |
|---|---|---|
| **故障时长** | 从业务受损的时刻开始计算，到业务开始恢复上涨的时刻结束计算。分钟级报告必须包含首尾分钟桶。 | 事故开始、开始恢复和完全恢复仍按 Step 3 曲线判定；完全恢复不参与故障时长。 |
| **L0S/业务方不可用时长扣除** | P3+事故受损业务方：核心指标定级到 P0/P1 时扣除故障时长；P2 且下跌比例≥50%时扣除故障时长；P2 且下跌比例<50%时扣除“故障时长×实际下跌比例×2”；P3时扣除“故障时长×实际下跌比例”。 | 适用范围：代驾、能源（加油、充电）、两轮车（海棠湾、黑马）、货运、企业级、滴滴支付、滴滴信贷、效能（EP）、体验技术、增长技术、滴滴保险。责任属性未确认或明确为第三方责任时，不先行扣除。 |
| **中后台不可用时长扣除** | P3+（P0、P1、P2、P3）事故作为有责团队且破部门月度不可用时长目标：不可用时长=中后台事故完全恢复时间−中后台事故开始时间。 | 月度目标按“当月天数×1440×（1−全部可用性）”计算；国际化出行/国际化外卖对应地图团队全年可用性为99.98%。 |

## 执行流程

### Step 1：查映射

从上方内嵌映射表中按「业务方 + 定级标准指标」查出：定级标准链接、大盘指标名、大盘链接。

**大盘链接就是本次取数口径，必须按链接执行，不能只使用链接中的 dashboard `id` 或仅使用指标名。**

- 解析大盘链接的完整查询参数；对于 `#` 后的路由链接，解析 `#` 后 `?` 开始的 query string。保留所有参数名、参数值、重复参数及其含义，并进行 URL 解码。将参数分为“看板元数据”（如 `id`）和“指标维度过滤条件”：看板元数据用于记录，不作为指标维度发送；所有指标维度过滤条件都必须进入取数请求。
- 将解析出的维度过滤条件作为 `woater_query_metric_timeseries` 的过滤条件：工具显式支持的参数直接传参，工具未在 schema 中声明但大盘链接包含的参数放入 `extra_query` JSON；不得因为参数看起来是默认值、参数较多或当前指标“可能不需要”而删除。
- 大盘链接中的 `startTime`、`endTime`、`__time`仅在实际查询时替换为当前观察窗口的时间范围和粒度；其余过滤条件必须原样保留。链接中的 `id` 是看板/接口标识，不得替代映射表中的 `大盘指标名`。
- 不得自行新增大盘链接中没有的维度，也不得把 API 默认值当成大盘口径。若链接没有某个维度，就不补值；若取数工具强制要求该维度，必须报告参数冲突并停止该指标的自动定级。
- 报告和故障数据 Excel 的“过滤维度”必须记录最终实际发送的完整参数。每个指标至少用事故开始分钟做一次回读校验：返回值应与大盘该分钟显示值一致；不一致时先排查过滤参数、数值字段和时间粒度，不能继续计算或用另一套口径替代。

若该指标无大盘指标名：在候选指标和报告中标记“无法自动取数/需人工核实”，提供大盘链接和缺失字段，但不得主动要求用户填写故障期间指标值或正常水平值。若用户主动提供人工核实数据，可在标注来源后继续计算。

### Step 2：读取定级标准

用 WebFetch 抓取 Step 1 得到的定级标准链接，提取两类定级依据：

1. **核心指标定级表**：各等级（P0/P1/P2/P3/P4…）对应的指标下跌比例阈值 × 持续时长阈值（形如「下跌 ≥50% 且持续 ≥60 分钟为 P1」）。注意阈值通常是「比例 AND 时长」双条件，两个条件都要核对。
2. **核心功能定级表**：核心功能不可用比例/范围对应的等级（形如「核心功能 100% 不可用且持续 ≥X 分钟为 PY」）。

文档抓取失败时，重试一次；仍失败则标记“定级阈值无法自动获取”，保留标准链接并暂停该指标的自动定级。不得把粘贴标准表格或阈值作为用户必填项；若用户主动提供规则，再标注来源后继续计算。

### Step 3：大盘曲线判定实际故障时间（核心步骤）

**原则：使用者提供的发生/止损/恢复时间仅作参考锚点，实际以核心指标大盘曲线判定为准。**

> 正常情况下大盘判定与使用者提供的时间相差不大（≤10 分钟）；**若相差大（>10 分钟），必须把双方时间列出，让使用者确认采用哪个后再继续定级**，不得擅自采用其中任何一个。

**3.1 取观察窗口数据（分钟级）**

通过 observe-cn 取数 MCP（调用规范见 Step 4 工具表），取事故当天核心指标的分钟级数据（`__time=MINUTE`）：

- **窗口范围**：使用者给的事故发生时间 **前 60 分钟 → 完全恢复时间后 60 分钟**；若完全恢复时间未提供，取事故发生时间后 3 小时。
- **用哪个指标**：优先用下跌最明显的核心指标；若影响指标有多个，每个指标都取观察窗口数据并逐指标判定，取**最早开始下降时刻**作为事故发生时间、**最晚开始回升时刻**作为开始止损时间（保守口径，报告中列各指标判定结果）。
- 若映射表中该指标无大盘指标名，跳过曲线判定，直接以使用者提供时间为准并在报告中注明。

**3.2 计算正常水平基线**

- 正常水平 = 使用者给的事故发生时间**前 30 分钟**指标均值。
- 若该 30 分钟段本身异常（已处于下跌/数据缺失/剧烈抖动），向前扩展到前 60–90 分钟，取最平稳的连续 30 分钟段。
- 若仍无法获得平稳段（如凌晨低峰期、指标绝对值过小、波动极大），标记**「曲线判定置信度低」**，此时以使用者提供时间为主，并在报告中说明。

**3.3 判定事故发生时间（= 大盘指标开始下降的时刻）**

先明确分钟桶口径：`__time=14:32:00` 表示 **[14:32:00, 14:33:00)** 这一整分钟的观测桶，不能把接口返回时间当成秒级拐点，也不能因为后续 14:33 才跌破某个阈值就把开始时间顺延到 14:33。

从未受影响的正常基线末分钟之后向后扫描，找**第一个已出现持续性下行证据的分钟桶** t：

- t 相对前一个正常分钟出现明确下行，且 t、t+1、t+2 连续保持下行/低位（中间允许单点小幅抖动）；
- 后续不应在短时间内回到正常水平，且相对至少一条可用历史同期曲线出现同向异常下降；
- “连续 3 分钟低于正常水平 ×90%”是**确认条件**，不是把开始时间顺延到首次跌破 90% 的分钟。若 t 已是曲线从正常平台掉头的首个受影响桶，即使 t 仍略高于 90% 阈值，也应记录 t，并在依据中同时写出后续阈值确认分钟。

例如：14:31 尚处正常平台，14:32 首次明显下探，14:33、14:34 延续低位，则事故开始记为 14:32；不能因 14:33 才满足“低于90%”而记为14:33。

即：曲线从正常水平掉头向下、持续走低且未能收复的**首个受影响分钟桶**，就是大盘指标开始下降的时刻。

若只满足“低于事故前均值”而不满足历史同期对比，输出“未识别到可归因于事故的指标下降”；此时影响开始、开始止损和完全恢复时间均记为“未检出”，不得为了得出时长而强行选择曲线拐点。

**3.4 判定开始止损时间（= 大盘指标开始回升的时刻）**

严格区分“谷底分钟”和“开始回升分钟”，二者不能混写：

- **谷底分钟**：故障窗口内实际值最低的分钟桶，记为 `valley`。若最低值连续持平，谷底取持续低位区间的最后一个分钟桶；若之后又创新低，更新谷底。
- **开始回升分钟**：谷底之后第一个实际值严格高于谷底值的分钟桶，记为 `recovery_start`。后续分钟只用于确认该候选回升没有被新的更低点推翻，不用于把开始回升时间顺延到确认分钟。
- 若候选桶之后出现更低值或再次回到谷底低位、表明只是短暂反弹，则该候选不成立；更新谷底后，重新寻找其后的第一个高于谷底值的分钟桶。不得将谷底本身记为开始回升时间。

**判定与确认必须分开记录**：先按分钟时间顺序找到 `recovery_start` 候选，再检查其后至少 2 个分钟桶。若后续没有创新低或重新探至谷底低位，则确认回升成立，但开始回升时间仍是候选桶时间，不是这两个确认桶中的较晚时间。例：14:48=9,590 为最低点，14:49=9,675 是谷底后的首个更高值，14:50=10,041、14:51=10,844 延续上升；因此谷底记 14:48，开始回升/止损时间记 **14:49**，不能记 14:48，也不能等确认后改记 14:50 或 14:51。报告中可另列确认依据“14:50、14:51 持续上升”。

要点：
- 口径只判到「指标开始回升」为止，**不需要等到指标恢复到正常水平**（恢复到正常水平属 3.5 完全恢复时间，单独判定，不参与故障时长）。故障时段包含开始下降分钟桶和开始回升分钟桶两个端点。
- 谷底区反复波动（探底回升后又创新低或重新探至谷底低位）时，废弃被推翻的候选，从最新谷底之后重新判定；确认分钟只作证据，不能替代最初有效回升分钟。若数据噪声导致有效回升候选仍无法区分，在报告中列出谷底、候选分钟、原始值和后续确认值，并标为待确认，不得悄然选择较晚分钟。

**3.5 判定完全恢复时间（指标回到正常水平）**

- 指标恢复到 **≥ 正常水平 × 95% 且后续 10 分钟不再跌破 90%** 的首个分钟点。
- 若观察窗口结束仍未恢复，提示「指标在观察窗口内未恢复，请使用者人工确认实际恢复时间」。

**3.6 与使用者提供时间对比**

| 对比结果 | 处理方式 |
|---|---|
| 差 ≤ 10 分钟 | 视为一致，**采用大盘判定时间**，报告中同时列出双方时间 |
| 差 > 10 分钟 | 用 AskUserQuestion 列出对比表（使用者提供 vs 大盘判定 + 判定依据曲线），**让使用者确认采用哪个**后继续 |
| 曲线判定置信度低 | 以使用者提供时间为主，报告中标注 |

**3.7 计算故障时长（口径见上方名词定义）**

> **故障时长 = 大盘指标开始下降的时刻（最终确认的事故发生时间）→ 大盘指标开始回升的时刻（最终确认的开始止损时间）**，不是到完全恢复时间！完全恢复时间仅用于不可用时长扣除等场景，不参与故障时长。

同时计算 **止损耗时 = 开始止损时间 − 事故发生时间**（与故障时长同值）、**完全恢复耗时 = 完全恢复时间 − 事故发生时间**，一并在报告中体现。

### Step 4：指标取数

通过 observe-cn 指标取数 MCP（本地代理，已配置于 WorkBuddy，来源 https://mcphub.intra.xiaojukeji.com/square/observe-cn ）读取 Step 1 得到的**大盘指标名**。

**可用工具及调用规范（已实测，工具名以此为准）**：

| 工具 | 用途 | 关键参数 |
|---|---|---|
| `woater_query_metric_timeseries` | woater 大盘指标取数（**映射表大盘指标名均为 woater 指标，首选此工具**） | `metric`=大盘指标名（如 `huoyan_biface_platform_order_call_num`）；`startTime`/`endTime` **必须用单引号包裹**，如 `'2026-08-26 14:00:00'`；`__time`=粒度（MINUTE / FIVE_MINUTE / TEN_MINUTE / FIFTEEN_MINUTE / THIRTY_MINUTE / HOUR / DAY） |
| `woater_list_metric_tags` | 查询 woater 指标的占位符（维度）信息 | `path_param_1`=指标 ID（数字） |
| `odinmonitor_query_metric_timeseries` | odin 监控曲线时序数据 | `endpoint_counters` 列表：`{start, end}` 为 **unix 时间戳**，`ns` 必须以 `collect.` 开头（cluster 级），`metric` 为点分名（如 `rpc.counter`），`tags` 为有序键值串 `tagk1=v1,tagk2=v2`，`step` 必填（取 fullmatch 返回值） |
| `odinmonitor_list_metrics` / `odinmonitor_list_metric_tags` / `odinmonitor_find_series_ids_by_tags` | odin 指标检索链路（ns → metric → tagkv → counter） | 依次用于确定 ns 下有哪些指标、指标有哪些维度、哪条曲线有数据 |

**大盘 URL 参数执行规则（强制）**：Step 1 解析出的链接维度过滤条件是取数请求的唯一维度来源；看板元数据（如 `id`）只记录、不作为指标过滤条件。调用 `woater_query_metric_timeseries` 时，必须把每一个维度参数逐项传入；显式参数和 `extra_query` 合并后不得丢失任何链接过滤参数。以货运为例，大盘链接中的 `freight_transport_id=-1` 表示全部运力；不传该参数会落到 API 默认值 `0`，可能把大盘显示的 181 查询成默认运力的 8，属于错误口径。任何一个链接过滤参数缺失、被默认值覆盖或被替换成其他值，都必须视为取数失败并重新请求。

查询请求的时间参数只允许按当前窗口改写：`startTime`、`endTime` 和 `__time`由本次取数步骤设置；`metric`必须使用映射表中的大盘指标名；其它 query 参数保持链接值不变。报告中必须同时列出：大盘链接、解析后的完整过滤参数、实际数值字段（`order_cnt`/`num`/`y`）和事故开始分钟校验值。

**⚠️ 返回字段选择规则（关键）**：`woater_query_metric_timeseries` 的数值字段因指标而异，必须检查实际响应。按 `order_cnt` → `num` → `y` 的优先级选择：存在 `order_cnt` 时使用 `order_cnt`（与大盘页面显示一致）；否则存在 `num` 时使用 `num`（如货运发单数 `freight_order_create_and_dispatch_cnt`）；仅当前两者均不存在时使用 `y`。若三者均不存在，列出返回字段并标记为数据结构异常，不得猜测数值字段。

**取数步骤**：

1. **故障时段数据**：以 Step 3 **最终确认的事故发生时间 → 开始止损时间**为故障时段（Step 3.1 的观察窗口数据已覆盖该时段，直接截取计算，无需重复取数）。**注意：故障时段包含事故发生时间到开始止损时间之间的全部分钟点（含两端点）**，而非仅含起点不含终点。例：17:11-17:13 则取 17:11、17:12、17:13 三个分钟点的数据。
2. **第一轮基线数据（必须先取两条）**：
   - **前一天同期**：事故前一天同一时刻（如事故 08-27 14:30–14:55，则取 08-26 14:30–14:55）；
   - **上周同期**：上周同一天同一时刻（08-20 14:30–14:55）。
   - 注：Step 3.2 的「事故当天故障前正常水平」用于比较基线，不替代基线本身。
3. **基线差异检查与扩展取数**：
   - 将前一天同期、上周同期**分别**与事故当天故障前正常水平比较，并检查候选日期自身是否异常、缺失或剧烈抖动；不能只比较两个候选日期彼此之间的差异。
   - 默认将候选相对事故当天故障前正常水平偏差超过 20%，或两个候选基线彼此差异超过 20%，判定为“差距很大”；业务定级标准另有阈值时优先采用业务标准，并在报告中注明。
   - 只要第一轮前一天和上周同期均与事故当天正常水平差距很大、两者彼此差距很大，或两条数据均异常/不可用，就按固定顺序扩展取数：**上两周同期（事故日前第 14 天）→ 上三周同期（事故日前第 21 天）**。不得跳过上两周直接使用上三周，也不得把事故当天故障前水平当作唯一基线。
   - 扩展日期必须与故障时段完全对齐，并同时取对应日期的全天总量。
   - 若只有一个第一轮候选明显偏离，而另一个候选正常且可解释，可保留正常候选，但必须记录未扩展或扩展判断理由。
4. **全天日总量（用于累计影响计算）**：
   - 对所有实际参与比较的候选日期，通过 `woater_query_metric_timeseries` 取 `__time=DAY` 粒度的全天总量。
   - 例：事故 09-11，第一轮取 09-10、09-04；触发扩展后再取 08-28、08-21 的全天总量。
   - 按前述 `order_cnt` → `num` → `y` 字段选择规则取值。
5. **基线选择规则与终止条件**：
   - 在所有可用候选日期中，优先选择与事故当天故障前正常水平最接近且候选日期自身无异常的一条；其他候选保留用于对比和敏感性分析。
   - **扩展到上两周、上三周后，只要四个候选仍与事故当天故障前正常水平存在明显差距，四者之间无法形成稳定一致的基线，或四条候选数据不完整/不可审计，就立即终止自动定级并直接返回用户。**返回内容必须包括四个候选日期、各自与故障当天正常水平的差异、候选之间的差异、数据异常/缺失原因和可选的手动对比日期格式；此时不得自动选择基线、不得计算或输出确定事故等级，也不得用均值、估算值或事故当天数据替代。
   - 用户指定对比日期后，按同一时段和全天总量重新取数；日期仍异常时标记为待人工确认，不得用估算值替代。
   - **必须在报告中写明选择了哪条基线、是否扩展到上两周/上三周、每次扩展的触发原因及最终选择理由**。
6. **报告中必须列出所有已取候选基线的计算结果**（下跌比例、累计影响和数据状态），而非只列最终选中的一条。

**无法形成基线时的固定返回格式**：

```markdown
**最终定级：待定**
基线无法自动确定，已停止自动定级。请手动指定一个或多个对比日期（格式：YYYY-MM-DD；如需指定时段，请同时给出 HH:mm-HH:mm）。

| 候选日期 | 与事故当天故障前正常水平差异 | 与其他候选差异 | 数据状态/原因 |
|---|---:|---:|---|
| 前一天 | XX.XX% | XX.XX% | 正常/异常/缺失 |
| 上周 | XX.XX% | XX.XX% | 正常/异常/缺失 |
| 上两周 | XX.XX% | XX.XX% | 正常/异常/缺失 |
| 上三周 | XX.XX% | XX.XX% | 正常/异常/缺失 |
```

收到用户指定的对比日期后，才重新取对应日期的同一故障时段和全天总量，并继续计算；在此之前禁止输出推测等级。

**降级策略**：MCP 未连接、调用报错（如 woater 返回 `backend returned status 403`，表示当前账号无该 API 权限）或指标无数据时，输出具体错误、影响的指标和大盘链接，标记该指标“无法自动计算”，并继续计算其他可用指标。不得主动要求用户人工查数或提供数值；用户主动提供人工核实数据时，才可作为补充来源继续计算。

### Step 5：计算与定级

对每个受影响指标：

- **基线总量** B = 所选基线故障窗口内全部分钟原始值之和，基线窗口与故障窗口对齐，同样包含两端点全部分钟点；标准要求分钟级均值时另外计算，不能将均值混入总量公式；
- **故障期间实际总量** A = 故障时段内**全部分钟点**原始值之和（含事故发生时间和开始止损时间两个端点）；
- **下跌比例** = (B − A) / B × 100%；
- **影响指标量级** I = 故障时段内实际受影响的业务总量（如“影响完单量 20,000 单”），默认 I = max(B − A, 0)。若业务标准指定其他影响量公式，按原文自动取齐所需数据后计算；不得以故障期间实际总量 A、每分钟均值或同比日期全天总量替代 I。
- **事故时段影响指标量占基线日总量比例（全天累计影响）** = I / C × 100%，其中 C 是**所选基线日同一指标全天总量**（Step 4 第4步已取），不是事故当天的全天总量。每条候选基线分别使用各自日期的全天总量做分母。
  - **何时必须计算**：受影响业务的定级标准中**只要包含**累计影响/全天影响阈值条款（绝大多数业务定级标准都有，如企业级 P2 条件 3「累计≥1%」、P3 条件 2「累计≥0.5%」；花小猪、网约车等同），则**必须计算并对照阈值**，与「下跌比例+时长」作为两条独立定级路径，最终等级取高。
  - **报告展示**：只要指标量级 I 和基线日总量 C 可用，就必须计算并展示此比例；标准未设置累计影响阈值时，仅作事实披露，不将其自行转化为定级条件。纯核心功能无可比指标时写“不适用”；I、C 缺失或 C 为零时写“无法计算”及具体原因。
  - **禁止臆测不包含**：不允许因为"没读到"或"标准大致看过没印象"而判定为不包含。如不能确认，**必须先通过 cooper 读取定级标准原文核实**，再决定是否计算。误判会导致定级等级降低（如本次企业级事故标准明文有 0.5% 累计阈值，跳过会漏掉一条 P3 定级路径）。
- **下跌持续时长** = 故障时长（Step 3）；
- **下跌单量（缺失单量）** = B − A。**单量类门槛一律指"下跌单量/受损单量"（基线总量 − 实际总量），不是基线总量、不是故障期间总量**。企业级定级标准 V1.8 的 P1-P4 均含下跌单量门槛（P1≥2万 / P2≥1万 / P3≥5000 / P4≥2500），网约车等标准无单量门槛——每个业务的条件结构不同，必须逐字核对原文；
- 将「下跌比例 × 持续时长 ×（如标准含有的）下跌单量」代入定级标准的核心指标定级表（各条件为 AND 关系，全部满足才成立），得到该指标的**指标等级**；
- **⚠️ 阈值表述必须逐字引用定级标准原文，禁止凭印象转述或简化**。历史教训：曾把"下跌单量≥5000单"误读为"基线总量≥5000单"，导致企业级定级虚高（P3→实为P5）。单量类、比例类、时长类、累计类条件的分子分母口径，判定前必须在报告中原文引用并逐项核对。

若用户报告了核心功能受损（映射表中标注「核心功能」的行，如下单、启动充电、油站列表等），按定级标准的**核心功能定级表**评定**功能等级**。

### Step 6：判定 L0S/业务方不可用时长扣除

先分别记录“核心指标路径等级”“最终定级及定级因素”“责任属性及其依据”。最终定级可以由其他维度提高，但不得以提高后的等级套用核心指标扣除公式。

1. 业务方须在名词定义中的 L0S 适用范围内，且定级因素为核心指标受损、核心指标路径本身为 P1～P3、已确认非第三方责任，三项同时满足才计算。
2. 因核心功能、体验、资损、舆情或 G 侧影响定级，或明确为第三方责任，输出“L0S/业务方不可用时长扣除：0 分钟（不扣除）”及原因。
3. 核心指标路径为 P4 及以下时不扣除；不得用 P3+ 的集合条件自动纳入 P0。未覆盖的等级不外推公式。
4. 核心指标满足 P1～P3 但责任属性缺失或定级因素无法确认时，仅将扣除结果标记“待定”并列出具体缺口。无需因此中断指标取数、定级报告或 Excel 导出；不得把“未确认第三方”推断为“非第三方”。

通过适用性检查后，令 T 为该业务核心指标故障时长（分钟），r 为故障时段实际下跌比例的小数值（如 40% 取 0.40），按以下公式计算：

| 核心指标路径等级 | 实际下跌比例 | L0S 扣除（分钟） |
|---|---|---|
| P1 | 按实际取数 | T × 100% |
| P2 | r ≥ 50% | T × 100% |
| P2 | r < 50% | T × r × 2 |
| P3 | 按实际取数 | T × r |

报告列出 T、r、等级、责任依据、公式和代入结果。使用未四舍五入的 r 计算，最终分钟数展示两位小数；不得把 40% 当作 40 参与乘法，不得对同一业务多个指标的扣除简单相加。此规则只处理 L0S，不能替代中后台扣除规则。

### Step 7：导出故障数据 Excel

每次有可确定故障时段和同比日期的指标定级，都必须交付真实 `.xlsx` 文件，不能只返回大盘链接、截图、CSV 或虚构的文件路径。导出前读取 [Excel 数据源要求及脚本用法](../evidence-excel.md)，使用 [export_incident_evidence.py](../scripts/export_incident_evidence.py)。

- 数据范围：**指标开始下跌前 10 分钟至指标开始恢复后 10 分钟**，含两端；“开始恢复”是开始止损时间，不是完全恢复时间。故障当天和同比日期均取同一时间范围的每分钟原始值。对查询终点不包含在结果内的接口，将请求终点额外延后 1 分钟，再按要求裁剪。
- 排版遵循用户截图：第一行 B、C 列为同比日期和故障日期；第二行 A 列为“时间”，B、C 列为实际业务指标名称；其后每分钟一行。每个指标一个对比 sheet，另保留含双方完整日期时间的原始明细和计算依据。
- 导出窗口两侧各 10 分钟仅作取证，**不能计入**故障时段 A、B、影响指标量级或定级公式。报告与 Excel 必须使用相同的同比日期、指标 ID、过滤维度、数值字段和故障窗口。
- 缺失分钟标“缺失”，真实零值写数值 0；不插值、不补零。故障窗口内缺失时不输出确定指标等级；仅取证缓冲区缺失时保留已有结论并披露缺口。重复时间戳或未拆分维度必须先处理为唯一曲线，再导出。
- 未能确定故障窗口或同比日期时，报告相应字段写“未检出/待定”，故障数据源写“未生成（具体原因）”，不编造窗口或文件。文件生成失败时报告实际错误；定级已具备依据的可保留结论，但交付状态写“未完成（Excel 未生成）”。

### Step 8：汇总输出

**最终定级 = 业务标准中各已核实维度的最高等级**，包括核心指标、核心功能、体验、资损及适用的舆情/G 侧调整。每个等级必须有数据和条款依据。

以下字段式格式取代旧版九列表格作为默认汇总。标题固定为“事故定级报告（智能体计算结果，供参考，最终以评审裁定为准）”；**标题后第一行必须为“最终定级：Px”**。缺少关键证据时写“最终定级：待定”，不能在前面放推测等级。

**首部字段为强制格式，必须按以下顺序逐行输出；字段名、冒号和顺序不得改写。** 不得用表格、旧版“故障时间/指标计算/定级结论”分节替代这组字段。多业务方或多指标时，按业务方/指标分别重复完整字段组，最后再给总体最终定级。

1. `受影响业务方：`
2. `影响指标：`
3. `影响指标量级：`
4. `故障时段：`
5. `故障时长：`（必须明确“含首尾分钟桶”，同时给出分钟桶数量；例如端点差 14 分钟时写“14 分钟（含首尾分钟桶，共 15 个分钟桶）”）
6. `事故时段影响指标下跌比例：`（同一行必须写 `同比日期：`）
7. `事故时段影响指标量占基线日总量比例：`
8. `不可用时长扣除：`
9. `定级标准：`
10. `故障数据源：`

字段口径：

- **受影响业务方、影响指标**：使用正确业务名称，如“货运”“发单数/完单量”；`num`、`order_cnt`、`y` 只是取数字段，放在计算依据，不作为影响指标名称。
- **影响指标量级**：输出故障时段受影响总量 I 及单位，如“影响完单量 20,000 单”。该字段不是实际发单/完单总量或每分钟均值。纯核心功能则给出受损功能与范围/人数，并将不适用的指标比例写“不适用”。
- **故障时段**：`YYYY-MM-DD HH:mm:ss（指标开始下跌）—YYYY-MM-DD HH:mm:ss（指标开始恢复）`，默认 Asia/Shanghai。两端都是分钟桶标签：开始下跌取首个持续下行桶；开始恢复取谷底之后首个高于谷底值且经后续数据确认有效的候选桶，报告时间使用候选桶本身，而非确认桶。**最低点/谷底时间必须单独记录，不能直接替代开始恢复时间**。例如 14:48 为最低点、14:49 首次高于谷底且 14:50、14:51 继续上升时，开始恢复记 14:49。分钟级数据秒显示 `00`，同时注明精度为分钟级；不能声称监控有秒级精度。未检出则写“未检出”，不构造时间和时长。
- **回升判定留痕**：每个指标的计算依据必须同时列出谷底分钟及实际值、开始回升候选分钟及实际值、用于确认的后续至少 2 个分钟及实际值，并明确“候选分钟=报告中的开始恢复时间；确认分钟仅用于验证”。若候选被新低推翻，列出被废弃候选及原因，改用最新谷底后的候选。
- **故障时长**：按现有名词定义的分钟口径填写；展示时间点数量和时间差可能不同时注明口径，避免与秒级显示混淆。多个指标分别展示自身时段与计算结果。
- **事故时段影响指标下跌比例**：(B − A) / B × 100%，B、A 均为相同故障窗口总量；**同比日期**为最终选定的历史对比日期，不限定为去年同日；**事故时段影响指标量占基线日总量比例**：I / C × 100%。比例展示两位小数，定级判断保留原始精度；分母为零/数据缺失写原因，不输出虚构百分比。
- **不可用时长扣除**：固定放在“定级标准”前，格式为“不可用时长扣除：<xx> 分钟，计算公式：<xxx>”。扣除值与公式必须按 Step 6 输出：正常扣除时写明 T、r 和代入结果；不扣除时写“0 分钟，计算公式：不适用（<不扣除原因>）”；责任或定级因素未确认时写“待定，计算公式：待定（<具体缺口>）”，不得把待定显示成 0 分钟。
- **定级标准**：给出实际读取的标准名称和可点击链接。**故障数据源**：给出生成的 Excel 文件可点击链接和覆盖时间范围；不能用指标大盘链接替代文件。
- 多业务、多指标按同样字段逐项列出，不能合并成一个无法对应指标的比例。正文汇总之后保留计算公式、A/B/I/C 代入值、时间判定依据、所有已取候选日期的比较结果、最终选择理由，以及 L0S 扣除结果和责任属性。

```markdown
## 事故定级报告（智能体计算结果，供参考，最终以评审裁定为准）
**最终定级：<依据标准计算的等级/待定>**

受影响业务方：<业务方>
影响指标：<业务指标名>
影响指标量级：影响<指标名> <I> <单位>
故障时段：<YYYY-MM-DD HH:mm:ss>—<YYYY-MM-DD HH:mm:ss>
故障时长：<T> 分钟（含首尾分钟桶，共 <N> 个分钟桶）
事故时段影响指标下跌比例：<xx.xx>%，同比日期：<YYYY-MM-DD>
事故时段影响指标量占基线日总量比例：<xx.xx>%
不可用时长扣除：<xx> 分钟，计算公式：<xxx>
定级标准：[<标准名称>](<标准链接>)
故障数据源：[<Excel 文件名>](<实际生成的文件绝对路径>)（开始下跌前10分钟—开始恢复后10分钟，每分钟数据）

计算依据：实际总量 A=<...>；同比故障窗口总量 B=<...>；受影响总量 I=<...>；基线日全天总量 C=<...>；下跌比例=(B−A)/B；累计影响=I/C。列出监控指标 ID、实际数值字段、维度、时间精度、适用标准原文条款及逐项命中结果。
基线选择：列出所有已取候选日期的同窗口总量、与故障前水平的偏差、下跌比例、累计影响、数据状态及选择理由；扩展后仍不可靠时按 Step 4 固定格式直接返回，禁止推测等级。
扣除判定依据：定级因素=<...>；核心指标等级=<...>；责任属性=<...>；责任依据/待确认缺口=<...>。
```

## 边界与异常处理

1. **时间口径冲突（Step 3.6）**：大盘判定与使用者提供时间差 >10 分钟时，必须让使用者确认后再定级，不得擅自采用。若使用者确认采用其提供的时间，报告中保留大盘判定值作为参考并说明差异原因（如：口述时间对应的是感知时间、恢复策略调整等）。若差≤10分钟，也必须在报告中同时列出：首个受影响分钟桶、谷底分钟桶、开始回升候选桶、后续确认桶，以及各自原始值和判定依据；确认桶不得被误写成开始回升时间。
2. **跨等级模糊地带**（下跌比例或时长刚好卡在阈值边界）：按定级标准原文的取整/就高规则处理；标准未写明的，按就高原则定级并在报告中标注「边界情形，建议评审确认」。
3. **多个业务方同时受影响**：每个业务方独立走一遍 Step 1–8，最终定级仍取最高，并在报告中分业务方列示。
4. **指标取数 MCP 不可用/无权限**：给出错误信息、大盘链接和缺口字段，标记对应指标无法自动计算；继续处理其他可取数指标。不得将人工查数或提供数值作为继续定级的必需步骤；若全部指标均无法自动取数，则输出“最终定级：待定（自动取数失败）”，并列出人工核实入口。
5. **时间粒度**：大盘指标为分钟级，故障时长按分钟向上取整参与阈值判断（保守就高），并在报告中说明取整规则。
6. **低峰期/低基数指标**：凌晨或指标绝对值过小（如 <100/分钟）时曲线波动大，判定结果仅作参考，报告须标注「判定置信度低」。
7. 本 skill 只做定级；定级结果出来后，主动提示用户可以继续发起「事故定责」「事故通报」「事故复盘」。
8. **数据维护**：本 skill 内嵌的映射表与名词定义来自 Cooper 在线表格《事故管理信息表》（https://cooper.didichuxing.com/docs2/sheet/2209747621081，resourceId=2209747621081，含「名词定义」「事故定级大盘映射表」「事故管理知识库」三个 sheet，已同步 2026-11-12 版）。L0S 扣除和报告/Excel 格式以用户本次修订为准，不得被旧表格中的 P3+ 通用描述覆盖。国际化出行与国际化外卖的指标、区域拆分和看板字段以本次同步内容为准；若 Cooper 仅返回看板名称而非 URL，必须原样标注“未提供 URL”，不得沿用旧链接或自行拼接。表格更新后须同步更新本 skill 的内嵌数据（使用 `mcporter call Cooper.readContent resourceId=2209747621081 appId=2 range="事故定级大盘映射表!A1:H120" --output json`，必要时分段读取避免超时）。
