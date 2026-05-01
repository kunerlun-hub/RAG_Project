from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

from file_history_store import get_history
from vector_store import  VectorStoreService
import config_data as config


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return  prompt
class Rag:
    def __init__(self):
        self.vector_service = VectorStoreService(
            DashScopeEmbeddings(model = config.text_model))
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system","以我提供的已知参考资料为主,"
            "简洁和专业的回答用户问题,参考资料:{context}"),
             ("system","并且我提供用户的历史对话记录:"),
             MessagesPlaceholder("history"),
            ("user","请回答用户提问:{input}")]
        )
        self.chat_model = ChatTongyi(model = config.chat_model)
        self.chain = self.__get_chain()

    def __get_chain(self):
        def format_document(docs: list[Document]):
            if not docs:
                return "无参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段:{doc.page_content}\n文档元数据:{doc.metadata}\n"
            return formatted_str
        retriever = self.vector_service.get_retriver()
        def format_for_retriever(value: dict)-> str:
            return value["input"]
        def format_for_prompt_template(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value
        chain = ({"input": RunnablePassthrough(),
                  "context": RunnableLambda(format_for_retriever)|retriever|format_document} |RunnableLambda(format_for_prompt_template)|
                 self.prompt_template |print_prompt| self.chat_model |StrOutputParser())
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        return conversation_chain
if __name__ == '__main__':
    rag = Rag()
    res = rag.chain.invoke({"input":"我的体重是150斤,尺码推荐"},config.session_config)
    print(res)