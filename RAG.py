import rag_init


def _get_retriever():
    """Bug5 修复：懒加载 retriever，每次从最新的 rag_init.db 获取
    避免 rebuild_db() 后 retriever 仍绑定旧的 db 实例"""
    return rag_init.db.as_retriever(search_kwargs={"k": 3})


def rag_node(query):
    retriever = _get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        return f"""
    你是一个问答助手，知识库中未找到相关内容，请根据已有知识回答：

    问题：{query}
    """

    context = "\n".join([doc.page_content for doc in docs])

    return f"""
    你是一个问答助手，请基于以下内容回答问题：

    {context}

    问题：{query}
    """
