import time
from collections import defaultdict, deque


class Executor:
    def __init__(self, flow):
        self.flow = flow

    def run(self, input_data):
        """基于拓扑排序执行 DAG 工作流"""
        start_time = time.time()
        print(f"\n{'='*50}")
        print(f"[Executor] 开始执行工作流")
        print(f"[Executor] 节点: {list(self.flow.nodes.keys())}")
        print(f"[Executor] 边: {[(e.source, e.target) for e in self.flow.edges]}")
        print(f"{'='*50}")

        indegree = defaultdict(int)
        graph = defaultdict(list)

        # 入度统计
        for edge in self.flow.edges:
            graph[edge.source].append(edge.target)
            indegree[edge.target] += 1

        # 找起点（入度为 0 的节点）
        queue = deque()
        data_map = {}

        for node_id in self.flow.nodes:
            if indegree[node_id] == 0:
                queue.append(node_id)
                data_map[node_id] = input_data

        if not queue:
            raise RuntimeError("[Executor] 错误: 未找到起始节点，可能存在环路")

        # BFS 拓扑排序执行
        output = None
        step = 0

        while queue:
            current = queue.popleft()
            node = self.flow.nodes[current]
            step += 1

            print(f"\n[Step {step}] 执行节点: {current}")
            node_start = time.time()

            try:
                output = node.run(data_map[current])
            except Exception as e:
                print(f"[Step {step}] ❌ 节点 '{current}' 执行失败: {e}")
                raise RuntimeError(f"节点 '{current}' 执行失败: {e}") from e

            elapsed = time.time() - node_start
            print(f"[Step {step}] ✅ 节点 '{current}' 完成 ({elapsed:.2f}s)")

            for neighbor in graph[current]:
                data_map[neighbor] = output
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        total_time = time.time() - start_time
        print(f"\n{'='*50}")
        print(f"[Executor] 工作流执行完毕，共 {step} 步，耗时 {total_time:.2f}s")
        print(f"{'='*50}\n")

        if step == 0:
            raise RuntimeError("[Executor] 错误: 没有任何节点被执行，请检查 Flow 是否为空")

        return output