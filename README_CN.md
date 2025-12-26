[English](README_NEW.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 视频超分 - Docker 一体化版

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 一键部署 AI 视频/图片超分辨率 Web 服务**

*基于 [字节跳动 SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | 增强版 Docker 一体化方案*

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [Docker 镜像](#-docker-镜像) • [更新日志](#-更新日志)

</div>

---

## ✨ 功能特性

### 🎯 核心能力
| 功能 | 说明 |
|------|------|
| **12 个 AI 模型** | 3B/7B/7B-Sharp × FP16/FP8/GGUF 多种精度 |
| **分辨率支持** | 480p → 16K（支持自定义） |
| **VAE Tiling** | 高分辨率处理，智能自动开启 |
| **H.264 编码** | 浏览器兼容视频 + 保留原音轨 |
| **双语界面** | 中文/英文一键切换 |

### 🆕 增强功能（相比原版）
| 增强项 | 详情 |
|--------|------|
| **🔄 任务队列** | 串行 GPU 处理，支持多用户同时提交 (v1.4.0) |
| **Web UI** | 现代响应式界面，带对比滑块预览 |
| **智能 VAE** | 自动开启：视频 ≥2K / 图片 ≥5K |
| **VAE 质量** | 3 档可选：省显存(512) / 平衡(768) / 高质量(1024) |
| **显存管理** | 自动清理、模型卸载、优化流水线 |
| **丰富文件名** | `{名称}_{模型}_{分辨率}p_b{批大小}_c{颜色}_s{种子}[_vae{质量}]_{耗时}s` |
| **Docker 就绪** | 5 个预构建镜像，适配不同场景 |

---

## 🚀 快速开始

### 一行命令启动

```bash
# 完整版，包含全部 12 个模型 (103GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest

# 轻量版：仅 7B Sharp FP16 (~15GB)
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual
```

然后打开：**http://localhost:8200**

---

## 🐳 Docker 镜像

### 可用标签

| 镜像标签 | 包含模型 | 大小 | 适用场景 |
|----------|----------|------|----------|
| `v1.3.0-12models-16k-vaetiling-h264-memfix-bilingual` | 全部 12 个 | ~103GB | 完整功能 |
| `v1.3.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~35GB | 快速处理 |
| `v1.3.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~55GB | 高质量 |
| `v1.3.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~55GB | 细节增强 |
| `v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~15GB | 最小体积 |

### 标签命名规则
- `v1.3.0` - 版本号
- `12models/4models/fp16-only` - 模型数量
- `16k` - 最高支持 16K 分辨率
- `vaetiling` - VAE Tiling 高分辨率处理
- `h264` - H.264 编码 + 音频保留
- `bilingual` - 中英文双语界面

---

## 📦 安装部署

### 方式一：Docker（推荐）

#### 前置条件
- Docker 20.10+
- NVIDIA GPU（8GB+ 显存）
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

#### 健康检查
```bash
curl http://localhost:8200/health
# {"status": "healthy", "gpu": "available"}
```

### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/neosun100/seedvr2-docker-allinone.git
cd seedvr2-docker-allinone

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 下载模型（首次使用自动下载）
# 或手动放置到 models/SEEDVR2/

# 启动服务
python server.py
```

---

## 🎮 使用说明

### Web 界面

1. 打开 **http://localhost:8200**
2. 选择 AI 模型（3B/7B/7B-Sharp）
3. 上传视频/图片
4. 配置参数：
   - **分辨率**：480p - 16K
   - **批处理大小**：1-25（使用 4n+1 公式：1,5,9,13...）
   - **颜色校正**：LAB/Wavelet/HSV/AdaIN/无
   - **VAE Tiling**：自动/开启/关闭
   - **VAE 质量**：省显存/平衡/高质量
5. 点击"开始处理"
6. 使用对比滑块预览
7. 下载结果

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/gpu/status` | GET | GPU 状态 |
| `/api/models` | GET | 列出可用模型 |
| `/api/models/switch` | POST | 加载模型到 GPU |
| `/api/process` | POST | 开始处理 |
| `/api/task/{id}` | GET | 获取任务状态 |
| `/api/download/{id}` | GET | 下载结果 |

### API 调用示例
```bash
curl -X POST http://localhost:8200/api/process \
  -F "file=@input.mp4" \
  -F "resolution=1080" \
  -F "batch_size=5" \
  -F "dit_model=seedvr2_ema_7b_sharp_fp16.safetensors"
```

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 8200 | 服务端口 |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU 设备 ID |
| `GPU_IDLE_TIMEOUT` | 600 | 空闲 N 秒后自动卸载模型 |
| `DEFAULT_RESOLUTION` | 1080 | 默认输出分辨率 |
| `DEFAULT_BATCH_SIZE` | 5 | 默认批处理大小 |
| `MAX_UPLOAD_SIZE` | 500 | 最大上传大小 (MB) |

### 模型选择指南

| 模型 | 显存 | 速度 | 质量 | 适用场景 |
|------|------|------|------|----------|
| 3B FP16 | 12GB | ⚡⚡⚡ | ★★★ | 快速预览 |
| 3B FP8 | 8GB | ⚡⚡⚡ | ★★★ | 低显存 |
| 3B GGUF Q8 | 6GB | ⚡⚡ | ★★☆ | 极低显存 |
| 7B FP16 | 24GB | ⚡⚡ | ★★★★ | 高质量 |
| 7B FP8 | 16GB | ⚡⚡ | ★★★★ | 平衡 |
| 7B Sharp FP16 | 24GB | ⚡⚡ | ★★★★★ | 最佳细节 |

### VAE Tiling 设置

| 预设 | Tile 大小 | 重叠 | 显存 | 质量 |
|------|-----------|------|------|------|
| 省显存 | 512×512 | 64 | 8GB | 良好 |
| 平衡 | 768×768 | 96 | 16GB | 较好 |
| 高质量 | 1024×1024 | 128 | 24GB | 最佳 |

---

## 📊 更新日志

### v1.4.0 - 任务队列版 (2025-12-26)
#### 🔄 任务队列系统
- ✅ **串行 GPU 处理** - 任务逐个处理，无 CUDA OOM
- ✅ **多用户支持** - 100+ 用户可同时提交
- ✅ **队列状态 API** - 实时队列长度、位置、预计等待时间
- ✅ **队列历史** - 跟踪已完成/失败任务
- ✅ **UI 队列面板** - 实时队列状态显示

#### 新增 API 端点
- `GET /api/queue/status` - 队列概览（处理中、等待中、已完成）
- `GET /api/queue/position/{task_id}` - 任务位置和预计等待
- `GET /api/queue/history` - 已完成任务历史

#### MCP 增强
- `get_queue_status()` - 队列状态
- `submit_image_task()` / `submit_video_task()` - 提交到队列
- `get_task_position()` - 检查队列位置
- `wait_for_task()` - 阻塞等待完成

### v1.3.0 - 一体化发布版 (2025-12-26)
#### 新功能
- ✅ VAE 质量预设（省显存/平衡/高质量）
- ✅ 超高分辨率支持：10K/12K/16K
- ✅ 智能 VAE 自动开启（视频≥2K / 图片≥5K）
- ✅ 丰富的输出文件名，包含所有参数

#### 优化
- ✅ VAE Tiling 兼容性修复
- ✅ 显存管理优化
- ✅ 5 个 Docker 镜像适配不同场景

### v1.2.2 - VAE Tiling 修复 (2025-12-25)
- 🐛 修复 "cannot unpack non-iterable NoneType" 错误
- ✅ 添加默认 tile_size/tile_overlap 值

### v1.2.1 - 显存优化 (2025-12-25)
- ✅ 自动 GPU 显存清理（finally 块）
- ✅ upscale 阶段后强制清理缓存
- ✅ 模型卸载到 CPU

### v1.2.0 - UI 增强 (2025-12-25)
- ✅ 前后对比滑块
- ✅ 分辨率预设（480p-8K）
- ✅ VAE Tiling UI 控制
- ✅ H.264 视频编码
- ✅ 保留原视频音轨
- ✅ 丰富的输出文件名格式

### v1.1.0 - 全模型支持 (2025-12-24)
- ✅ 全部 12 个模型测试通过
- ✅ 模型热切换支持
- ✅ 预加载到内存功能

### v1.0.0 - Docker 发布 (2025-12-24)
- ✅ Docker 容器化
- ✅ Web UI / API / MCP 三种模式
- ✅ GPU 自动检测
- ✅ 中英文双语界面

---

## 🏗️ 项目结构

```
seedvr2-docker-allinone/
├── server.py           # Flask Web 服务器
├── templates/
│   └── index.html      # Web UI
├── src/                # 核心处理模块
├── models/SEEDVR2/     # AI 模型（自动下载）
├── configs_3b/         # 3B 模型配置
├── configs_7b/         # 7B 模型配置
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker Compose 配置
├── requirements.txt    # Python 依赖
└── outputs/            # 处理结果
```

---

## 🛠️ 技术栈

- **AI 框架**：PyTorch 2.0+, Diffusers
- **模型**：字节跳动 SeedVR2 (3B/7B)
- **后端**：Flask, Gunicorn
- **前端**：原生 JS, CSS3
- **容器**：Docker, NVIDIA Container Toolkit
- **视频**：OpenCV, FFmpeg (H.264)

---

## 🤝 贡献指南

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 发起 Pull Request

---

## 📜 许可证

本项目采用 Apache License 2.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

基于 [SeedVR2](https://github.com/ByteDance-Seed/SeedVR)（字节跳动）和 [ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler)（NumZ & AInVFX）。

---

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/seedvr2-docker-allinone&type=Date)](https://star-history.com/#neosun100/seedvr2-docker-allinone)

---

## 📱 关注公众号

<div align="center">

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

**扫码关注公众号，获取更多 AI 资讯**

</div>

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
