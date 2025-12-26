[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 Video Upscaler - Docker All-in-One

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 One-Click Deploy AI Video/Image Upscaler with Web UI**

*Based on [ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | Enhanced Docker All-in-One Edition*

[Quick Start](#-quick-start) • [Features](#-features) • [Docker Images](#-docker-images) • [Changelog](#-changelog)

<img src="https://img.aws.xin/uPic/IaHGPU.png" alt="Web UI Screenshot" width="280">

</div>

---

## ✨ Features

### 🎯 Core Capabilities
| Feature | Description |
|---------|-------------|
| **12 AI Models** | 3B/7B/7B-Sharp × FP16/FP8/GGUF variants |
| **Resolution Support** | 480p → 16K (custom supported) |
| **VAE Tiling** | High-resolution processing with smart auto-enable |
| **H.264 Encoding** | Browser-compatible video + audio preservation |
| **Bilingual UI** | Chinese/English interface with one-click switch |

### 🆕 Enhanced Features (vs Original)
| Enhancement | Details |
|-------------|---------|
| **🔄 Task Queue** | Serial GPU processing, multi-user support (v1.4.0) |
| **Web UI** | Modern responsive interface with comparison slider |
| **Smart VAE** | Auto-enable: Video ≥2K / Image ≥5K |
| **VAE Quality** | 3 presets: Low VRAM (512) / Balanced (768) / High Quality (1024) |
| **Memory Management** | Auto cleanup, model offloading, optimized pipeline |
| **Rich Filename** | `{name}_{model}_{res}p_b{batch}_c{color}_s{seed}[_vae{quality}]_{time}s` |
| **Docker Ready** | 5 pre-built images for different use cases |

---

## 🚀 Quick Start

### One-Line Docker Run

```bash
# Full version with all 12 models (103GB) - Recommended
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest

# Lightweight: 7B Sharp FP16 only (~27GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

Then open: **http://localhost:8200**

---

## 🐳 Docker Images

### Available Tags (v1.4.0)

| Image Tag | Models | Size | Use Case |
|-----------|--------|------|----------|
| `latest` / `v1.4.0` | All 12 | ~103GB | Full features + Task Queue |
| `v1.4.0-12models-16k-vaetiling-h264-bilingual` | All 12 | ~103GB | Full features |
| `v1.4.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~26GB | Fast processing |
| `v1.4.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~49GB | High quality |
| `v1.4.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~49GB | Detail enhancement |
| `v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~27GB | Minimal size |

### Tag Naming Convention
- `v1.4.0` - Version
- `12models/4models/fp16-only` - Model count
- `16k` - Max resolution support
- `vaetiling` - VAE Tiling for high-res
- `h264` - H.264 encoding + audio
- `bilingual` - CN/EN UI

---

### 📦 Image Details & Quick Start

#### 1. Full Version (All 12 Models) - 103GB
Best for users who want all model options.

```bash
docker run -d --name seedvr2 --gpus all -p 8200:8200 \
  -v /tmp/seedvr2/uploads:/app/uploads \
  -v /tmp/seedvr2/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

**Included Models:**
- 3B: FP16, FP8, GGUF-Q8, GGUF-Q4
- 7B: FP16, FP8, GGUF-Q8, GGUF-Q4
- 7B Sharp: FP16, FP8, GGUF-Q8, GGUF-Q4

---

#### 2. 3B Fast (4 Models) - 26GB
Best for fast processing and low VRAM GPUs.

```bash
docker run -d --name seedvr2-3b --gpus all -p 8200:8200 \
  neosun/seedvr2-allinone:v1.4.0-3b-fast-4models-16k-vaetiling-h264-bilingual
```

**Included Models:**
- seedvr2_ema_3b_fp16.safetensors (6.4GB, 12GB VRAM)
- seedvr2_ema_3b_fp8_e4m3fn.safetensors (3.2GB, 8GB VRAM)
- seedvr2_ema_3b-Q8_0.gguf (3.5GB, 6GB VRAM)
- seedvr2_ema_3b-Q4_K_M.gguf (1.9GB, 4GB VRAM)

**Use Case:** Quick preview, low-end GPUs (GTX 1080, RTX 3060)

---

#### 3. 7B Quality (4 Models) - 49GB
Best for high-quality output.

```bash
docker run -d --name seedvr2-7b --gpus all -p 8200:8200 \
  neosun/seedvr2-allinone:v1.4.0-7b-quality-4models-16k-vaetiling-h264-bilingual
```

**Included Models:**
- seedvr2_ema_7b_fp16.safetensors (16GB, 24GB VRAM)
- seedvr2_ema_7b_fp8_e4m3fn.safetensors (8GB, 16GB VRAM)
- seedvr2_ema_7b-Q8_0.gguf (8GB, 12GB VRAM)
- seedvr2_ema_7b-Q4_K_M.gguf (4GB, 8GB VRAM)

**Use Case:** Professional quality, mid-range GPUs (RTX 3080, RTX 4070)

---

#### 4. 7B Sharp (4 Models) - 49GB
Best for detail enhancement and sharpening.

```bash
docker run -d --name seedvr2-sharp --gpus all -p 8200:8200 \
  neosun/seedvr2-allinone:v1.4.0-7b-sharp-4models-16k-vaetiling-h264-bilingual
```

**Included Models:**
- seedvr2_ema_7b_sharp_fp16.safetensors (16GB, 24GB VRAM)
- seedvr2_ema_7b_sharp_fp8_e4m3fn.safetensors (8GB, 16GB VRAM)
- seedvr2_ema_7b_sharp-Q8_0.gguf (8GB, 12GB VRAM)
- seedvr2_ema_7b_sharp-Q4_K_M.gguf (4GB, 8GB VRAM)

**Use Case:** Maximum detail, texture enhancement, high-end GPUs (RTX 4080, RTX 4090)

---

#### 5. 7B Sharp FP16 Only - 27GB
Minimal size with best quality model.

```bash
docker run -d --name seedvr2-minimal --gpus all -p 8200:8200 \
  neosun/seedvr2-allinone:v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

**Included Models:**
- seedvr2_ema_7b_sharp_fp16.safetensors (16GB, 24GB VRAM)

**Use Case:** Best quality with minimal download, RTX 4090 / A100 users

---

## 📦 Installation

### Method 1: Docker (Recommended)

#### Prerequisites
- Docker 20.10+
- NVIDIA GPU with 8GB+ VRAM
- NVIDIA Container Toolkit

#### Docker Run
```bash
docker run -d \
  --name seedvr2 \
  --gpus '"device=0"' \
  -p 8200:8200 \
  -v /tmp/seedvr2/uploads:/app/uploads \
  -v /tmp/seedvr2/outputs:/app/outputs \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  neosun/seedvr2-allinone:latest
```

#### Docker Compose
```yaml
version: '3.8'
services:
  seedvr2:
    image: neosun/seedvr2-allinone:latest
    container_name: seedvr2
    ports:
      - "8200:8200"
    volumes:
      - /tmp/seedvr2/uploads:/app/uploads
      - /tmp/seedvr2/outputs:/app/outputs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
    restart: unless-stopped
```

```bash
docker-compose up -d
```

#### Health Check
```bash
curl http://localhost:8200/health
# {"status": "healthy", "gpu": "available"}
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/neosun100/seedvr2-docker-allinone.git
cd seedvr2-docker-allinone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download models (auto-download on first use)
# Or manually place in models/SEEDVR2/

# Start server
python server.py
```

---

## 🎮 Usage

### Web Interface

1. Open **http://localhost:8200**
2. Select AI model (3B/7B/7B-Sharp)
3. Upload video/image
4. Configure parameters:
   - **Resolution**: 480p - 16K
   - **Batch Size**: 1-25 (use 4n+1 formula: 1,5,9,13...)
   - **Color Correction**: LAB/Wavelet/HSV/AdaIN/None
   - **VAE Tiling**: Auto/On/Off
   - **VAE Quality**: Low VRAM/Balanced/High Quality
5. Click "Start Processing"
6. Preview with comparison slider
7. Download result

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/gpu/status` | GET | GPU status |
| `/api/models` | GET | List available models |
| `/api/models/switch` | POST | Load model to GPU |
| `/api/process` | POST | Start processing |
| `/api/task/{id}` | GET | Get task status |
| `/api/download/{id}` | GET | Download result |
| `/api/queue/status` | GET | Queue overview (v1.4.0) |
| `/api/queue/position/{id}` | GET | Task position in queue (v1.4.0) |
| `/api/queue/history` | GET | Completed task history (v1.4.0) |

### Example API Call
```bash
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5" \
  -F "dit_model=seedvr2_ema_7b_sharp_fp16.safetensors"
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8200 | Server port |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID |
| `GPU_IDLE_TIMEOUT` | 600 | Auto-unload model after N seconds |
| `DEFAULT_RESOLUTION` | 1080 | Default output resolution |
| `DEFAULT_BATCH_SIZE` | 5 | Default batch size |
| `MAX_UPLOAD_SIZE` | 500 | Max upload size (MB) |

### Model Selection Guide

| Model | VRAM | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| 3B FP16 | 12GB | ⚡⚡⚡ | ★★★ | Fast preview |
| 3B FP8 | 8GB | ⚡⚡⚡ | ★★★ | Low VRAM |
| 3B GGUF Q8 | 6GB | ⚡⚡ | ★★☆ | Minimal VRAM |
| 7B FP16 | 24GB | ⚡⚡ | ★★★★ | High quality |
| 7B FP8 | 16GB | ⚡⚡ | ★★★★ | Balanced |
| 7B Sharp FP16 | 24GB | ⚡⚡ | ★★★★★ | Best detail |

### VAE Tiling Settings

| Preset | Tile Size | Overlap | VRAM | Quality |
|--------|-----------|---------|------|---------|
| Low VRAM | 512×512 | 64 | 8GB | Good |
| Balanced | 768×768 | 96 | 16GB | Better |
| High Quality | 1024×1024 | 128 | 24GB | Best |

---

## 📊 Changelog

### v1.4.0 - Task Queue Edition (2025-12-26)
#### 🔄 Task Queue System
- ✅ **Serial GPU Processing** - Tasks processed one by one, no CUDA OOM
- ✅ **Multi-user Support** - 100+ users can submit simultaneously
- ✅ **Queue Status API** - Real-time queue length, position, ETA
- ✅ **Queue History** - Track completed/failed tasks
- ✅ **UI Queue Panel** - Live queue status display

#### New API Endpoints
- `GET /api/queue/status` - Queue overview (processing, waiting, completed)
- `GET /api/queue/position/{task_id}` - Task position and estimated wait
- `GET /api/queue/history` - Completed task history

#### MCP Enhancements
- `get_queue_status()` - Queue status
- `submit_image_task()` / `submit_video_task()` - Submit to queue
- `get_task_position()` - Check queue position
- `wait_for_task()` - Blocking wait for completion

### v1.3.3 - UI Enhancement (2025-12-26)
- ✅ **Project Footer** - Added GitHub/Docker Hub links in Web UI
- ✅ Improved UI layout and branding

### v1.3.2 - Privacy & Security (2025-12-26)
- 🔒 **Privacy Fix** - Removed all user files from Docker images
- 📁 **Volume Mount** - Recommended deployment with host directory mount
- 📁 **tmpfs Option** - Maximum privacy with memory-only storage
- 📖 **MCP Documentation** - Complete client registration examples (Claude Desktop, Cursor)
- 📖 **WeChat Article** - Added project promotion article

### v1.3.1 - MCP Bugfix (2025-12-26)
- 🐛 **BFloat16 Fix** - Fixed "Got unsupported ScalarType BFloat16" error in MCP
- ✅ Added tensor dtype conversion before numpy conversion
- ✅ Matches server.py implementation

### v1.3.0 - All-in-One Release (2025-12-26)
#### New Features
- ✅ VAE Quality presets (Low/Balanced/High)
- ✅ Ultra-high resolution: 10K/12K/16K support
- ✅ Smart VAE auto-enable (Video≥2K / Image≥5K)
- ✅ Rich output filename with all parameters

#### Improvements
- ✅ VAE Tiling compatibility fix
- ✅ Memory management optimization
- ✅ 5 Docker images for different use cases

### v1.2.2 - VAE Tiling Fix (2025-12-25)
- 🐛 Fixed "cannot unpack non-iterable NoneType" error
- ✅ Added default tile_size/tile_overlap values

### v1.2.1 - Memory Optimization (2025-12-25)
- ✅ Auto GPU memory cleanup (finally block)
- ✅ Force cache clear after upscale phase
- ✅ Model offload to CPU

### v1.2.0 - UI Enhancement (2025-12-25)
- ✅ Before/After comparison slider
- ✅ Resolution presets (480p-8K)
- ✅ VAE Tiling UI control
- ✅ H.264 video encoding
- ✅ Audio preservation from original video
- ✅ Rich output filename format

### v1.1.0 - All Models (2025-12-24)
- ✅ All 12 models tested and working
- ✅ Model hot-switching support
- ✅ Preload to memory feature

### v1.0.0 - Docker Release (2025-12-24)
- ✅ Docker containerization
- ✅ Web UI / API / MCP modes
- ✅ GPU auto-detection
- ✅ Bilingual interface (CN/EN)

---

## 🏗️ Project Structure

```
seedvr2-docker-allinone/
├── server.py           # Flask web server
├── mcp_server.py       # MCP server for AI assistants
├── templates/
│   └── index.html      # Web UI
├── src/                # Core processing modules
├── models/SEEDVR2/     # AI models (auto-download)
├── configs_3b/         # 3B model configs
├── configs_7b/         # 7B model configs
├── Dockerfile          # Docker build file
├── docker-compose.yml  # Docker Compose config
├── requirements.txt    # Python dependencies
└── outputs/            # Processing results
```

---

## 🛠️ Tech Stack

- **AI Framework**: PyTorch 2.0+, Diffusers
- **Models**: ByteDance SeedVR2 (3B/7B)
- **Backend**: Flask, Gunicorn
- **Frontend**: Vanilla JS, CSS3
- **Container**: Docker, NVIDIA Container Toolkit
- **Video**: OpenCV, FFmpeg (H.264)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📜 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file.

Based on [SeedVR2](https://github.com/ByteDance-Seed/SeedVR) by ByteDance and [ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler) by NumZ & AInVFX.

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/seedvr2-docker-allinone&type=Date)](https://star-history.com/#neosun100/seedvr2-docker-allinone)

---

## 📱 Follow Us

<div align="center">

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

**Scan to follow our WeChat Official Account**

</div>

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
