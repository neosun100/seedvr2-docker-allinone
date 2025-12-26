# SeedVR2 视频超分 - API 文档

[English](API.md) | [简体中文](API_CN.md)

## 概述

SeedVR2 视频超分提供完整的 REST API，支持视频和图片超分辨率处理。API 支持任务队列管理、GPU 状态监控和模型切换。

**基础 URL:** `http://localhost:8200`

**API 文档界面:** `http://localhost:8200/docs`

---

## 快速参考

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/gpu/status` | GET | GPU 状态和显存 |
| `/api/gpu/offload` | POST | 释放 GPU 显存 |
| `/api/models` | GET | 列出可用模型 |
| `/api/models/switch` | POST | 切换/加载模型 |
| `/api/queue/status` | GET | 队列状态 |
| `/api/queue/position/{task_id}` | GET | 任务队列位置 |
| `/api/queue/history` | GET | 已完成任务历史 |
| `/api/process` | POST | 提交处理任务 |
| `/api/status/{task_id}` | GET | 获取任务状态 |
| `/api/download/{task_id}` | GET | 下载结果 |

---

## 端点详情

### 健康检查

```http
GET /health
```

**响应:**
```json
{
  "status": "healthy",
  "version": "1.4.2",
  "queue_enabled": true,
  "queue_length": 0,
  "timestamp": "2025-12-26T16:00:00.000000"
}
```

---

### GPU 状态

```http
GET /api/gpu/status
```

**响应:**
```json
{
  "cuda_available": true,
  "gpu_name": "NVIDIA L40S",
  "vram_used_mb": 3418,
  "vram_total_mb": 45709,
  "model_loaded": true,
  "current_model": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
  "loading": false,
  "loading_model": null,
  "processing": false,
  "current_task": null
}
```

---

### 释放 GPU 显存

```http
POST /api/gpu/offload
```

**响应:**
```json
{
  "status": "success",
  "message": "GPU memory released"
}
```

---

### 列出模型

```http
GET /api/models
```

**响应:**
```json
{
  "models": [
    {
      "name": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
      "params": "3B",
      "precision": "FP8",
      "size": "3.2GB",
      "vram": "~8GB",
      "variant": "",
      "desc": {
        "en": "3B params FP8 - Balanced quality & speed ⭐Recommended",
        "zh-CN": "3B参数 FP8 - 质量与速度平衡 ⭐推荐"
      }
    }
  ],
  "default": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
  "current": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
  "loading": false,
  "loading_model": null
}
```

**可用模型:**

| 模型 | 参数量 | 精度 | 大小 | 显存需求 |
|------|--------|------|------|----------|
| `seedvr2_ema_3b_fp16.safetensors` | 3B | FP16 | 6.4GB | ~12GB |
| `seedvr2_ema_3b_fp8_e4m3fn.safetensors` | 3B | FP8 | 3.2GB | ~8GB |
| `seedvr2_ema_3b-Q4_K_M.gguf` | 3B | Q4 | 1.9GB | ~4GB |
| `seedvr2_ema_3b-Q8_0.gguf` | 3B | Q8 | 3.5GB | ~6GB |
| `seedvr2_ema_7b_fp16.safetensors` | 7B | FP16 | 16GB | ~24GB |
| `seedvr2_ema_7b_fp8_e4m3fn.safetensors` | 7B | FP8 | 7.7GB | ~16GB |
| `seedvr2_ema_7b-Q4_K_M.gguf` | 7B | Q4 | 4.5GB | ~8GB |
| `seedvr2_ema_7b-Q8_0.gguf` | 7B | Q8 | 8.3GB | ~12GB |
| `seedvr2_ema_7b_sharp_fp16.safetensors` | 7B Sharp | FP16 | 16GB | ~24GB |
| `seedvr2_ema_7b_sharp_fp8_e4m3fn.safetensors` | 7B Sharp | FP8 | 7.7GB | ~16GB |
| `seedvr2_ema_7b_sharp-Q4_K_M.gguf` | 7B Sharp | Q4 | 4.5GB | ~8GB |
| `seedvr2_ema_7b_sharp-Q8_0.gguf` | 7B Sharp | Q8 | 8.3GB | ~12GB |

---

### 切换模型

```http
POST /api/models/switch
Content-Type: application/json

{
  "model": "seedvr2_ema_7b_sharp_fp16.safetensors"
}
```

**响应:**
```json
{
  "status": "loaded",
  "model": "seedvr2_ema_7b_sharp_fp16.safetensors"
}
```

---

### 队列状态

```http
GET /api/queue/status
```

**响应:**
```json
{
  "queue_length": 2,
  "processing": {
    "task_id": "abc12345",
    "progress": 50,
    "model": "3b_fp8"
  },
  "processing_progress": 50,
  "pending_tasks": [
    {"task_id": "def67890", "position": 2}
  ],
  "total_completed": 10,
  "total_failed": 0,
  "avg_process_time": 25,
  "estimated_total_wait": 50
}
```

---

### 任务位置

```http
GET /api/queue/position/{task_id}
```

**响应 (排队中):**
```json
{
  "task_id": "abc12345",
  "status": "queued",
  "position": 3,
  "estimated_wait": 75
}
```

**响应 (处理中):**
```json
{
  "task_id": "abc12345",
  "status": "processing",
  "position": 0,
  "estimated_wait": 0
}
```

---

### 队列历史

```http
GET /api/queue/history?limit=20
```

**响应:**
```json
{
  "history": [
    {
      "id": "abc12345",
      "status": "completed",
      "created_at": "2025-12-26T16:00:00",
      "completed_at": "2025-12-26T16:00:25",
      "process_time": 25,
      "output_filename": "video_3b_fp8_1080p_b5_clab_s42_25s.mp4",
      "output_resolution": "1920x1080"
    }
  ]
}
```

---

### 提交处理任务

```http
POST /api/process
Content-Type: multipart/form-data
```

**参数:**

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `file` | File | 是 | - | 视频或图片文件 |
| `resolution` | int | 否 | 1080 | 目标分辨率（短边） |
| `batch_size` | int | 否 | 5 | 每批帧数 (4n+1: 1,5,9,13...) |
| `dit_model` | string | 否 | default | 模型文件名 |
| `color_correction` | string | 否 | lab | lab/wavelet/hsv/none |
| `seed` | int | 否 | 42 | 随机种子 |
| `vae_tiling` | string | 否 | auto | auto/on/off |
| `vae_quality` | string | 否 | high | low/medium/high |

**示例:**
```bash
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5" \
  -F "dit_model=seedvr2_ema_7b_sharp_fp16.safetensors" \
  -F "color_correction=lab" \
  -F "seed=42"
```

**响应:**
```json
{
  "status": "queued",
  "task_id": "abc12345",
  "queue_position": 1,
  "estimated_wait_seconds": 25
}
```

---

### 任务状态

```http
GET /api/status/{task_id}
```

**响应 (处理中):**
```json
{
  "id": "abc12345",
  "status": "processing",
  "progress": 50,
  "queue_position": 1,
  "created_at": "2025-12-26T16:00:00",
  "started_at": "2025-12-26T16:00:01",
  "params": {
    "resolution": 1080,
    "batch_size": 5,
    "dit_model": "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
    "color_correction": "lab",
    "seed": 42
  }
}
```

**响应 (已完成):**
```json
{
  "id": "abc12345",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-12-26T16:00:00",
  "started_at": "2025-12-26T16:00:01",
  "completed_at": "2025-12-26T16:00:26",
  "process_time": 25,
  "output_path": "/app/outputs/video_3b_fp8_1080p_b5_clab_s42_25s.mp4",
  "output_filename": "video_3b_fp8_1080p_b5_clab_s42_25s.mp4",
  "output_resolution": "1920x1080"
}
```

---

### 下载结果

```http
GET /api/download/{task_id}
```

返回处理后的文件下载。

---

## API 测试指南

### 快速测试脚本

```bash
#!/bin/bash
BASE_URL="http://localhost:8200"

echo "=== SeedVR2 API 测试套件 ==="

# 1. 健康检查
echo "1. 健康检查"
curl -s $BASE_URL/health | jq .

# 2. GPU 状态
echo "2. GPU 状态"
curl -s $BASE_URL/api/gpu/status | jq .

# 3. 列出模型
echo "3. 列出模型"
curl -s $BASE_URL/api/models | jq '{count: (.models|length), default, current}'

# 4. 切换模型
echo "4. 切换模型"
curl -s -X POST $BASE_URL/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "seedvr2_ema_3b_fp8_e4m3fn.safetensors"}' | jq .

# 5. 队列状态
echo "5. 队列状态"
curl -s $BASE_URL/api/queue/status | jq .

# 6. 提交任务
echo "6. 提交图片任务"
RESP=$(curl -s -X POST $BASE_URL/api/process \
  -F "file=@test.png" \
  -F "resolution=480" \
  -F "batch_size=1")
echo "$RESP" | jq .
TASK_ID=$(echo "$RESP" | jq -r '.task_id')

# 7. 轮询状态
echo "7. 轮询任务状态..."
while true; do
  STATUS=$(curl -s $BASE_URL/api/status/$TASK_ID)
  STATE=$(echo "$STATUS" | jq -r '.status')
  echo "  状态: $STATE"
  [ "$STATE" = "completed" ] || [ "$STATE" = "failed" ] && break
  sleep 2
done
echo "$STATUS" | jq .

# 8. 下载结果
echo "8. 下载结果"
curl -s -I $BASE_URL/api/download/$TASK_ID | head -5

echo "=== 所有测试完成 ==="
```

### Python 测试客户端

```python
import requests
import time

class SeedVR2Client:
    def __init__(self, base_url="http://localhost:8200"):
        self.base_url = base_url
    
    def health(self):
        return requests.get(f"{self.base_url}/health").json()
    
    def gpu_status(self):
        return requests.get(f"{self.base_url}/api/gpu/status").json()
    
    def list_models(self):
        return requests.get(f"{self.base_url}/api/models").json()
    
    def switch_model(self, model_name):
        return requests.post(
            f"{self.base_url}/api/models/switch",
            json={"model": model_name}
        ).json()
    
    def submit_task(self, file_path, resolution=1080, batch_size=5, **kwargs):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'resolution': resolution, 'batch_size': batch_size, **kwargs}
            return requests.post(f"{self.base_url}/api/process", files=files, data=data).json()
    
    def wait_for_task(self, task_id, timeout=300, poll_interval=2):
        start = time.time()
        while time.time() - start < timeout:
            status = requests.get(f"{self.base_url}/api/status/{task_id}").json()
            if status['status'] in ['completed', 'failed']:
                return status
            time.sleep(poll_interval)
        raise TimeoutError(f"任务 {task_id} 超时")

# 使用示例
client = SeedVR2Client("http://localhost:8200")
print(client.health())
result = client.submit_task("input.mp4", resolution=1080)
final = client.wait_for_task(result['task_id'])
```

---

## MCP (模型上下文协议) 集成

SeedVR2 提供 MCP 服务器支持，用于 AI 助手集成（Claude、GPT 等）。

### 启动 MCP 服务器

```bash
# 在容器内
python mcp_server.py

# 或使用自定义 API URL
SEEDVR2_API_URL=http://localhost:8200 python mcp_server.py
```

### 可用 MCP 工具

| 工具 | 参数 | 描述 |
|------|------|------|
| `get_queue_status()` | - | 获取当前队列状态 |
| `get_gpu_status()` | - | 获取 GPU 状态和显存 |
| `list_available_models()` | - | 列出可用 DiT 模型 |
| `submit_image_task()` | file_path, resolution, dit_model, color_correction, seed | 提交图片超分 |
| `submit_video_task()` | file_path, resolution, batch_size, dit_model, color_correction, seed | 提交视频超分 |
| `get_task_status()` | task_id | 获取任务状态 |
| `get_task_position()` | task_id | 获取队列位置 |
| `wait_for_task()` | task_id, timeout=600, poll_interval=5 | 等待任务完成 |
| `get_queue_history()` | limit=20 | 获取已完成任务 |
| `release_gpu_memory()` | - | 释放 GPU 显存 |

### MCP 工具详情

#### submit_image_task
```python
submit_image_task(
    file_path: str,           # 图片文件路径
    resolution: int = 1080,   # 目标分辨率
    dit_model: str = None,    # 模型名称（可选）
    color_correction: str = "lab",  # lab/wavelet/hsv/none
    seed: int = 42            # 随机种子
) -> Dict[str, Any]
```

#### submit_video_task
```python
submit_video_task(
    file_path: str,           # 视频文件路径
    resolution: int = 1080,   # 目标分辨率
    batch_size: int = 5,      # 每批帧数 (4n+1)
    dit_model: str = None,    # 模型名称（可选）
    color_correction: str = "lab",
    seed: int = 42
) -> Dict[str, Any]
```

#### wait_for_task
```python
wait_for_task(
    task_id: str,             # 提交返回的任务 ID
    timeout: int = 600,       # 最大等待秒数
    poll_interval: int = 5    # 轮询频率
) -> Dict[str, Any]           # 最终任务状态
```

### MCP 客户端实现

#### Python MCP 客户端示例

```python
"""
SeedVR2 MCP 客户端 - 用于 AI 助手集成
"""
import json
import subprocess
from typing import Any, Dict

class SeedVR2MCPClient:
    """SeedVR2 视频超分 MCP 客户端"""
    
    def __init__(self, mcp_server_path: str = "mcp_server.py"):
        self.server_path = mcp_server_path
    
    def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict:
        """通过 stdio 调用 MCP 工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        proc = subprocess.Popen(
            ["python", self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, _ = proc.communicate(json.dumps(request).encode())
        return json.loads(stdout)
    
    def get_queue_status(self) -> Dict:
        return self._call_tool("get_queue_status")
    
    def submit_video(self, file_path: str, resolution: int = 1080, 
                     batch_size: int = 5, **kwargs) -> Dict:
        return self._call_tool("submit_video_task", {
            "file_path": file_path,
            "resolution": resolution,
            "batch_size": batch_size,
            **kwargs
        })
    
    def wait_for_task(self, task_id: str, timeout: int = 600) -> Dict:
        return self._call_tool("wait_for_task", {
            "task_id": task_id,
            "timeout": timeout
        })

# 使用示例
client = SeedVR2MCPClient()
result = client.submit_video("/path/to/video.mp4", resolution=1080)
final = client.wait_for_task(result['task_id'])
```

#### Claude Desktop MCP 配置

添加到 `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seedvr2": {
      "command": "docker",
      "args": ["exec", "-i", "seedvr2", "python", "/app/mcp_server.py"],
      "env": {
        "SEEDVR2_API_URL": "http://localhost:8200"
      }
    }
  }
}
```

#### Cursor IDE MCP 配置

添加到 `.cursor/mcp.json`:

```json
{
  "servers": {
    "seedvr2": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "SEEDVR2_API_URL": "http://localhost:8200"
      }
    }
  }
}
```

### MCP 测试指南

```bash
# 直接测试 MCP 服务器
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py

# 测试特定工具
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_queue_status","arguments":{}}}' | python mcp_server.py

# 通过 Docker 测试
docker exec -i seedvr2 python /app/mcp_server.py << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_gpu_status","arguments":{}}}
EOF
```

---

## 错误码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求错误（缺少参数） |
| 404 | 资源未找到（任务/模型） |
| 500 | 服务器内部错误 |

---

## 速率限制

- API 调用无速率限制
- 任务串行处理（一次一个）
- 队列支持 100+ 并发提交

---

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `PORT` | 8200 | 服务器端口 |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU 设备 ID |
| `GPU_IDLE_TIMEOUT` | 600 | 空闲 N 秒后自动卸载模型 |
| `SEEDVR2_API_URL` | http://localhost:8200 | MCP 服务器 API URL |
