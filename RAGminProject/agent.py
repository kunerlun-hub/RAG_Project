from typing import Iterator

from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

from file_history_store import get_history
from vector_store import VectorStoreService
import config_data as config


@tool
def calculator(expression: str) -> str:
    """计算数学表达式。支持 +, -, *, /, //, %, ** 运算。
    示例输入: "2 + 3 * 4"
    """
    try:
        allowed_chars = set("0123456789+-*/().%^ eE")
        if not all(c in allowed_chars for c in expression.replace("**", "^")):
            return "表达式包含不允许的字符"
        safe_expr = expression.replace("^", "**")
        result = eval(safe_expr, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"计算出错: {e}"


class ProblemSolvingAgent:
    """智能体：能主动检索知识库并使用工具来解决问题的对话助手"""

    def __init__(self):
        self.vector_service = VectorStoreService(
            DashScopeEmbeddings(model=config.text_model))
        self.tools = [self._create_retrieve_tool(), calculator]
        self.chat_model = ChatTongyi(model=config.chat_model)
        self.agent = create_agent(
            model=self.chat_model,
            tools=self.tools,
            system_prompt=(
                "你是一个智能问题解决助手。你可以使用以下工具:\n"
                "- retrieve_knowledge: 从知识库中检索相关文档资料\n"
                "- calculator: 执行数学计算\n"
                "使用规则:\n"
                "1. 当用户问题需要参考资料时，先使用 retrieve_knowledge 检索\n"
                "2. 当涉及数学计算时，使用 calculator 工具\n"
                "3. 基于检索结果或计算结果，给出简洁专业的回答\n"
                "4. 如果问题可以直接回答，无需使用工具"
            ),
        )

    def _create_retrieve_tool(self):
        retriever = self.vector_service.get_retriever()

        @tool
        def retrieve_knowledge(query: str) -> str:
            """从知识库中检索与查询相关的文档信息。当用户问题需要参考资料或背景知识时使用。
            query: 搜索关键词或问题
            """
            docs = retriever.invoke(query)
            if not docs:
                return "未找到相关参考资料"
            parts = []
            for i, doc in enumerate(docs, 1):
                src = doc.metadata.get("source", "未知")
                parts.append(f"[资料{i}] 来源:{src}\n{doc.page_content}")
            return "\n\n".join(parts)

        return retrieve_knowledge

    def chat(self, message: str, session_id: str) -> str:
        history = get_history(session_id)
        messages = list(history.messages)
        messages.append(HumanMessage(content=message))

        result = self.agent.invoke({"messages": messages})
        output = self._extract_response(result["messages"][len(messages):])
        history.add_messages([HumanMessage(content=message), AIMessage(content=output)])
        return output

    def chat_stream(self, message: str, session_id: str) -> Iterator[dict]:
        history = get_history(session_id)
        messages = list(history.messages)
        messages.append(HumanMessage(content=message))

        full_output = ""
        for chunk in self.agent.stream({"messages": messages}):
            for node, data in chunk.items():
                if not isinstance(data, dict) or "messages" not in data:
                    continue
                for m in data["messages"]:
                    if isinstance(m, AIMessage):
                        if m.tool_calls:
                            for tc in m.tool_calls:
                                yield {"type": "status",
                                       "content": f"正在使用工具: {tc.get('name', 'unknown')}..."}
                        elif m.content and isinstance(m.content, str) and m.content.strip():
                            full_output = m.content
                            yield {"type": "token", "content": m.content}

        if full_output:
            history.add_messages([HumanMessage(content=message), AIMessage(content=full_output)])

    def _extract_response(self, new_messages: list) -> str:
        for m in reversed(new_messages):
            if isinstance(m, AIMessage) and m.content:
                return m.content
        return "抱歉，我无法处理这个问题。"
