import json
import uuid
from typing import Iterator

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

import config_data as config
from rag import Rag


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


app = FastAPI(title="RAG Web App")
rag = Rag()


HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>智能答题</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f6f7fb; margin: 0; }
    .container { max-width: 920px; margin: 24px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 14px rgba(0,0,0,0.08); overflow: hidden; }
    .header { padding: 16px 20px; border-bottom: 1px solid #ececec; font-size: 20px; font-weight: 700; }
    .chat { height: 62vh; overflow-y: auto; padding: 18px 20px; display: flex; flex-direction: column; gap: 12px; }
    .msg { max-width: 80%; padding: 10px 12px; border-radius: 10px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
    .user { align-self: flex-end; background: #2f66f3; color: #fff; }
    .assistant { align-self: flex-start; background: #f1f3f6; color: #111; }
    .footer { padding: 12px; border-top: 1px solid #ececec; display: flex; gap: 10px; }
    .footer input { flex: 1; border: 1px solid #ddd; border-radius: 8px; padding: 10px 12px; font-size: 14px; }
    .footer button { border: 0; background: #2f66f3; color: #fff; border-radius: 8px; padding: 0 18px; font-size: 14px; cursor: pointer; }
    .footer button:disabled { opacity: 0.5; cursor: not-allowed; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">智能答题</div>
    <div class="chat" id="chat"></div>
    <div class="footer">
      <input id="input" placeholder="请输入你的问题..." />
      <button id="send">发送</button>
    </div>
  </div>

  <script>
    const chat = document.getElementById("chat");
    const input = document.getElementById("input");
    const send = document.getElementById("send");

    let sessionId = localStorage.getItem("rag_session_id");
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem("rag_session_id", sessionId);
    }

    function appendMessage(role, content) {
      const div = document.createElement("div");
      div.className = `msg ${role}`;
      div.textContent = content;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
      return div;
    }

    appendMessage("assistant", "你好, 有什么可以帮助你的?");

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      input.value = "";
      send.disabled = true;

      appendMessage("user", text);
      const aiBox = appendMessage("assistant", "AI思考中...");

      try {
        const resp = await fetch("/api/chat/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, session_id: sessionId })
        });

        if (!resp.ok || !resp.body) {
          aiBox.textContent = "请求失败，请稍后重试。";
          return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let answer = "";

        aiBox.textContent = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const chunks = buffer.split("\\n\\n");
          buffer = chunks.pop() || "";

          for (const chunk of chunks) {
            if (!chunk.startsWith("data:")) continue;
            const payload = chunk.slice(5).trim();
            if (!payload) continue;
            if (payload === "[DONE]") continue;
            try {
              const data = JSON.parse(payload);
              if (data.type === "token") {
                answer += data.content;
                aiBox.textContent = answer;
                chat.scrollTop = chat.scrollHeight;
              } else if (data.type === "error") {
                aiBox.textContent = data.content;
              }
            } catch (e) {
              aiBox.textContent = "响应解析失败。";
            }
          }
        }
      } catch (e) {
        aiBox.textContent = "网络异常，请检查服务状态。";
      } finally {
        send.disabled = false;
        input.focus();
      }
    }

    send.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return HTML_PAGE


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat/stream")
def chat_stream(payload: ChatRequest, session_id: str | None = Query(default=None)) -> StreamingResponse:
    user_message = payload.message.strip()
    if not user_message:
        return StreamingResponse(iter(["data: " + json.dumps({"type": "error", "content": "消息不能为空"}) + "\n\n"]),
                                 media_type="text/event-stream")

    current_session_id = payload.session_id or session_id or str(uuid.uuid4())

    session_config = {
        "configurable": {
            "session_id": current_session_id
        }
    }

    def event_stream() -> Iterator[str]:
        try:
            for chunk in rag.chain.stream({"input": user_message}, session_config):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            error_msg = f"服务异常: {exc}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
