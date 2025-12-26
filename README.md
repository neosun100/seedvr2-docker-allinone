[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 Video Upscaler - Docker All-in-One

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.2-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)
[![Stable](https://img.shields.io/badge/Stable-1.3.3-blue?style=for-the-badge)](https://hub.docker.com/r/neosun/seedvr2-allinone/tags)

**🚀 One-Click Deploy AI Video/Image Upscaler with Web UI**

*Based on [ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | Enhanced Docker All-in-One Edition*

[Quick Start](#-quick-start) • [Features](#-features) • [Docker Images](#-docker-images) • [API Docs](#-api-documentation) • [Changelog](#-changelog)

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
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.4.1-7b-sharp-fp16-only
```

Then open: **http://localhost:8200**

---

## 🐳 Docker Images

### Available Tags (v1.4.1)

| Image Tag | Models | Size | Use Case |
|-----------|--------|------|----------|
| `latest` / `v1.4.1` | All 12 | ~103GB | Full features + Task Queue |
| `v1.4.0-12models-16k-vaetiling-h264-bilingual` | All 12 | ~103GB | Full features |
| `v1.4.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~26GB | Fast processing |
| `v1.4.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~49GB | High quality |
| `v1.4.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~49GB | Detail enhancement |
| `v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~27GB | Minimal size |

---

## 📚 API Documentation

Full API documentation is available:

- **English:** [API.md](API.md)
- **中文:** [API_CN.md](API_CN.md)
- **Interactive Docs:** `http://localhost:8200/docs`

### Quick API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/gpu/status` | GET | GPU status |
| `/api/models` | GET | List models |
| `/api/models/switch` | POST | Load model |
| `/api/queue/status` | GET | Queue status |
| `/api/process` | POST | Submit task |
| `/api/status/{id}` | GET | Task status |
| `/api/download/{id}` | GET | Download result |

---

## 📊 Changelog

### v1.4.2 - Stability Release (2025-12-27)
#### 🐛 Bug Fixes
- ✅ **Fixed numpy import error** - Added missing `import numpy as np` that caused "name 'np' is not defined" error during video processing
- ✅ **Fixed model state tracking** - Model status now persists correctly across UI interactions
- ✅ **Fixed `/api/models` response** - Added `current`, `loading`, `loading_model` fields
- ✅ **Fixed `/api/models/switch`** - Now properly sets model state in GPUManager
- ✅ **Fixed startProcess override bug** - Removed broken empty function override
- ✅ **Fixed UI model display** - "✓ 已加载" indicator now shows correctly

#### Docker Tags
- `latest` → v1.4.2 (newest features + task queue)
- `stable` → v1.3.3 (proven stable, no task queue)

#### All v1.4.2 Variants Tested ✅
| Variant | Models | Queue | Processing Test |
|---------|--------|-------|-----------------|
| `v1.4.2` (12models) | 12 | ✅ | ✅ 5s |
| `v1.4.2-3b-fast-4models-...` | 4 | ✅ | ✅ 6s |
| `v1.4.2-7b-quality-4models-...` | 4 | ✅ | ✅ 15s |
| `v1.4.2-7b-sharp-4models-...` | 4 | ✅ | ✅ 16s |
| `v1.4.2-7b-sharp-fp16-only-...` | 1 | ✅ | ✅ 20s |

#### API Improvements
- `/api/gpu/status` now returns complete model state
- `/api/models` returns current loaded model info
- Full API documentation added (API.md, API_CN.md)

### v1.4.1 - Bug Fix Release (2025-12-27)
- 🐛 Intermediate fix release (superseded by v1.4.2)

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

### v1.3.2 - Privacy & Security (2025-12-26)
- 🔒 **Privacy Fix** - Removed all user files from Docker images
- 📁 **Volume Mount** - Recommended deployment with host directory mount

### v1.3.1 - MCP Bugfix (2025-12-26)
- 🐛 **BFloat16 Fix** - Fixed "Got unsupported ScalarType BFloat16" error in MCP

### v1.3.0 - All-in-One Release (2025-12-26)
- ✅ VAE Quality presets (Low/Balanced/High)
- ✅ Ultra-high resolution: 10K/12K/16K support
- ✅ Smart VAE auto-enable (Video≥2K / Image≥5K)

### v1.2.x - Earlier Releases
- VAE Tiling Fix, Memory Optimization, UI Enhancement

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
├── API.md              # API documentation (English)
├── API_CN.md           # API documentation (Chinese)
├── templates/
│   └── index.html      # Web UI
├── src/                # Core processing modules
├── models/SEEDVR2/     # AI models
└── outputs/            # Processing results
```

---

## 📜 License

Apache License 2.0 - Based on [SeedVR2](https://github.com/ByteDance-Seed/SeedVR) by ByteDance.

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
