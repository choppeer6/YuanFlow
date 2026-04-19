from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    model="moonshot-v1-8k",
    model_provider="openai",
    base_url="https://api.moonshot.cn/v1",
    api_key=os.getenv("MOONSHOT_API_KEY")
)
def llm_node(x):
    return model.invoke(x).content