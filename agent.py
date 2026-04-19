import json
from LLM import llm_node
from RAG import rag_node
import numexpr


def weather_tool(query):
    """天气查询工具（示例）"""
    return "今天是晴天 25摄氏度"


def calculator_tool(query):
    """数学计算工具"""
    try:
        result = numexpr.evaluate(query)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


# 工具注册表 —— 新增工具只需在此添加
TOOLS = {
    "weather_tool": {
        "func": weather_tool,
        "description": "查询天气信息"
    },
    "calculator_tool": {
        "func": calculator_tool,
        "description": "计算数学表达式"
    },
    "RAG": {
        "func": rag_node,
        "description": "从知识库检索相关信息并回答"
    }
}


def _build_tool_list():
    """动态生成工具列表描述"""
    lines = []
    for i, (name, info) in enumerate(TOOLS.items(), 1):
        lines.append(f"  {i}. {name}: {info['description']}")
    return "\n".join(lines)


def agent_node(query):
    """Agent 决策节点：判断是否需要调用工具"""
    tool_list = _build_tool_list()
    prompt = f"""你是一个智能助手，可以使用以下工具：

{tool_list}

用户问题：{query}

请判断是否需要调用工具。

如果需要，请严格按照以下 JSON 格式返回（不要包含其他内容）：
{{"tool": "工具名", "input": "输入内容"}}

如果不需要工具，直接回答用户问题即可。"""

    response = llm_node(prompt)
    return response


def _fuzzy_match_tool(tool_name: str) -> str | None:
    """大小写不敏感地匹配工具名，返回注册表中真实 key，找不到返回 None"""
    for key in TOOLS:
        if key.lower() == tool_name.lower():
            return key
    return None


def parse_agent_output(text):
    """解析 Agent 输出，优先尝试 JSON 格式，兼容旧的 TOOL/INPUT 格式"""
    # 尝试 JSON 解析
    try:
        # 提取 JSON（处理可能的多余文本）
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(text[start:end])
            tool = data.get("tool", "").strip()
            input_text = data.get("input", "").strip()
            if tool:
                # Bug2 修复：大小写不敏感匹配
                matched = _fuzzy_match_tool(tool)
                return matched or tool, input_text
    except (json.JSONDecodeError, KeyError):
        pass

    # 兼容旧格式: TOOL: xxx / INPUT: xxx
    if "TOOL:" in text:
        try:
            tool = text.split("TOOL:")[1].split("\n")[0].strip()
            input_text = text.split("INPUT:")[1].strip()
            matched = _fuzzy_match_tool(tool)
            return matched or tool, input_text
        except (IndexError, ValueError):
            pass

    # 无需工具，直接返回原文
    return None, text


def run_agent(query):
    """执行 Agent：决策 → 工具调用 → 最终回答"""
    print(f"[Agent] 收到问题: {query}")

    # 1. LLM 决策
    decision = agent_node(query)
    print(f"[Agent] LLM 决策: {decision[:100]}...")

    # 2. 解析决策
    tool_name, tool_input = parse_agent_output(decision)

    if tool_name is None:
        print("[Agent] 无需工具，直接回答")
        return decision

    # 3. 查找并执行工具
    if tool_name not in TOOLS:
        print(f"[Agent] 警告: 未知工具 '{tool_name}'，直接回答")
        return decision

    print(f"[Agent] 调用工具: {tool_name}({tool_input})")
    # Bug1 修复：提前初始化 result，避免 except 后访问未定义变量
    result = ""
    try:
        tool_func = TOOLS[tool_name]["func"]
        # RAG 工具使用原始 query 而非 tool_input
        result = tool_func(query) if tool_name == "RAG" else tool_func(tool_input)
    except Exception as e:
        result = f"工具执行出错: {e}"
        print(f"[Agent] {result}")

    # 4. LLM 整合最终回答
    final_prompt = f"用户提问：{query}\n工具 {tool_name} 返回结果：{result}\n\n请根据以上信息，用自然语言回答用户的问题。"
    final = llm_node(final_prompt)
    print(f"[Agent] 最终回答生成完毕")
    return final