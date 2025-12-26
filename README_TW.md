[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# 🎬 SeedVR2 影片超解析度 - Docker 一體化版

**🚀 一鍵部署 AI 影片/圖片超解析度 Web 服務**

</div>

---

## 🚀 快速開始

```bash
docker run -d --gpus all -p 8200:8200 neosun/seedvr2-allinone:latest
```

然後開啟：**http://localhost:8200**

---

## 🐳 Docker 映像檔

| 映像檔標籤 | 包含模型 | 大小 |
|------------|----------|------|
| `v1.3.0-12models-16k-vaetiling-h264-memfix-bilingual` | 全部 12 個 | ~103GB |
| `v1.3.0-7b-sharp-fp16-only-16k-vaetiling-h264-bilingual` | 1× 7B Sharp FP16 | ~15GB |

---

<div align="center">

**Made with ❤️ by [NeoSun](https://github.com/neosun100)**

</div>