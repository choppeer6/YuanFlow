from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

# Bug4 修复：使用绝对路径，避免不同 cwd 下路径错误
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(_BASE_DIR, "chroma_db")
DATA_FILE = os.path.join(_BASE_DIR, "data.txt")

# Embedding 模型（始终需要，检索时也用）
embedding = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)


def _load_and_split():
    """加载文档并切分"""
    # 1️⃣ 加载文档
    loader = TextLoader(DATA_FILE, encoding="utf-8")
    documents = loader.load()

    # 2️⃣ 切分
    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = splitter.split_documents(documents)

    # 3️⃣ 清洗（关键）
    clean_docs = []
    for d in docs:
        content = d.page_content
        if not isinstance(content, str):
            content = str(content)
        content = content.strip()
        if content:
            d.page_content = content
            clean_docs.append(d)

    return clean_docs


def _init_db():
    """初始化向量数据库，已有则直接加载，否则构建"""
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print("[RAG] 检测到已有向量库，直接加载...")
        db = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embedding
        )
    else:
        print("[RAG] 未找到向量库，正在构建...")
        clean_docs = _load_and_split()
        db = Chroma.from_documents(
            clean_docs,
            embedding,
            persist_directory=PERSIST_DIR
        )
        print(f"[RAG] 向量库构建完成，共 {len(clean_docs)} 个文档块")
    return db


def rebuild_db():
    """强制重建向量库（当 data.txt 更新时调用）"""
    import shutil
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
        print("[RAG] 已清除旧向量库")
    return _init_db()


# 模块加载时初始化
db = _init_db()
