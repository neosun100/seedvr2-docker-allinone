[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 视频超分 - Docker 一体化版

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.2-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 一键部署 AI 视频/图片超分辨率 Web 服务**

*基于 [字节跳动 SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | 增强版 Docker 一体化方案*

<img src="https://img.aws.xin/uPic/IaHGPU.png" alt="Web UI 截图">

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **12 个 AI 模型** | 3B/7B/7B-Sharp × FP16/FP8/GGUF 多种精度 |
| **三种接口** | Web UI + REST API + MCP（模型上下文协议） |
| **分辨率支持** | 480p → 16K（支持自定义） |
| **VAE Tiling** | 高分辨率处理，智能自动开启 |
| **H.264 编码** | 浏览器兼容视频 + 保留原音轨 |
| **多语言界面** | 中文/英文/繁体中文/日语 |
| **隐私安全** | 镜像不含用户数据 |

---

## 🎯 效果展示

| 原图 | 超分后 (2160p) |
|:----:|:--------------:|
| ![原图](https://img.aws.xin/uPic/liu.jpeg) | ![超分后](https://img.aws.xin/uPic/liu_7b_sharp_fp16_2160p_b5_clab_s42_22s.png) |

![处理前后对比](https://img.aws.xin/uPic/ZZ3Nwy.png)

---

## 🚀 快速开始

### 推荐方式：挂载本地目录

```bash
# 创建目录
mkdir -p /tmp/seedvr2-docker-allinone/uploads /tmp/seedvr2-docker-allinone/outputs

# 启动容器
docker run -d --gpus all -p 8200:8200 \
  -v /tmp/seedvr2-docker-allinone/uploads:/app/uploads \
  -v /tmp/seedvr2-docker-allinone/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

然后打开：
- **Web UI**：http://localhost:8200
- **API 文档**：http://localhost:8200/apidocs

---

## 🐳 Docker 镜像

| 镜像标签 | 包含模型 | 大小 | 适用场景 |
|----------|----------|------|----------|
| `latest` / `v1.3.2-12models-*` | 全部 12 个 | ~103GB | 完整功能 |
| `v1.3.2-3b-fast-4models-*` | 4× 3B | ~26GB | 快速处理 |
| `v1.3.2-7b-quality-4models-*` | 4× 7B | ~49GB | 高质量 |
| `v1.3.2-7b-sharp-4models-*` | 4× 7B Sharp | ~49GB | 细节增强 |
| `v1.3.2-7b-sharp-fp16-only-*` | 1× 7B Sharp FP16 | ~27GB | 最小体积 |

> ⚠️ **建议使用最新版本**以获得最佳体验和安全性。

---

## 📚 API 使用

### 处理图片/视频

```bash
# 提交任务
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5"

# 查询状态
curl http://localhost:8200/api/status/{task_id}

# 下载结果
curl -O http://localhost:8200/api/download/{task_id}
```

---

## 🔧 MCP 接口

支持 Claude Desktop、Cursor 等 MCP 客户端直接调用。

**Claude Desktop 配置**：

```json
{
  "mcpServers": {
    "seedvr2-upscaler": {
      "command": "docker",
      "args": ["exec", "-i", "seedvr2-upscaler", "python", "/app/mcp_server.py"]
    }
  }
}
```

### MCP 工具

| 工具 | 说明 |
|------|------|
| `upscale_image` | 图片超分 |
| `upscale_video` | 视频超分 |
| `get_gpu_status` | GPU 状态 |
| `release_gpu_memory` | 释放显存 |
| `list_available_models` | 模型列表 |

---

## 📊 更新日志

### v1.3.2（最新）
- 🔒 安全性优化
- 📁 支持宿主机目录挂载
- 📖 完善 MCP 文档

### v1.3.1
- 🐛 修复 MCP BFloat16 转换问题

### v1.3.0
- ✅ VAE 质量预设
- ✅ 16K 超高分辨率支持
- ✅ Swagger API 文档

---

## 📜 许可证

Apache License 2.0

基于 [SeedVR2](https://github.com/ByteDance-Seed/SeedVR)（字节跳动）

---

## 📱 关注公众号

<div align="center">

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

</div>

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
