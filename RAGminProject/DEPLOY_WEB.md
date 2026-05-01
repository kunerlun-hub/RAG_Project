# 将 Streamlit 改为 Web 应用并对外开放

## 1) 安装依赖

```bash
pip install -r requirements.txt
```

## 2) 配置环境变量

本项目使用 DashScope，请先在系统中配置 API Key：

```bash
set DASHSCOPE_API_KEY=你的key
```

PowerShell:

```powershell
$env:DASHSCOPE_API_KEY="你的key"
```

## 3) 启动 Web 服务

```bash
python web_app.py
```

或用 uvicorn：

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

本机访问：`http://127.0.0.1:8000`

## 4) 给局域网用户使用

同一网络其他设备访问：

`http://你的局域网IP:8000`

注意防火墙放行 8000 端口。

## 5) 给公网用户使用（推荐）

可以把本地 8000 端口映射成公网地址：

- Cloudflare Tunnel (`cloudflared`)
- ngrok
- 部署到云服务器并配置 Nginx 反向代理 + HTTPS

### Cloudflare Tunnel 示例

```bash
cloudflared tunnel --url http://localhost:8000
```

运行后会得到一个 `https://xxxx.trycloudflare.com` 的公网地址，直接分享给其他人即可。
