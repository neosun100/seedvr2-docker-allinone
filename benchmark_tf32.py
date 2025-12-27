#!/usr/bin/env python3
"""
Benchmark: Test TF32 optimization only (without cudnn.benchmark)
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
from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches
from src.utils.downloads import download_weight

MODEL_DIR = f"/app/models/{SEEDVR2_FOLDER_NAME}"

def benchmark(dit_model: str, resolution: int, config_name: str):
    """Run benchmark."""
    print(f"\n{'='*60}")
    print(f"Testing: {config_name}")
    print(f"  cudnn.benchmark: {torch.backends.cudnn.benchmark}")
    print(f"  cudnn.allow_tf32: {torch.backends.cudnn.allow_tf32}")
    print(f"  cuda.matmul.allow_tf32: {torch.backends.cuda.matmul.allow_tf32}")
    print(f"{'='*60}")
    
    torch.cuda.empty_cache()
    debug = Debug(enabled=False)
    
    test_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    frames_tensor = torch.from_numpy(test_img).float() / 255.0
    frames_tensor = frames_tensor.unsqueeze(0)
    
    download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=MODEL_DIR, debug=debug)
    
    ctx = setup_generation_context(
        dit_device='cuda:0', vae_device='cuda:0',
        dit_offload_device='cpu', vae_offload_device='cpu',
        tensor_offload_device='cpu', debug=debug
    )
    
    runner, cache_ctx = prepare_runner(
        dit_model=dit_model, vae_model=DEFAULT_VAE,
        model_dir=MODEL_DIR, debug=debug, ctx=ctx,
        block_swap_config={'blocks_to_swap': 0},
        encode_tile_size=(512, 512), encode_tile_overlap=(64, 64),
        decode_tile_size=(512, 512), decode_tile_overlap=(64, 64),
        encode_tiled=True, decode_tiled=True,
        dit_cache=False, vae_cache=False
    )
    ctx['cache_context'] = cache_ctx if cache_ctx else {}
    
    # Warmup
    ctx_warmup = ctx.copy()
    ctx_warmup = encode_all_batches(runner, ctx=ctx_warmup, images=frames_tensor, 
                                   debug=debug, batch_size=1, resolution=480)
    torch.cuda.synchronize()
    del ctx_warmup
    torch.cuda.empty_cache()
    
    timings = {}
    
    # Phase 1
    torch.cuda.synchronize()
    t1 = time.perf_counter()
    ctx = encode_all_batches(runner, ctx=ctx, images=frames_tensor, debug=debug,
                            batch_size=1, resolution=resolution)
    torch.cuda.synchronize()
    timings['encode'] = time.perf_counter() - t1
    
    # Phase 2
    torch.cuda.synchronize()
    t2 = time.perf_counter()
    ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=42)
    torch.cuda.synchronize()
    timings['dit'] = time.perf_counter() - t2
    
    torch.cuda.empty_cache()
    
    # Phase 3
    torch.cuda.synchronize()
    t3 = time.perf_counter()
    ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
    torch.cuda.synchronize()
    timings['decode'] = time.perf_counter() - t3
    
    timings['vae'] = timings['encode'] + timings['decode']
    timings['total'] = timings['encode'] + timings['dit'] + timings['decode']
    
    print(f"  Encode: {timings['encode']:.2f}s | DiT: {timings['dit']:.2f}s | Decode: {timings['decode']:.2f}s")
    print(f"  VAE Total: {timings['vae']:.2f}s | Total: {timings['total']:.2f}s")
    
    del runner, ctx
    torch.cuda.empty_cache()
    return timings

def main():
    model = 'seedvr2_ema_3b_fp8_e4m3fn.safetensors'
    resolution = 2160
    
    print("\n" + "="*70)
    print("VAE OPTIMIZATION BENCHMARK: TF32 vs FP32")
    print("="*70)
    
    results = {}
    
    # Config 1: All disabled (baseline)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    results['baseline'] = benchmark(model, resolution, "Baseline (FP32)")
    
    # Config 2: TF32 only
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cuda.matmul.allow_tf32 = True
    results['tf32'] = benchmark(model, resolution, "TF32 enabled")
    
    # Config 3: cudnn.benchmark only
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    results['benchmark'] = benchmark(model, resolution, "cudnn.benchmark only")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'Config':<25} {'Encode':>8} {'DiT':>8} {'Decode':>8} {'Total':>8}")
    print("-"*70)
    
    baseline = results['baseline']['total']
    for name, t in results.items():
        speedup = (baseline - t['total']) / baseline * 100
        sp_str = f"({speedup:+.0f}%)" if name != 'baseline' else ""
        print(f"{name:<25} {t['encode']:>7.2f}s {t['dit']:>7.2f}s {t['decode']:>7.2f}s {t['total']:>7.2f}s {sp_str}")

if __name__ == "__main__":
    main()
