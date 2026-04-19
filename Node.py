class Node:
    def __init__(self, node_id,func):
        self.id = node_id
        self.func = func

    def run(self,input):
        return self.func(input)



# def prompt_node(x):
#     return f"帮我总结:{x}"
#
# n = Node("prompt",prompt_node)
# print(n.run("今天天气很好"))
# print(n.id)