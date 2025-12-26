# SeedVR2 Video Upscaler - API Documentation

[English](API.md) | [简体中文](API_CN.md)

## Overview

SeedVR2 Video Upscaler provides a comprehensive REST API for video and image upscaling. The API supports task queue management, GPU status monitoring, and model switching.

**Base URL:** `http://localhost:8200`

**API Documentation UI:** `http://localhost:8200/docs`

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/gpu/status` | GET | GPU status and memory |
| `/api/gpu/offload` | POST | Release GPU memory |
| `/api/models` | GET | List available models |
| `/api/models/switch` | POST | Switch/load model |
| `/api/queue/status` | GET | Queue status |
| `/api/queue/position/{task_id}` | GET | Task position in queue |
| `/api/queue/history` | GET | Completed tasks history |
| `/api/process` | POST | Submit processing task |
| `/api/status/{task_id}` | GET | Get task status |
| `/api/download/{task_id}` | GET | Download result |

---

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
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

### GPU Status

```http
GET /api/gpu/status
```

**Response:**
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

### Release GPU Memory

```http
POST /api/gpu/offload
```

**Response:**
```json
{
  "status": "success",
  "message": "GPU memory released"
}
```

---

### List Models

```http
GET /api/models
```

**Response:**
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

**Available Models:**

| Model | Params | Precision | Size | VRAM |
|-------|--------|-----------|------|------|
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

### Switch Model

```http
POST /api/models/switch
Content-Type: application/json

{
  "model": "seedvr2_ema_7b_sharp_fp16.safetensors"
}
```

**Response:**
```json
{
  "status": "loaded",
  "model": "seedvr2_ema_7b_sharp_fp16.safetensors"
}
```

---

### Queue Status

```http
GET /api/queue/status
```

**Response:**
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

### Task Position

```http
GET /api/queue/position/{task_id}
```

**Response (queued):**
```json
{
  "task_id": "abc12345",
  "status": "queued",
  "position": 3,
  "estimated_wait": 75
}
```

**Response (processing):**
```json
{
  "task_id": "abc12345",
  "status": "processing",
  "position": 0,
  "estimated_wait": 0
}
```

---

### Queue History

```http
GET /api/queue/history?limit=20
```

**Response:**
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

### Submit Processing Task

```http
POST /api/process
Content-Type: multipart/form-data
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | Video or image file |
| `resolution` | int | No | 1080 | Target resolution (short edge) |
| `batch_size` | int | No | 5 | Frames per batch (4n+1: 1,5,9,13...) |
| `dit_model` | string | No | default | Model filename |
| `color_correction` | string | No | lab | lab/wavelet/hsv/none |
| `seed` | int | No | 42 | Random seed |
| `vae_tiling` | string | No | auto | auto/on/off |
| `vae_quality` | string | No | high | low/medium/high |

**Example:**
```bash
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5" \
  -F "dit_model=seedvr2_ema_7b_sharp_fp16.safetensors" \
  -F "color_correction=lab" \
  -F "seed=42"
```

**Response:**
```json
{
  "status": "queued",
  "task_id": "abc12345",
  "queue_position": 1,
  "estimated_wait_seconds": 25
}
```

---

### Task Status

```http
GET /api/status/{task_id}
```

**Response (processing):**
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

**Response (completed):**
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

### Download Result

```http
GET /api/download/{task_id}
```

Returns the processed file as a download.

---

## API Testing Guide

### Quick Test Script

```bash
#!/bin/bash
BASE_URL="http://localhost:8200"

echo "=== SeedVR2 API Test Suite ==="

# 1. Health Check
echo "1. Health Check"
curl -s $BASE_URL/health | jq .

# 2. GPU Status
echo "2. GPU Status"
curl -s $BASE_URL/api/gpu/status | jq .

# 3. List Models
echo "3. List Models"
curl -s $BASE_URL/api/models | jq '{count: (.models|length), default, current}'

# 4. Switch Model
echo "4. Switch Model"
curl -s -X POST $BASE_URL/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "seedvr2_ema_3b_fp8_e4m3fn.safetensors"}' | jq .

# 5. Queue Status
echo "5. Queue Status"
curl -s $BASE_URL/api/queue/status | jq .

# 6. Submit Task
echo "6. Submit Image Task"
RESP=$(curl -s -X POST $BASE_URL/api/process \
  -F "file=@test.png" \
  -F "resolution=480" \
  -F "batch_size=1")
echo "$RESP" | jq .
TASK_ID=$(echo "$RESP" | jq -r '.task_id')

# 7. Poll Status
echo "7. Polling Task Status..."
while true; do
  STATUS=$(curl -s $BASE_URL/api/status/$TASK_ID)
  STATE=$(echo "$STATUS" | jq -r '.status')
  echo "  Status: $STATE"
  [ "$STATE" = "completed" ] || [ "$STATE" = "failed" ] && break
  sleep 2
done
echo "$STATUS" | jq .

# 8. Download Result
echo "8. Download Result"
curl -s -I $BASE_URL/api/download/$TASK_ID | head -5

# 9. Queue History
echo "9. Queue History"
curl -s $BASE_URL/api/queue/history | jq .

# 10. Release GPU
echo "10. Release GPU Memory"
curl -s -X POST $BASE_URL/api/gpu/offload | jq .

echo "=== All Tests Completed ==="
```

### Python Test Client

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
    
    def queue_status(self):
        return requests.get(f"{self.base_url}/api/queue/status").json()
    
    def submit_task(self, file_path, resolution=1080, batch_size=5, **kwargs):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'resolution': resolution, 'batch_size': batch_size, **kwargs}
            return requests.post(f"{self.base_url}/api/process", files=files, data=data).json()
    
    def task_status(self, task_id):
        return requests.get(f"{self.base_url}/api/status/{task_id}").json()
    
    def wait_for_task(self, task_id, timeout=300, poll_interval=2):
        start = time.time()
        while time.time() - start < timeout:
            status = self.task_status(task_id)
            if status['status'] in ['completed', 'failed']:
                return status
            time.sleep(poll_interval)
        raise TimeoutError(f"Task {task_id} timed out")
    
    def download(self, task_id, output_path):
        resp = requests.get(f"{self.base_url}/api/download/{task_id}")
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        return output_path

# Usage
client = SeedVR2Client("http://localhost:8200")
print(client.health())
result = client.submit_task("input.mp4", resolution=1080)
final = client.wait_for_task(result['task_id'])
client.download(result['task_id'], "output.mp4")
```

---

## MCP (Model Context Protocol) Integration

SeedVR2 provides MCP server support for AI assistant integration (Claude, GPT, etc.).

### Starting MCP Server

```bash
# Inside container
python mcp_server.py

# Or with custom API URL
SEEDVR2_API_URL=http://localhost:8200 python mcp_server.py
```

### Available MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_queue_status()` | - | Get current queue status |
| `get_gpu_status()` | - | Get GPU status and memory |
| `list_available_models()` | - | List available DiT models |
| `submit_image_task()` | file_path, resolution, dit_model, color_correction, seed | Submit image upscaling |
| `submit_video_task()` | file_path, resolution, batch_size, dit_model, color_correction, seed | Submit video upscaling |
| `get_task_status()` | task_id | Get task status |
| `get_task_position()` | task_id | Get queue position |
| `wait_for_task()` | task_id, timeout=600, poll_interval=5 | Wait for completion |
| `get_queue_history()` | limit=20 | Get completed tasks |
| `release_gpu_memory()` | - | Release GPU memory |

### MCP Tool Details

#### submit_image_task
```python
submit_image_task(
    file_path: str,           # Path to image file
    resolution: int = 1080,   # Target resolution
    dit_model: str = None,    # Model name (optional)
    color_correction: str = "lab",  # lab/wavelet/hsv/none
    seed: int = 42            # Random seed
) -> Dict[str, Any]
```

#### submit_video_task
```python
submit_video_task(
    file_path: str,           # Path to video file
    resolution: int = 1080,   # Target resolution
    batch_size: int = 5,      # Frames per batch (4n+1)
    dit_model: str = None,    # Model name (optional)
    color_correction: str = "lab",
    seed: int = 42
) -> Dict[str, Any]
```

#### wait_for_task
```python
wait_for_task(
    task_id: str,             # Task ID from submit
    timeout: int = 600,       # Max wait seconds
    poll_interval: int = 5    # Poll frequency
) -> Dict[str, Any]           # Final task status
```

### MCP Client Implementation

#### Python MCP Client Example

```python
"""
SeedVR2 MCP Client - For integration with AI assistants
"""
import json
import subprocess
from typing import Any, Dict

class SeedVR2MCPClient:
    """MCP client for SeedVR2 Video Upscaler"""
    
    def __init__(self, mcp_server_path: str = "mcp_server.py"):
        self.server_path = mcp_server_path
    
    def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict:
        """Call MCP tool via stdio"""
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
    
    def get_gpu_status(self) -> Dict:
        return self._call_tool("get_gpu_status")
    
    def list_models(self) -> Dict:
        return self._call_tool("list_available_models")
    
    def submit_image(self, file_path: str, resolution: int = 1080, **kwargs) -> Dict:
        return self._call_tool("submit_image_task", {
            "file_path": file_path,
            "resolution": resolution,
            **kwargs
        })
    
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

# Usage Example
if __name__ == "__main__":
    client = SeedVR2MCPClient()
    
    # Check status
    print(client.get_queue_status())
    print(client.list_models())
    
    # Process video
    result = client.submit_video("/path/to/video.mp4", resolution=1080)
    task_id = result['content'][0]['text']  # Extract task_id
    
    # Wait for completion
    final = client.wait_for_task(task_id)
    print(f"Completed: {final}")
```

#### Claude Desktop MCP Configuration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seedvr2": {
      "command": "docker",
      "args": [
        "exec", "-i", "seedvr2",
        "python", "/app/mcp_server.py"
      ],
      "env": {
        "SEEDVR2_API_URL": "http://localhost:8200"
      }
    }
  }
}
```

#### Cursor IDE MCP Configuration

Add to `.cursor/mcp.json`:

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

### MCP Testing Guide

```bash
# Test MCP server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py

# Test specific tool
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_queue_status","arguments":{}}}' | python mcp_server.py

# Test with Docker
docker exec -i seedvr2 python /app/mcp_server.py << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_gpu_status","arguments":{}}}
EOF
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad request (missing parameters) |
| 404 | Resource not found (task/model) |
| 500 | Internal server error |

---

## Rate Limits

- No rate limits for API calls
- Tasks are processed serially (one at a time)
- Queue supports 100+ concurrent submissions

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8200 | Server port |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID |
| `GPU_IDLE_TIMEOUT` | 600 | Auto-unload model after N seconds |
| `SEEDVR2_API_URL` | http://localhost:8200 | MCP server API URL |
