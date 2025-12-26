[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 Video Upscaler - Docker All-in-One

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 One-Click Deploy AI Video/Image Upscaler with Web UI**

*Based on [ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | Enhanced Docker All-in-One Edition*

[Quick Start](#-quick-start) • [Features](#-features) • [Docker Images](#-docker-images) • [Changelog](#-changelog)

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
# Full version with all 12 models (103GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest

# Lightweight: 7B Sharp FP16 only (~15GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

Then open: **http://localhost:8200**

---

## 🐳 Docker Images

### Available Tags

| Image Tag | Models | Size | Use Case |
|-----------|--------|------|----------|
| `v1.3.0-12models-16k-vaetiling-h264-memfix-bilingual` | All 12 | ~103GB | Full features |
| `v1.3.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~35GB | Fast processing |
| `v1.3.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~55GB | High quality |
| `v1.3.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~55GB | Detail enhancement |
| `v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~15GB | Minimal size |

### Tag Naming Convention
- `v1.3.0` - Version
- `12models/4models/fp16-only` - Model count
- `16k` - Max resolution support
- `vaetiling` - VAE Tiling for high-res
- `h264` - H.264 encoding + audio
- `bilingual` - CN/EN UI

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
  -v ./outputs:/app/outputs \
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
      - ./outputs:/app/outputs
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

### v1.3.0 - All-in-One Release (2024-12-26)
#### New Features
- ✅ VAE Quality presets (Low/Balanced/High)
- ✅ Ultra-high resolution: 10K/12K/16K support
- ✅ Smart VAE auto-enable (Video≥2K / Image≥5K)
- ✅ Rich output filename with all parameters

#### Improvements
- ✅ VAE Tiling compatibility fix
- ✅ Memory management optimization
- ✅ 5 Docker images for different use cases

### v1.2.2 - VAE Tiling Fix (2024-12-25)
- 🐛 Fixed "cannot unpack non-iterable NoneType" error
- ✅ Added default tile_size/tile_overlap values

### v1.2.1 - Memory Optimization (2024-12-25)
- ✅ Auto GPU memory cleanup (finally block)
- ✅ Force cache clear after upscale phase
- ✅ Model offload to CPU

### v1.2.0 - UI Enhancement (2024-12-25)
- ✅ Before/After comparison slider
- ✅ Resolution presets (480p-8K)
- ✅ VAE Tiling UI control
- ✅ H.264 video encoding
- ✅ Audio preservation from original video
- ✅ Rich output filename format

### v1.1.0 - All Models (2024-12-24)
- ✅ All 12 models tested and working
- ✅ Model hot-switching support
- ✅ Preload to memory feature

### v1.0.0 - Docker Release (2024-12-24)
- ✅ Docker containerization
- ✅ Web UI / API / MCP modes
- ✅ GPU auto-detection
- ✅ Bilingual interface (CN/EN)

---

## 🛠️ Tech Stack

- **AI Framework**: PyTorch 2.0+, Diffusers
- **Models**: ByteDance SeedVR2 (3B/7B)
- **Backend**: Flask, Gunicorn
- **Frontend**: Vanilla JS, CSS3
- **Container**: Docker, NVIDIA Container Toolkit
- **Video**: OpenCV, FFmpeg (H.264)

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
