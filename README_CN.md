[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 视频超分 - Docker 一体化版

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 一键部署 AI 视频/图片超分辨率 Web 服务**

*基于 [字节跳动 SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | 增强版 Docker 一体化方案*

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **12 个 AI 模型** | 3B/7B/7B-Sharp × FP16/FP8/GGUF 多种精度 |
| **分辨率支持** | 480p → 16K（支持自定义） |
| **VAE Tiling** | 高分辨率处理，智能自动开启 |
| **H.264 编码** | 浏览器兼容视频 + 保留原音轨 |
| **双语界面** | 中文/英文一键切换 |

---

## 🚀 快速开始

```bash
# 完整版，包含全部 12 个模型 (103GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest

# 轻量版：仅 7B Sharp FP16 (~15GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

然后打开：**http://localhost:8200**

---

## 🐳 Docker 镜像

| 镜像标签 | 包含模型 | 大小 | 适用场景 |
|----------|----------|------|----------|
| `v1.3.0-12models-16k-vaetiling-h264-memfix-bilingual` | 全部 12 个 | ~103GB | 完整功能 |
| `v1.3.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~35GB | 快速处理 |
| `v1.3.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~55GB | 高质量 |
| `v1.3.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~55GB | 细节增强 |
| `v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~15GB | 最小体积 |

---

## 📜 许可证

Apache License 2.0

基于 [SeedVR2](https://github.com/ByteDance-Seed/SeedVR)（字节跳动）和 [ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler)（NumZ & AInVFX）。

---

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/seedvr2-docker-allinone&type=Date)](https://star-history.com/#neosun100/seedvr2-docker-allinone)

---

## 📱 关注公众号

<div align="center">

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

</div>

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>