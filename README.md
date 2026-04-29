# Agent
### 1. 真正的多Agent通信

- 用 `MessageBus` 实现类似 Kafka / RabbitMQ 的机制
- Agent之间完全解耦

### 2. 有“角色分工”

- Planner → 思考
- Executor → 干活
- Reviewer → 监督
- 这才是 AutoGPT / CrewAI 的核心思路

### 3.有“共享记忆”

`memory.write("results", results)`

可以扩展为：

- Redis
- 向量数据库（Milvus / FAISS）

###  4. 可接入大模型（关键升级点）

把 Executor 改成调用 LLM：

`def` call_llm(prompt):`
    return openai.ChatCompletion.create(...)`



可以加入场景

## 场景1：自媒体矩阵

- Planner：选题
- Executor：
  - 写小红书
  - 写抖音脚本
  - 生成标题
- Reviewer：优化内容

## 场景2：电商运营

- Planner：制定营销策略
- Executor：
  - 生成商品文案
  - 分析销量
- Reviewer：ROI评估

## 场景3：AI公司内部自动化

- 自动写周报
- 自动分析数据
- 自动生成PPT

