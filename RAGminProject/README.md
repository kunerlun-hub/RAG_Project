# RAGminProject

基于 **LangChain**、**阿里云 DashScope（通义）** 与 **Chroma** 的简易 RAG（检索增强生成）示例：支持本地向量库、会话历史与 Web / Streamlit 两种交互方式。

## 功能概览

| 入口 | 说明 |
|------|------|
| `web_app.py` | FastAPI 服务，内置聊天页，支持 **SSE 流式**输出 |
| `app_qa.py` | Streamlit 对话界面 |
| `app_file_uploader.py` | Streamlit 上传 TXT，写入向量库（MD5 去重） |
| `knowledge_base.py` | 知识入库逻辑（可被脚本或其它入口调用） |

知识检索由 `rag.py` 中的 `Rag` 类串联：向量检索 → 带上下文的提示词 → 对话模型。

## 环境要求

- Python 3.10+（与类型注解 `str | None` 等一致）
- 有效的 [DashScope API Key](https://help.aliyun.com/zh/dashscope/)

## 快速开始

### 1. 安装依赖

```bash
cd RAGminProject
pip install -r requirements.txt
```

### 2. 配置 API Key

**Windows CMD**

```bat
set DASHSCOPE_API_KEY=你的密钥
```

**PowerShell**

```powershell
$env:DASHSCOPE_API_KEY="你的密钥"
```

**Linux / macOS**

```bash
export DASHSCOPE_API_KEY="你的密钥"
```

也可使用 `.env` 配合你的启动方式自行加载（仓库默认通过 `.gitignore` 忽略 `.env`）。

### 3. 准备知识库（可选）

- 将 TXT 放入 `Data/`，或通过 `app_file_uploader.py` 上传。
- 首次运行会在本地生成 `chroma_db/`（向量持久化，已被 `.gitignore` 忽略）。

### 4. 启动服务

**Web（推荐）**

```bash
python web_app.py
```

浏览器访问：<http://127.0.0.1:8000>  
健康检查：<http://127.0.0.1:8000/health>

或使用 uvicorn：

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

**Streamlit 问答**

```bash
streamlit run app_qa.py
```

**Streamlit 文件上传**

```bash
streamlit run app_file_uploader.py
```

## 配置说明

主要参数在 `config_data.py`：

- `text_model` / `chat_model`：嵌入与对话模型名称（DashScope）
- `similarity_top_k`：检索返回的文档块数量
- `chunk_size` / `chunk_overlap` / `separators`：文本切分策略
- `persist_directory` / `collection_name`：Chroma 存储路径与集合名

会话历史默认写入 `chat_history/`（已忽略版本控制）。调试完整提示词时可设置环境变量 `RAG_DEBUG_PROMPTS=1`。

## 项目结构（核心文件）

```text
RAGminProject/
├── README.md
├── requirements.txt
├── config_data.py          # 全局配置
├── rag.py                  # RAG 链与对话封装
├── vector_store.py         # Chroma 检索封装
├── knowledge_base.py       # 入库与 MD5 去重
├── file_history_store.py   # 基于文件的会话历史
├── web_app.py              # FastAPI + 前端聊天页
├── app_qa.py               # Streamlit 问答
├── app_file_uploader.py    # Streamlit 上传
├── Data/                   # 示例知识文本
└── DEPLOY_WEB.md           # 局域网 / 公网暴露端口说明
```

## 对外访问与部署

局域网、内网穿透、云服务器等说明见 [DEPLOY_WEB.md](./DEPLOY_WEB.md)。

## 许可证


