[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 動画アップスケーラー - Docker オールインワン版

[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/seedvr2-allinone?style=for-the-badge&logo=docker)](https://hub.docker.com/r/neosun/seedvr2-allinone)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/seedvr2-docker-allinone?style=for-the-badge&logo=github)](https://github.com/neosun100/seedvr2-docker-allinone)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.0-green?style=for-the-badge)](https://github.com/neosun100/seedvr2-docker-allinone/releases)

**🚀 ワンクリックでAI動画/画像アップスケーラーをデプロイ**

*[ByteDance SeedVR2](https://github.com/ByteDance-Seed/SeedVR) ベース | 強化版 Docker オールインワン*

<img src="https://img.aws.xin/uPic/IaHGPU.png" alt="Web UI スクリーンショット">

</div>

---

## ✨ 機能

| 機能 | 説明 |
|------|------|
| **12 AI モデル** | 3B/7B/7B-Sharp × FP16/FP8/GGUF |
| **🔄 タスクキュー** | シリアルGPU処理、マルチユーザー対応（v1.4.0 新機能）|
| **3つのインターフェース** | Web UI + REST API + MCP |
| **解像度サポート** | 480p → 16K |
| **VAE Tiling** | 高解像度処理、スマート自動有効化 |
| **H.264 エンコード** | ブラウザ互換動画 + オーディオ保持 |
| **多言語 UI** | 中国語/英語/繁体字中国語/日本語 |

---

## 🚀 クイックスタート

```bash
# ディレクトリ作成
mkdir -p /tmp/seedvr2/uploads /tmp/seedvr2/outputs

# コンテナ起動
docker run -d --gpus all -p 8200:8200 \
  -v /tmp/seedvr2/uploads:/app/uploads \
  -v /tmp/seedvr2/outputs:/app/outputs \
  neosun/seedvr2-allinone:latest
```

ブラウザで開く：**http://localhost:8200**

---

## 🐳 Docker イメージ

| イメージタグ | モデル | サイズ | 用途 |
|--------------|--------|--------|------|
| `latest` / `v1.4.0` | 全12個 | ~103GB | フル機能 + タスクキュー |
| `v1.4.0-12models-16k-vaetiling-h264-bilingual` | 全12個 | ~103GB | フル機能 |
| `v1.4.0-3b-fast-4models-16k-vaetiling-h264-bilingual` | 4× 3B | ~26GB | 高速処理 |
| `v1.4.0-7b-quality-4models-16k-vaetiling-h264-bilingual` | 4× 7B | ~49GB | 高品質 |
| `v1.4.0-7b-sharp-4models-16k-vaetiling-h264-bilingual` | 4× 7B Sharp | ~49GB | ディテール強化 |
| `v1.4.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~27GB | 最小サイズ |

> ⚠️ 最高の体験とセキュリティのため、**最新バージョンの使用を推奨**します。

---

## 🔄 タスクキューシステム（v1.4.0 新機能）

### コア機能
- **シリアルGPU処理**：タスクを1つずつ実行、CUDA OOMを回避
- **マルチユーザー対応**：100人以上が同時にタスク送信可能
- **リアルタイムステータス**：キュー長、位置、推定待ち時間
- **履歴記録**：完了/失敗タスクの追跡

### キュー API

| エンドポイント | メソッド | 説明 |
|----------------|----------|------|
| `/api/queue/status` | GET | キュー概要（処理中、待機中、完了数）|
| `/api/queue/position/{task_id}` | GET | タスク位置と推定待ち時間 |
| `/api/queue/history` | GET | 完了タスク履歴 |

---

## 🔧 MCP インターフェース

Claude Desktop、Cursor などの MCP クライアントから直接呼び出し可能。

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

### MCP キュー機能（v1.4.0）
- `get_queue_status()` - キューステータス取得
- `submit_image_task()` / `submit_video_task()` - キューにタスク送信
- `get_task_position()` - キュー位置確認
- `wait_for_task()` - タスク完了までブロッキング待機

---

## 📊 更新履歴

### v1.4.0 - タスクキュー版（2025-12-26）
#### 🔄 タスクキューシステム
- ✅ **シリアルGPU処理** - タスクを1つずつ実行、CUDA OOMなし
- ✅ **マルチユーザー対応** - 100人以上が同時送信可能
- ✅ **キューステータスAPI** - リアルタイムキュー長、位置、推定時間
- ✅ **キュー履歴** - 完了/失敗タスクの追跡
- ✅ **UIキューパネル** - リアルタイムキューステータス表示

### v1.3.3 - UI強化（2025-12-26）
- ✅ **プロジェクトフッター** - Web UIにGitHub/Docker Hubリンクを追加
- ✅ UIレイアウトとブランディングの改善

### v1.3.2 - プライバシーとセキュリティ（2025-12-26）
- 🔒 **プライバシー修正** - Dockerイメージからすべてのユーザーファイルを削除
- 📁 **ボリュームマウント** - ホストディレクトリマウントでのデプロイを推奨
- 📖 **MCPドキュメント** - 完全なクライアント登録例

### v1.3.1 - MCP修正（2025-12-26）
- 🐛 **BFloat16修正** - MCPの"Got unsupported ScalarType BFloat16"エラーを修正

### v1.3.0 - オールインワンリリース（2025-12-26）
- ✅ VAE品質プリセット
- ✅ 16K超高解像度サポート

---

## 📜 ライセンス

Apache License 2.0

[SeedVR2](https://github.com/ByteDance-Seed/SeedVR)（ByteDance）ベース

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>
