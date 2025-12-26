[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 Video Upscaler - Docker All-in-One

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.2-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 One-Click Deploy AI Video/Image Upscaler with Web UI**

*Based on [ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | Enhanced Docker All-in-One Edition*

[Quick Start](#-quick-start) • [Features](#-features) • [API Docs](#-api-documentation) • [Docker Images](#-docker-images)

<img src="https://img.aws.xin/uPic/IaHGPU.png" alt="Web UI Screenshot">

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **12 AI Models** | 3B/7B/7B-Sharp × FP16/FP8/GGUF variants |
| **3 Interfaces** | Web UI + REST API + MCP (Model Context Protocol) |
| **Resolution** | 480p → 16K (custom supported) |
| **VAE Tiling** | Smart auto-enable for high-res processing |
| **H.264 Encoding** | Browser-compatible video + audio preservation |
| **Bilingual UI** | Chinese/English/Traditional Chinese/Japanese |
| **Privacy Safe** | No user files stored in image |

---

## 🚀 Quick Start

### Recommended: With Volume Mounts (Privacy Safe)

```bash
# Create directories on host
mkdir -p /tmp/seedvr2-docker-allinone/uploads /tmp/seedvr2-docker-allinone/outputs

# Run with volume mounts - files stored on host, not in container
docker run -d --gpus all -p 8200:8200 \
  -v /tmp/seedvr2-docker-allinone/uploads:/app/uploads \
  -v /tmp/seedvr2-docker-allinone/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

### Simple Start (Files stored in container)

```bash
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest
```

### Lightweight Version

```bash
docker run -d --gpus all -p 8200:8200 \
  -v /tmp/seedvr2-docker-allinone/uploads:/app/uploads \
  -v /tmp/seedvr2-docker-allinone/outputs:/app/outputs \
  neosun/seedvr2-allinone:v1.3.2-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

Then open:
- **Web UI**: http://localhost:8200
- **API Docs (Swagger)**: http://localhost:8200/apidocs
- **Health Check**: http://localhost:8200/health

---

## 🔒 Privacy & Storage Options

### Option 1: Host Volume Mount (Recommended)

Files are stored on the host machine, giving you full control:

```bash
docker run -d --gpus all -p 8200:8200 \
  -v /path/to/uploads:/app/uploads \
  -v /path/to/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

- ✅ Files persist on host
- ✅ Easy to manage and clean up
- ✅ No data in container

### Option 2: tmpfs (Memory Storage)

Files are stored in RAM and cleared on container restart:

```bash
docker run -d --gpus all -p 8200:8200 \
  --tmpfs /app/uploads:size=10G \
  --tmpfs /app/outputs:size=50G \
  neosun/seedvr2-allinone:latest
```

- ✅ Maximum privacy - data cleared on restart
- ✅ Fast I/O performance
- ⚠️ Requires sufficient RAM
- ⚠️ Data lost on container stop

---

## 🐳 Docker Images

| Image Tag | Models | Size | Use Case |
|-----------|--------|------|----------|
| `latest` / `v1.3.2-12models-*` | All 12 | ~103GB | Full features |
| `v1.3.2-3b-fast-4models-*` | 4× 3B | ~26GB | Fast processing |
| `v1.3.2-7b-quality-4models-*` | 4× 7B | ~49GB | High quality |
| `v1.3.2-7b-sharp-4models-*` | 4× 7B Sharp | ~49GB | Detail enhancement |
| `v1.3.2-7b-sharp-fp16-only-*` | 1× 7B Sharp FP16 | ~27GB | Minimal size |

---

## 📚 API Documentation

### Interactive API Docs

Access Swagger UI at: **http://localhost:8200/apidocs**

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/gpu/status` | GET | GPU status (VRAM, model loaded) |
| `/api/gpu/offload` | POST | Release GPU memory |
| `/api/models` | GET | List available models |
| `/api/models/switch` | POST | Load model to GPU |
| `/api/process` | POST | Start processing task |
| `/api/status/{task_id}` | GET | Get task progress |
| `/api/download/{task_id}` | GET | Download result |

### API Usage Examples

#### 1. Check GPU Status
```bash
curl http://localhost:8200/api/gpu/status
```
Response:
```json
{
  "cuda_available": true,
  "gpu_name": "NVIDIA GeForce RTX 4090",
  "vram_used_mb": 2048,
  "vram_total_mb": 24564,
  "model_loaded": true,
  "current_model": "seedvr2_ema_7b_sharp_fp16.safetensors"
}
```

#### 2. List Available Models
```bash
curl http://localhost:8200/api/models
```

#### 3. Load a Model
```bash
curl -X POST http://localhost:8200/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "seedvr2_ema_7b_sharp_fp16.safetensors"}'
```

#### 4. Process Image/Video
```bash
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5" \
  -F "dit_model=seedvr2_ema_7b_sharp_fp16.safetensors" \
  -F "color_correction=lab" \
  -F "seed=42" \
  -F "vae_tiling=auto" \
  -F "vae_quality=high"
```
Response:
```json
{"task_id": "abc12345", "status": "queued"}
```

#### 5. Check Task Status
```bash
curl http://localhost:8200/api/status/abc12345
```
Response:
```json
{
  "id": "abc12345",
  "status": "completed",
  "progress": 100,
  "output_path": "/app/outputs/result.mp4",
  "output_resolution": "1920x1080",
  "process_time": 45
}
```

#### 6. Download Result
```bash
curl -O http://localhost:8200/api/download/abc12345
```

### Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | File | Required | Input image/video |
| `resolution` | int | 1080 | Target short-edge resolution (480-16000) |
| `batch_size` | int | 5 | Frames per batch (1,5,9,13,17,21,25) |
| `dit_model` | string | auto | Model filename |
| `color_correction` | string | lab | lab/wavelet/hsv/adain/none |
| `seed` | int | 42 | Random seed |
| `vae_tiling` | string | auto | auto/on/off |
| `vae_quality` | string | high | low/medium/high |

---

## 🔧 MCP Interface

For programmatic access via Model Context Protocol:

```bash
python mcp_server.py
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `upscale_image` | Upscale a single image |
| `upscale_video` | Upscale a video file |
| `get_gpu_status` | Get GPU status |
| `release_gpu_memory` | Release GPU memory |
| `list_available_models` | List available models |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8200 | Server port |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID |
| `GPU_IDLE_TIMEOUT` | 600 | Auto-unload after N seconds |
| `MAX_UPLOAD_SIZE` | 500 | Max upload size (MB) |

### VAE Tiling Settings

| Preset | Tile Size | Overlap | VRAM | Quality |
|--------|-----------|---------|------|---------|
| Low VRAM | 512×512 | 64 | 8GB | Good |
| Balanced | 768×768 | 96 | 16GB | Better |
| High Quality | 1024×1024 | 128 | 24GB | Best |

---

## 📊 Changelog

### v1.3.2 (2025-12-26)
- 🔒 **Privacy Fix**: Removed all user files from Docker images
- 📁 Added volume mount documentation for privacy-safe deployment
- 📁 Added tmpfs option for maximum privacy (memory storage)
- 🧹 Clean `/app/uploads` and `/app/outputs` directories in all images

### v1.3.1 (2025-12-26)
- 🐛 Fixed MCP BFloat16 conversion error in upscale_image/upscale_video
- ✅ All 5 MCP tools fully tested and working
- ✅ All 9 REST API endpoints verified

### v1.3.0 (2025-12-26)
- ✅ VAE Quality presets (Low/Balanced/High)
- ✅ Ultra-high resolution: 10K/12K/16K support
- ✅ Smart VAE auto-enable
- ✅ 5 Docker images for different use cases
- ✅ Complete API documentation with Swagger

### v1.2.x (2025-12-25)
- ✅ VAE Tiling compatibility fix
- ✅ Memory management optimization
- ✅ H.264 encoding + audio preservation
- ✅ Before/After comparison slider

---

## 📜 License

Apache License 2.0 - Based on [SeedVR2](https://github.com/ByteDance-Seed/SeedVR) by ByteDance

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
