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

# Lightweight: 7B Sharp FP16 only (~27GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

Then open: **http://localhost:8200**

---

## 🐳 Docker Images

### Available Tags

| Image Tag | Models | Size | Use Case |
|-----------|--------|------|----------|
| `v1.3.0-12models-16k-vaetiling-h264-memfix-bilingual` | All 12 | ~103GB | Full features |
| `v1.3.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~26GB | Fast processing |
| `v1.3.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~49GB | High quality |
| `v1.3.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~49GB | Detail enhancement |
| `v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~27GB | Minimal size |

---

## 📦 Installation

### Docker (Recommended)

```bash
docker run -d \
  --name seedvr2 \
  --gpus all \
  -p 8200:8200 \
  -v ./outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

### Manual Installation

```bash
git clone https://github.com/neosun100/seedvr2-docker-allinone.git
cd seedvr2-docker-allinone
pip install -r requirements.txt
python server.py
```

---

## 🎮 Usage

1. Open **http://localhost:8200**
2. Select AI model (3B/7B/7B-Sharp)
3. Upload video/image
4. Configure: Resolution, Batch Size, Color Correction, VAE Tiling
5. Click "Start Processing"
6. Download result

---

## 📊 Changelog

### v1.3.0 (2025-12-26)
- ✅ VAE Quality presets (Low/Balanced/High)
- ✅ Ultra-high resolution: 10K/12K/16K support
- ✅ Smart VAE auto-enable
- ✅ 5 Docker images for different use cases

### v1.2.x (2025-12-25)
- ✅ VAE Tiling compatibility fix
- ✅ Memory management optimization
- ✅ H.264 encoding + audio preservation

---

## 📜 License

Apache License 2.0 - Based on [SeedVR2](https://github.com/ByteDance-Seed/SeedVR) by ByteDance

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
