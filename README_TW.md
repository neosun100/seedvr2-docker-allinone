[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 影片超解析度 - Docker 一體化版

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 一鍵部署 AI 影片/圖片超解析度 Web 服務**

*基於 [字節跳動 SeedVR2](https://github.com/ByteDance-Seed/SeedVR) | 增強版 Docker 一體化方案*

<img src="https://img.aws.xin/uPic/IaHGPU.png" alt="Web UI 截圖">

</div>

---

## ✨ 功能特性

| 功能 | 說明 |
|------|------|
| **12 個 AI 模型** | 3B/7B/7B-Sharp × FP16/FP8/GGUF 多種精度 |
| **🔄 任務佇列** | 串列 GPU 處理，支援多用戶同時提交（v1.4.0 新增）|
| **三種介面** | Web UI + REST API + MCP |
| **解析度支援** | 480p → 16K |
| **VAE Tiling** | 高解析度處理，智慧自動開啟 |
| **H.264 編碼** | 瀏覽器相容影片 + 保留原音軌 |
| **多語言介面** | 中文/英文/繁體中文/日語 |

---

## 🚀 快速開始

```bash
# 建立目錄
mkdir -p /tmp/seedvr2/uploads /tmp/seedvr2/outputs

# 啟動容器
docker run -d --gpus all -p 8200:8200 \
  -v /tmp/seedvr2/uploads:/app/uploads \
  -v /tmp/seedvr2/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

然後開啟：**http://localhost:8200**

---

## 🐳 Docker 映像檔

| 映像檔標籤 | 包含模型 | 大小 | 適用場景 |
|------------|----------|------|----------|
| `latest` / `v1.4.0` | 全部 12 個 | ~103GB | 完整功能 + 任務佇列 |
| `v1.4.0-12models-16k-vaetiling-h264-bilingual` | 全部 12 個 | ~103GB | 完整功能 |
| `v1.4.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~26GB | 快速處理 |
| `v1.4.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~49GB | 高品質 |
| `v1.4.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~49GB | 細節增強 |
| `v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~27GB | 最小體積 |

> ⚠️ **建議使用最新版本**以獲得最佳體驗和安全性。

---

## 🔄 任務佇列系統（v1.4.0 新增）

### 核心特性
- **串列 GPU 處理**：任務逐一執行，避免 CUDA OOM
- **多用戶支援**：100+ 用戶可同時提交任務
- **即時狀態**：佇列長度、位置、預估等待時間
- **歷史記錄**：追蹤已完成/失敗的任務

### 佇列 API

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/queue/status` | GET | 佇列概覽（處理中、等待中、已完成數量）|
| `/api/queue/position/{task_id}` | GET | 任務位置和預估等待時間 |
| `/api/queue/history` | GET | 已完成任務歷史 |

---

## 🔧 MCP 介面

支援 Claude Desktop、Cursor 等 MCP 客戶端直接呼叫。

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

### MCP 佇列功能（v1.4.0）
- `get_queue_status()` - 取得佇列狀態
- `submit_image_task()` / `submit_video_task()` - 提交任務到佇列
- `get_task_position()` - 查詢佇列位置
- `wait_for_task()` - 阻塞等待任務完成

---

## 📊 更新日誌

### v1.4.0 - 任務佇列版（2025-12-26）
#### 🔄 任務佇列系統
- ✅ **串列 GPU 處理** - 任務逐一執行，無 CUDA OOM
- ✅ **多用戶支援** - 100+ 用戶可同時提交
- ✅ **佇列狀態 API** - 即時佇列長度、位置、預估時間
- ✅ **佇列歷史** - 追蹤已完成/失敗任務
- ✅ **UI 佇列面板** - 即時佇列狀態顯示

### v1.3.3 - UI 增強（2025-12-26）
- ✅ **專案頁腳** - Web UI 新增 GitHub/Docker Hub 連結
- ✅ 改進 UI 佈局和品牌展示

### v1.3.2 - 隱私與安全（2025-12-26）
- 🔒 **隱私修復** - 從 Docker 映像檔中移除所有用戶檔案
- 📁 **卷掛載** - 推薦使用宿主機目錄掛載部署
- 📖 **MCP 文件** - 完整的客戶端註冊範例

### v1.3.1 - MCP 修復（2025-12-26）
- 🐛 **BFloat16 修復** - 修復 MCP 中 "Got unsupported ScalarType BFloat16" 錯誤

### v1.3.0 - 一體化發布版（2025-12-26）
- ✅ VAE 品質預設
- ✅ 16K 超高解析度支援

---

## 📜 授權條款

Apache License 2.0

基於 [SeedVR2](https://github.com/ByteDance-Seed/SeedVR)（字節跳動）

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
