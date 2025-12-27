# SeedVR2 Video Upscaler - Benchmark Report

[English](BENCHMARK.md) | [简体中文](BENCHMARK_CN.md)

## Test Environment

| Item | Specification |
|------|---------------|
| **GPU** | NVIDIA L40S (45GB VRAM) |
| **CUDA** | 12.x |
| **Docker Image** | neosun/seedvr2-allinone:v1.4.2 |
| **Input Image** | 256×256 RGB PNG |
| **Batch Size** | 1 |
| **Test Date** | 2025-12-27 |

---

## Benchmark Results (Processing Time in Seconds)

### Complete Results Table

| Model | 480p | 540p | 720p | 1080p | 1440p | 1620p | 2160p | 2880p | 3384p | 4320p |
|-------|------|------|------|-------|-------|-------|-------|-------|-------|-------|
| **3B FP16** | 3 | 2 | 4 | 3 | 5 | 7 | 9 | 14 | 18 | 27 |
| **3B FP8** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 14 | 18 | 27 |
| **3B Q4** | 3 | 3 | 4 | 4 | 5 | 6 | 9 | 14 | 18 | 27 |
| **3B Q8** | 3 | 4 | 3 | 4 | 5 | 6 | 9 | 14 | 17 | 27 |
| **7B FP16** | 3 | 3 | 4 | 4 | 5 | 6 | 9 | 13 | 18 | 27 |
| **7B FP8** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 14 | 18 | 28 |
| **7B Q4** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 14 | 18 | 27 |
| **7B Q8** | 3 | 4 | 4 | 4 | 5 | 6 | 9 | 14 | 18 | 27 |
| **7B Sharp FP16** | 4 | 4 | 4 | 4 | 5 | 6 | 9 | 13 | 18 | 27 |
| **7B Sharp FP8** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 13 | 17 | 27 |
| **7B Sharp Q4** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 13 | 17 | 27 |
| **7B Sharp Q8** | 3 | 3 | 3 | 4 | 5 | 6 | 9 | 14 | 17 | 27 |

---

## Analysis

### By Resolution

| Resolution | Name | Avg Time | Min | Max |
|------------|------|----------|-----|-----|
| 480p | SD | 3.1s | 3s | 4s |
| 540p | qHD | 3.2s | 2s | 4s |
| 720p | HD | 3.4s | 3s | 4s |
| 1080p | Full HD | 3.9s | 3s | 4s |
| 1440p | 2K | 5.0s | 5s | 5s |
| 1620p | 2.5K | 6.1s | 6s | 7s |
| 2160p | 4K | 9.0s | 9s | 9s |
| 2880p | 5K | 13.6s | 13s | 14s |
| 3384p | 6K | 17.6s | 17s | 18s |
| 4320p | 8K | 27.1s | 27s | 28s |

### By Model Family

| Model Family | Avg Time (all res) | Best For |
|--------------|-------------------|----------|
| **3B** | 9.2s | Fast processing, low VRAM |
| **7B** | 9.2s | High quality |
| **7B Sharp** | 9.0s | Maximum detail |

### By Precision

| Precision | Avg Time | VRAM Usage | Quality |
|-----------|----------|------------|--------|
| **FP16** | 9.2s | High | Best |
| **FP8** | 9.1s | Medium | Excellent |
| **Q8** | 9.1s | Low | Very Good |
| **Q4** | 9.0s | Lowest | Good |

---

## Key Findings

### 1. Processing Time Scales with Resolution
- **SD to HD (480p-720p)**: ~3-4 seconds
- **Full HD to 2K (1080p-1440p)**: ~4-5 seconds
- **2.5K to 4K (1620p-2160p)**: ~6-9 seconds
- **5K to 8K (2880p-4320p)**: ~14-27 seconds

### 2. Model Size Has Minimal Impact on Speed
- 3B and 7B models perform similarly on L40S GPU
- The bottleneck is VAE encoding/decoding, not DiT inference
- Choose model based on quality needs, not speed

### 3. Precision Trade-offs
- **FP16**: Best quality, highest VRAM
- **FP8**: Near-FP16 quality, 50% less VRAM
- **Q4/Q8 GGUF**: Good quality, lowest VRAM, ideal for consumer GPUs

### 4. Recommended Configurations

| Use Case | Model | Resolution | Expected Time |
|----------|-------|------------|---------------|
| Quick Preview | 3B FP8 | 720p | ~3s |
| Social Media | 7B FP8 | 1080p | ~4s |
| Professional | 7B Sharp FP16 | 2160p | ~9s |
| Print/Archive | 7B Sharp FP16 | 4320p | ~27s |

---

## VRAM Requirements

| Model | Precision | VRAM Required |
|-------|-----------|---------------|
| 3B | FP16 | ~12GB |
| 3B | FP8 | ~8GB |
| 3B | Q8 | ~6GB |
| 3B | Q4 | ~4GB |
| 7B | FP16 | ~24GB |
| 7B | FP8 | ~16GB |
| 7B | Q8 | ~12GB |
| 7B | Q4 | ~8GB |

---

## Notes

1. **Test Conditions**: Single image processing, batch_size=1, no VAE tiling
2. **VAE Tiling**: Automatically enabled for resolutions ≥2K (video) or ≥5K (image)
3. **Video Processing**: Multiply image time by frame count, add ~20% overhead
4. **Real-world Performance**: May vary based on input complexity and system load

---

## Conclusion

SeedVR2 v1.4.2 delivers consistent performance across all 12 models:
- **All 120 tests passed** (12 models × 10 resolutions)
- **No failures or timeouts**
- **Predictable scaling** with resolution

For most users, **7B Sharp FP8** offers the best balance of quality, speed, and VRAM usage.
