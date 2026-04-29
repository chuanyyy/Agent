import threading
import queue
import time
import uuid

# ======================
# 消息系统
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

    def register(self, name):
        self.queues[name] = queue.Queue()

    def send(self, msg):
        self.queues[msg.receiver].put(msg)

    def receive(self, name):
        return self.queues[name].get()


# ======================
# Memory（带状态）
# ======================
class Memory:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def write(self, key, value):
        with self.lock:
            self.data[key] = value

    def append(self, key, value):
        with self.lock:
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)

    def read(self, key):
        with self.lock:
            return self.data.get(key)


# ======================
# Agent基类
# ======================
class Agent(threading.Thread):
    def __init__(self, name, bus, memory):
        super().__init__(daemon=True)
        self.name = name
        self.bus = bus
        self.memory = memory
        self.bus.register(name)

    def send(self, to, content, msg_type="task"):
        self.bus.send(Message(self.name, to, content, msg_type))

    def run(self):
        while True:
            msg = self.bus.receive(self.name)
            self.handle(msg)

    def handle(self, msg):
        pass


# ======================
# Planner（含Chain-of-Thought）
# ======================
class Planner(Agent):
    def handle(self, msg):
        print(f"\n[Planner] 收到任务: {msg.content}")

        # ===== 长链推理（内部）=====
        thoughts = [
            "用户需要完成一个复杂任务",
            "需要拆解为多个步骤",
            "按照执行顺序安排"
        ]

        print("[Planner-CoT]", " -> ".join(thoughts))

        tasks = ["收集数据", "分析数据", "生成报告"]

        self.memory.write("tasks", tasks)
        self.memory.write("current_step", 0)

        self.send("Orchestrator", "TASK_READY")


# ======================
# Executor
# ======================
class Executor(Agent):
    def handle(self, msg):
        task = msg.content
        print(f"[Executor] 执行: {task}")

        time.sleep(1)

        result = f"{task}完成"
        self.memory.append("results", result)

        self.send("Reviewer", result)


# ======================
# Reviewer（带决策）
# ======================
class Reviewer(Agent):
    def handle(self, msg):
        result = msg.content
        print(f"[Reviewer] 检查: {result}")

        if "完成" in result:
            decision = "PASS"
        else:
            decision = "RETRY"

        self.send("Orchestrator", decision)


# ======================
# Orchestrator（核心逻辑流）
# ======================
class Orchestrator(Agent):
    def handle(self, msg):

        if msg.content == "TASK_READY":
            self.run_next_task()

        elif msg.content == "PASS":
            step = self.memory.read("current_step") + 1
            self.memory.write("current_step", step)
            self.run_next_task()

        elif msg.content == "RETRY":
            print("[Orchestrator] 任务失败，重新执行")
            self.run_current_task()

    def run_next_task(self):
        tasks = self.memory.read("tasks")
        step = self.memory.read("current_step")

        if step >= len(tasks):
            print("\n? 所有任务完成")
            print("结果:", self.memory.read("results"))
            return

        task = tasks[step]
        print(f"\n[Orchestrator] 分配任务: {task}")
        self.send("Executor", task)

    def run_current_task(self):
        tasks = self.memory.read("tasks")
        step = self.memory.read("current_step")
        self.send("Executor", tasks[step])


# ======================
# 启动系统
# ======================
class System:
    def __init__(self):
        self.bus = MessageBus()
        self.memory = Memory()

        self.agents = [
            Planner("Planner", self.bus, self.memory),
            Executor("Executor", self.bus, self.memory),
            Reviewer("Reviewer", self.bus, self.memory),
            Orchestrator("Orchestrator", self.bus, self.memory),
        ]

    def start(self):
        for a in self.agents:
            a.start()

    def run(self, task):
        self.bus.send(Message("User", "Planner", task))


# ======================
# 主程序
# ======================
if __name__ == "__main__":
    sys = System()
    sys.start()

    sys.run("生成市场分析报告")

    time.sleep(10)