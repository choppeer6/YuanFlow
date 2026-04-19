"""
YuanFlow - 测试与交互入口

支持三种模式：
  1. 预设流程执行
  2. 交互式对话
  3. 直接 Agent 调用
"""
from Executor import Executor
from Flow import Flow
from Node import Node
from RAG import rag_node
from LLM import llm_node
from agent import run_agent


# ── 工具节点 ──────────────────────────────────────────

def prompt(x):
    """原样传递输入"""
    return f"{x}"


def output(x):
    """打印最终结果"""
    print(f"\n💬 结果: {x}")
    return x


# ── 预设流程 ──────────────────────────────────────────

def build_agent_flow():
    """构建 Agent 工作流: prompt → agent → output"""
    flow = Flow()
    flow.add_node(Node("prompt", prompt))
    flow.add_node(Node("agent", run_agent))
    flow.add_node(Node("output", output))

    flow.add_edge("prompt", "agent")
    flow.add_edge("agent", "output")
    return flow


def build_rag_flow():
    """构建 RAG 工作流: prompt → rag → llm → output"""
    flow = Flow()
    flow.add_node(Node("prompt", prompt))
    flow.add_node(Node("rag", rag_node))
    flow.add_node(Node("llm", llm_node))
    flow.add_node(Node("output", output))

    flow.add_edge("prompt", "rag")
    flow.add_edge("rag", "llm")
    flow.add_edge("llm", "output")
    return flow


def build_llm_flow():
    """构建纯 LLM 工作流: prompt → llm → output"""
    flow = Flow()
    flow.add_node(Node("prompt", prompt))
    flow.add_node(Node("llm", llm_node))
    flow.add_node(Node("output", output))

    flow.add_edge("prompt", "llm")
    flow.add_edge("llm", "output")
    return flow


# ── 交互模式 ──────────────────────────────────────────

FLOWS = {
    "1": ("Agent 模式 (自动选择工具)", build_agent_flow),
    "2": ("RAG 模式 (知识库检索)", build_rag_flow),
    "3": ("LLM 模式 (纯大模型对话)", build_llm_flow),
}


def interactive():
    """交互式对话入口"""
    print("\n" + "=" * 50)
    print("  🚀 YuanFlow 交互式工作流引擎")
    print("=" * 50)
    print("\n请选择工作流模式：")
    for key, (desc, _) in FLOWS.items():
        print(f"  [{key}] {desc}")
    print(f"  [q] 退出")

    choice = input("\n请输入选项: ").strip()
    if choice == "q":
        print("再见！")
        return

    if choice not in FLOWS:
        print("无效选项，使用默认 Agent 模式")
        choice = "1"

    desc, builder = FLOWS[choice]
    flow = builder()
    executor = Executor(flow)
    print(f"\n已选择: {desc}")
    print("输入 'quit' 退出\n")

    while True:
        query = input("🧑 你: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if not query:
            continue
        try:
            executor.run(query)
        except Exception as e:
            print(f"\n❌ 执行出错: {e}\n")


# ── 入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    interactive()
