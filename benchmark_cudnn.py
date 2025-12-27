#!/usr/bin/env python3
"""
Benchmark: Compare VAE performance with cuDNN optimizations only
(torch.compile is NOT suitable for this VAE due to dynamic shapes)
"""
import os
import sys
import time
import torch
import numpy as np

sys.path.insert(0, '/app')
os.chdir('/app')

from src.utils.model_registry import DEFAULT_VAE
from src.utils.constants import SEEDVR2_FOLDER_NAME
from src.utils.debug import Debug
from src.core.generation_utils import setup_generation_context, prepare_runner
from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches, postprocess_all_batches
from src.utils.downloads import download_weight

MODEL_DIR = f"/app/models/{SEEDVR2_FOLDER_NAME}"

def benchmark_cudnn(dit_model: str, resolution: int, enable_cudnn_opts: bool = True):
    """Run benchmark with cuDNN optimizations."""
    
    # Set cuDNN options BEFORE any CUDA operations
    if enable_cudnn_opts:
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cuda.matmul.allow_tf32 = True
    else:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_tf32 = False
    
    config_name = "WITH cuDNN opts" if enable_cudnn_opts else "WITHOUT cuDNN opts"
    print(f"\n{'='*60}")
    print(f"Testing: {dit_model.split('_')[2]} @ {resolution}p - {config_name}")
    print(f"  cudnn.benchmark: {torch.backends.cudnn.benchmark}")
    print(f"  cudnn.allow_tf32: {torch.backends.cudnn.allow_tf32}")
    print(f"  cuda.matmul.allow_tf32: {torch.backends.cuda.matmul.allow_tf32}")
    print(f"{'='*60}")
    
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    debug = Debug(enabled=False)
    
    # Create test image
    test_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    frames_tensor = torch.from_numpy(test_img).float() / 255.0
    frames_tensor = frames_tensor.unsqueeze(0)
    
    download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=MODEL_DIR, debug=debug)
    
    device = 'cuda:0'
    ctx = setup_generation_context(
        dit_device=device, vae_device=device,
        dit_offload_device='cpu', vae_offload_device='cpu',
        tensor_offload_device='cpu', debug=debug
    )
    
    runner, cache_ctx = prepare_runner(
        dit_model=dit_model, vae_model=DEFAULT_VAE,
        model_dir=MODEL_DIR, debug=debug, ctx=ctx,
        block_swap_config={'blocks_to_swap': 0},
        encode_tile_size=(512, 512),
        encode_tile_overlap=(64, 64),
        decode_tile_size=(512, 512),
        decode_tile_overlap=(64, 64),
        encode_tiled=True,
        decode_tiled=True,
        dit_cache=False, vae_cache=False
    )
    ctx['cache_context'] = cache_ctx if cache_ctx else {}
    
    timings = {}
    
    # Warmup run
    print("  Warmup run...")
    ctx_warmup = ctx.copy()
    ctx_warmup = encode_all_batches(runner, ctx=ctx_warmup, images=frames_tensor, 
                                   debug=debug, batch_size=1, resolution=480)
    torch.cuda.synchronize()
    del ctx_warmup
    torch.cuda.empty_cache()
    print("  Warmup complete")
    
    # Phase 1: VAE Encoding
    torch.cuda.synchronize()
    t1_start = time.perf_counter()
    ctx = encode_all_batches(runner, ctx=ctx, images=frames_tensor, debug=debug,
                            batch_size=1, resolution=resolution)
    torch.cuda.synchronize()
    timings['encode'] = time.perf_counter() - t1_start
    print(f"  Phase 1 (VAE Encode): {timings['encode']:.2f}s")
    
    # Phase 2: DiT
    torch.cuda.synchronize()
    t2_start = time.perf_counter()
    ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=42)
    torch.cuda.synchronize()
    timings['dit'] = time.perf_counter() - t2_start
    print(f"  Phase 2 (DiT): {timings['dit']:.2f}s")
    
    torch.cuda.empty_cache()
    
    # Phase 3: VAE Decoding
    torch.cuda.synchronize()
    t3_start = time.perf_counter()
    ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
    torch.cuda.synchronize()
    timings['decode'] = time.perf_counter() - t3_start
    print(f"  Phase 3 (VAE Decode): {timings['decode']:.2f}s")
    
    timings['total'] = timings['encode'] + timings['dit'] + timings['decode']
    timings['vae_total'] = timings['encode'] + timings['decode']
    
    del runner, ctx
    torch.cuda.empty_cache()
    
    return timings

def main():
    model = 'seedvr2_ema_3b_fp8_e4m3fn.safetensors'
    resolution = 2160  # 4K
    
    print("\n" + "="*70)
    print("VAE OPTIMIZATION BENCHMARK: cuDNN Optimizations")
    print("="*70)
    print(f"Model: {model}")
    print(f"Resolution: {resolution}p")
    print("\nNote: torch.compile is NOT suitable for this VAE due to dynamic shapes")
    print("      (tiling causes recompilation overhead > 100x slower)")
    
    # Test without cuDNN opts
    results_no_opts = benchmark_cudnn(model, resolution, enable_cudnn_opts=False)
    
    # Test with cuDNN opts
    results_with_opts = benchmark_cudnn(model, resolution, enable_cudnn_opts=True)
    
    # Print comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    
    print(f"\n{'Phase':<20} {'No Opts':>12} {'With Opts':>14} {'Speedup':>10}")
    print("-"*60)
    
    for phase in ['encode', 'dit', 'decode', 'vae_total', 'total']:
        t1 = results_no_opts[phase]
        t2 = results_with_opts[phase]
        speedup = (t1 - t2) / t1 * 100 if t1 > 0 else 0
        speedup_str = f"+{speedup:.1f}%" if speedup > 0 else f"{speedup:.1f}%"
        
        label = phase.replace('_', ' ').title()
        if phase == 'vae_total':
            label = "VAE Total"
        print(f"{label:<20} {t1:>11.2f}s {t2:>13.2f}s {speedup_str:>10}")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    vae_speedup = (results_no_opts['vae_total'] - results_with_opts['vae_total']) / results_no_opts['vae_total'] * 100
    total_speedup = (results_no_opts['total'] - results_with_opts['total']) / results_no_opts['total'] * 100
    print(f"VAE speedup with cuDNN opts: {vae_speedup:.1f}%")
    print(f"Total speedup: {total_speedup:.1f}%")

if __name__ == "__main__":
    main()
