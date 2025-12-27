#!/usr/bin/env python3
"""
Benchmark: Compare VAE performance with and without torch.compile + cuDNN optimizations
"""
import os
import sys
import time
import torch

# Enable cuDNN optimizations
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.matmul.allow_tf32 = True

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

def benchmark_with_config(dit_model: str, resolution: int, use_compile: bool = False):
    """Run benchmark with specific configuration."""
    config_name = "WITH torch.compile" if use_compile else "WITHOUT torch.compile"
    print(f"\n{'='*60}")
    print(f"Testing: {dit_model.split('_')[2]} @ {resolution}p - {config_name}")
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
    
    # torch.compile configuration
    compile_args = None
    if use_compile:
        compile_args = {
            'backend': 'inductor',
            'mode': 'reduce-overhead',  # Optimized for inference
            'fullgraph': False,
            'dynamic': False
        }
    
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
        dit_cache=False, vae_cache=False,
        torch_compile_args_vae=compile_args
    )
    ctx['cache_context'] = cache_ctx if cache_ctx else {}
    
    timings = {}
    
    # Warmup run (important for torch.compile)
    if use_compile:
        print("  Warmup run for torch.compile...")
        try:
            ctx_warmup = ctx.copy()
            ctx_warmup = encode_all_batches(runner, ctx=ctx_warmup, images=frames_tensor, 
                                           debug=debug, batch_size=1, resolution=480)
            torch.cuda.synchronize()
            print("  Warmup complete")
        except Exception as e:
            print(f"  Warmup failed: {e}")
    
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
    
    # Phase 4: Post-process
    torch.cuda.synchronize()
    t4_start = time.perf_counter()
    ctx = postprocess_all_batches(runner, ctx=ctx, debug=debug, color_correction='none')
    torch.cuda.synchronize()
    timings['post'] = time.perf_counter() - t4_start
    print(f"  Phase 4 (Post): {timings['post']:.2f}s")
    
    timings['total'] = sum(timings.values())
    timings['vae_total'] = timings['encode'] + timings['decode']
    
    del runner, ctx
    torch.cuda.empty_cache()
    
    return timings

def main():
    model = 'seedvr2_ema_3b_fp8_e4m3fn.safetensors'
    resolution = 2160  # 4K - should work without OOM with tiling
    
    print("\n" + "="*70)
    print("VAE OPTIMIZATION BENCHMARK: torch.compile + cuDNN")
    print("="*70)
    print(f"Model: {model}")
    print(f"Resolution: {resolution}p")
    print(f"cuDNN benchmark: {torch.backends.cudnn.benchmark}")
    print(f"cuDNN TF32: {torch.backends.cudnn.allow_tf32}")
    print(f"CUDA TF32: {torch.backends.cuda.matmul.allow_tf32}")
    
    # Test without compile
    try:
        results_no_compile = benchmark_with_config(model, resolution, use_compile=False)
    except Exception as e:
        print(f"Error without compile: {e}")
        results_no_compile = None
    
    # Test with compile
    try:
        results_with_compile = benchmark_with_config(model, resolution, use_compile=True)
    except Exception as e:
        print(f"Error with compile: {e}")
        import traceback
        traceback.print_exc()
        results_with_compile = None
    
    # Print comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70)
    
    if results_no_compile and results_with_compile:
        print(f"\n{'Phase':<20} {'No Compile':>12} {'With Compile':>14} {'Speedup':>10}")
        print("-"*60)
        
        for phase in ['encode', 'dit', 'decode', 'post', 'vae_total', 'total']:
            t1 = results_no_compile[phase]
            t2 = results_with_compile[phase]
            speedup = (t1 - t2) / t1 * 100 if t1 > 0 else 0
            speedup_str = f"+{speedup:.1f}%" if speedup > 0 else f"{speedup:.1f}%"
            
            label = phase.replace('_', ' ').title()
            if phase == 'vae_total':
                label = "VAE Total"
            print(f"{label:<20} {t1:>11.2f}s {t2:>13.2f}s {speedup_str:>10}")
    else:
        print("Could not complete comparison - one or both tests failed")
        if results_no_compile:
            print(f"\nWithout compile results: {results_no_compile}")
        if results_with_compile:
            print(f"\nWith compile results: {results_with_compile}")

if __name__ == "__main__":
    main()
