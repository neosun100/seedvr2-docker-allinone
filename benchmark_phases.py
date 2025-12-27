#!/usr/bin/env python3
"""
Benchmark script to measure processing time for each phase:
- Phase 1: VAE Encoding
- Phase 2: DiT Upscaling  
- Phase 3: VAE Decoding
- Phase 4: Post-processing
"""
import os
import sys
import time
import torch
import numpy as np

# Add src to path
sys.path.insert(0, '/app')
os.chdir('/app')

from src.utils.model_registry import DEFAULT_VAE
from src.utils.constants import SEEDVR2_FOLDER_NAME
from src.utils.debug import Debug
from src.core.generation_utils import setup_generation_context, prepare_runner
from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches, postprocess_all_batches
from src.utils.downloads import download_weight

MODEL_DIR = f"/app/models/{SEEDVR2_FOLDER_NAME}"

def benchmark_phases(dit_model: str, resolution: int = 2160):
    """Run benchmark and measure each phase."""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {dit_model} @ {resolution}p")
    print(f"{'='*60}\n")
    
    # Clear GPU memory first
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    debug = Debug(enabled=False)  # Disable verbose logging
    
    # Create test image (256x256)
    test_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    frames_tensor = torch.from_numpy(test_img).float() / 255.0
    frames_tensor = frames_tensor.unsqueeze(0)  # [1, H, W, C]
    
    # Download model if needed
    download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=MODEL_DIR, debug=debug)
    
    # Setup context
    device = 'cuda:0'
    ctx = setup_generation_context(
        dit_device=device, vae_device=device,
        dit_offload_device='cpu', vae_offload_device='cpu',
        tensor_offload_device='cpu', debug=debug
    )
    
    # Prepare runner with VAE tiling enabled for high res
    runner, cache_ctx = prepare_runner(
        dit_model=dit_model, vae_model=DEFAULT_VAE,
        model_dir=MODEL_DIR, debug=debug, ctx=ctx,
        block_swap_config={'blocks_to_swap': 0},
        encode_tile_size=(512, 512),
        encode_tile_overlap=(64, 64),
        decode_tile_size=(512, 512),
        decode_tile_overlap=(64, 64),
        dit_cache=False, vae_cache=False
    )
    ctx['cache_context'] = cache_ctx if cache_ctx else {}
    
    timings = {}
    
    # Phase 1: VAE Encoding
    torch.cuda.synchronize()
    t1_start = time.perf_counter()
    ctx = encode_all_batches(
        runner, ctx=ctx, images=frames_tensor, debug=debug,
        batch_size=1, resolution=resolution
    )
    torch.cuda.synchronize()
    t1_end = time.perf_counter()
    timings['phase1_encode'] = t1_end - t1_start
    print(f"  Phase 1 (VAE Encode): {timings['phase1_encode']:.2f}s")
    
    # Phase 2: DiT Upscaling
    torch.cuda.synchronize()
    t2_start = time.perf_counter()
    ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=42)
    torch.cuda.synchronize()
    t2_end = time.perf_counter()
    timings['phase2_dit'] = t2_end - t2_start
    print(f"  Phase 2 (DiT Upscale): {timings['phase2_dit']:.2f}s")
    
    # Clear cache between phases
    torch.cuda.empty_cache()
    
    # Phase 3: VAE Decoding
    torch.cuda.synchronize()
    t3_start = time.perf_counter()
    ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
    torch.cuda.synchronize()
    t3_end = time.perf_counter()
    timings['phase3_decode'] = t3_end - t3_start
    print(f"  Phase 3 (VAE Decode): {timings['phase3_decode']:.2f}s")
    
    # Phase 4: Post-processing
    torch.cuda.synchronize()
    t4_start = time.perf_counter()
    ctx = postprocess_all_batches(runner, ctx=ctx, debug=debug, color_correction='none')
    torch.cuda.synchronize()
    t4_end = time.perf_counter()
    timings['phase4_postprocess'] = t4_end - t4_start
    print(f"  Phase 4 (Post-process): {timings['phase4_postprocess']:.2f}s")
    
    total = sum(timings.values())
    timings['total'] = total
    
    # Cleanup
    del runner, ctx
    torch.cuda.empty_cache()
    
    return timings

def print_results(results: dict, resolution: int):
    """Print formatted results."""
    print(f"\n{'='*80}")
    print(f"PHASE TIMING BREAKDOWN @ {resolution}p")
    print(f"{'='*80}")
    print(f"{'Model':<20} {'Encode':>10} {'DiT':>10} {'Decode':>10} {'Post':>10} {'Total':>10}")
    print(f"{'─'*80}")
    
    for model, t in results.items():
        short = model.replace('seedvr2_ema_', '').replace('.safetensors', '')
        total = t['total']
        print(f"{short:<20} {t['phase1_encode']:>9.2f}s {t['phase2_dit']:>9.2f}s {t['phase3_decode']:>9.2f}s {t['phase4_postprocess']:>9.2f}s {total:>9.2f}s")
    
    print(f"\n{'='*80}")
    print("PERCENTAGE BREAKDOWN")
    print(f"{'='*80}")
    print(f"{'Model':<20} {'Encode':>10} {'DiT':>10} {'Decode':>10} {'Post':>10}")
    print(f"{'─'*80}")
    
    for model, t in results.items():
        short = model.replace('seedvr2_ema_', '').replace('.safetensors', '')
        total = t['total']
        print(f"{short:<20} {t['phase1_encode']/total*100:>9.1f}% {t['phase2_dit']/total*100:>9.1f}% {t['phase3_decode']/total*100:>9.1f}% {t['phase4_postprocess']/total*100:>9.1f}%")

if __name__ == "__main__":
    resolution = 4320  # 8K
    
    models = [
        'seedvr2_ema_3b_fp8_e4m3fn.safetensors',
        'seedvr2_ema_7b_fp8_e4m3fn.safetensors',
        'seedvr2_ema_7b_sharp_fp8_e4m3fn.safetensors',
    ]
    
    results = {}
    for model in models:
        try:
            results[model] = benchmark_phases(model, resolution=resolution)
        except Exception as e:
            print(f"Error testing {model}: {e}")
            import traceback
            traceback.print_exc()
    
    if results:
        print_results(results, resolution)
