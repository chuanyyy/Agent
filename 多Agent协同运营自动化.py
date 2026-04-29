import threading
import queue
import time
import uuid

# ======================
# 消息系统（Agent通信核心）
# ======================
class Message:
    def __init__(self, sender, receiver, content, msg_type="task"):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type


class MessageBus:
    def __init__(self):
        self.queues = {}

    def register(self, agent_name):
        self.queues[agent_name] = queue.Queue()

    def send(self, message: Message):
        if message.receiver in self.queues:
            self.queues[message.receiver].put(message)

    def receive(self, agent_name):
        return self.queues[agent_name].get()


# ======================
# 共享记忆
# ======================
class SharedMemory:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def write(self, key, value):
        with self.lock:
            self.data[key] = value

    def read(self, key):
        with self.lock:
            return self.data.get(key)


# ======================
# Agent基类
# ======================
class BaseAgent(threading.Thread):
    def __init__(self, name, bus, memory):
        super().__init__(daemon=True)
        self.name = name
        self.bus = bus
        self.memory = memory
        self.bus.register(name)

    def send(self, receiver, content, msg_type="task"):
        msg = Message(self.name, receiver, content, msg_type)
        self.bus.send(msg)

    def run(self):
        while True:
            msg = self.bus.receive(self.name)
            self.handle_message(msg)

    def handle_message(self, msg):
        raise NotImplementedError


# ======================
# Planner Agent（任务拆解）
# ======================
class PlannerAgent(BaseAgent):
    def handle_message(self, msg):
        print(f"[Planner] 收到任务: {msg.content}")

        # 拆解任务
        tasks = [
            "收集数据",
            "分析数据",
            "生成报告"
        ]

        self.memory.write("tasks", tasks)

        for t in tasks:
            self.send("Executor", t)


# ======================
# Executor Agent（执行）
# ======================
class ExecutorAgent(BaseAgent):
    def handle_message(self, msg):
        print(f"[Executor] 执行任务: {msg.content}")
        time.sleep(1)

        result = f"{msg.content} 完成"

        # 写入记忆
        results = self.memory.read("results") or []
        results.append(result)
        self.memory.write("results", results)

        # 发给Reviewer
        self.send("Reviewer", result)


# ======================
# Reviewer Agent（审核+反馈）
# ======================
class ReviewerAgent(BaseAgent):
    def handle_message(self, msg):
        print(f"[Reviewer] 审核结果: {msg.content}")
        time.sleep(0.5)

        # 简单审核逻辑
        if "完成" in msg.content:
            print(f"[Reviewer] ? 通过: {msg.content}")
        else:
            print(f"[Reviewer] ? 失败: {msg.content}")


# ======================
# Orchestrator（调度器）
# ======================
class Orchestrator:
    def __init__(self):
        self.bus = MessageBus()
        self.memory = SharedMemory()

        self.agents = [
            PlannerAgent("Planner", self.bus, self.memory),
            ExecutorAgent("Executor", self.bus, self.memory),
            ReviewerAgent("Reviewer", self.bus, self.memory),
        ]

    def start(self):
        for agent in self.agents:
            agent.start()

    def run(self, task):
        self.bus.send(Message("System", "Planner", task))


# ======================
# 主程序
# ======================
if __name__ == "__main__":
    system = Orchestrator()
    system.start()

    system.run("生成一份市场分析报告")

    time.sleep(5)

    print("\n? 最终结果:")
    print(system.memory.read("results"))