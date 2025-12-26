"""
SeedVR2 Video Upscaler - MCP Server
Model Context Protocol interface for programmatic access
"""
import os
import sys
import time
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

# Setup path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("seedvr2-upscaler")

# Shared state
_gpu_manager = None
_last_used = 0
GPU_IDLE_TIMEOUT = int(os.environ.get('GPU_IDLE_TIMEOUT', 600))

def get_gpu_manager():
    """Lazy initialization of GPU manager"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = {
            'runner': None,
            'model_loaded': False,
            'last_used': 0
        }
    return _gpu_manager

@mcp.tool()
def upscale_image(
    file_path: str,
    resolution: int = 1080,
    dit_model: str = "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
    color_correction: str = "lab",
    seed: int = 42,
    blocks_to_swap: int = 0
) -> Dict[str, Any]:
    """
    Upscale a single image using SeedVR2.
    
    Args:
        file_path: Path to input image (PNG, JPG, etc.)
        resolution: Target resolution for short edge (default: 1080)
        dit_model: DiT model to use (default: 3B FP8)
        color_correction: Color correction method: lab, wavelet, hsv, adain, none
        seed: Random seed for reproducibility
        blocks_to_swap: BlockSwap blocks for VRAM optimization (0-32)
    
    Returns:
        dict with status, output_path, and processing info
    """
    import torch
    import cv2
    import numpy as np
    
    try:
        if not os.path.exists(file_path):
            return {'status': 'error', 'error': f'File not found: {file_path}'}
        
        # Import processing modules
        from src.core.generation_utils import setup_generation_context, prepare_runner
        from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches, postprocess_all_batches
        from src.utils.downloads import download_weight
        from src.utils.model_registry import DEFAULT_VAE
        from src.utils.constants import SEEDVR2_FOLDER_NAME
        from src.utils.debug import Debug
        
        debug = Debug(enabled=False)
        model_dir = os.environ.get('MODEL_DIR', f'./models/{SEEDVR2_FOLDER_NAME}')
        
        # Download models
        download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=model_dir, debug=debug)
        
        # Load image
        frame = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if frame is None:
            return {'status': 'error', 'error': 'Cannot read image file'}
        
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        frame = frame.astype(np.float32) / 255.0
        frames_tensor = torch.from_numpy(frame[None, ...]).to(torch.float16)
        
        # Setup
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        ctx = setup_generation_context(
            dit_device=device, vae_device=device,
            dit_offload_device='cpu', vae_offload_device='cpu',
            tensor_offload_device='cpu', debug=debug
        )
        
        runner, cache_ctx = prepare_runner(
            dit_model=dit_model, vae_model=DEFAULT_VAE,
            model_dir=model_dir, debug=debug, ctx=ctx,
            block_swap_config={'blocks_to_swap': blocks_to_swap}
        )
        ctx['cache_context'] = cache_ctx
        
        gm = get_gpu_manager()
        gm['runner'] = runner
        gm['last_used'] = time.time()
        gm['model_loaded'] = True
        
        # Process
        start_time = time.time()
        
        ctx = encode_all_batches(runner, ctx=ctx, images=frames_tensor, debug=debug,
                                 batch_size=1, resolution=resolution)
        ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=seed)
        ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
        ctx = postprocess_all_batches(ctx=ctx, debug=debug, color_correction=color_correction)
        
        # Fix: Convert BFloat16 to Float32 before numpy conversion
        result_tensor = ctx['final_video']
        if result_tensor.dtype == torch.bfloat16:
            result_tensor = result_tensor.to(torch.float32)
        result = result_tensor.cpu().numpy()
        
        # Save
        output_dir = os.environ.get('OUTPUT_FOLDER', './outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        input_name = Path(file_path).stem
        output_path = os.path.join(output_dir, f"{input_name}_upscaled.png")
        
        frame_out = (result[0] * 255).astype(np.uint8)
        if frame_out.shape[2] == 4:
            frame_bgr = cv2.cvtColor(frame_out, cv2.COLOR_RGBA2BGRA)
        else:
            frame_bgr = cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, frame_bgr)
        
        processing_time = time.time() - start_time
        
        return {
            'status': 'success',
            'output_path': output_path,
            'input_shape': list(frame.shape),
            'output_shape': list(result[0].shape),
            'processing_time': round(processing_time, 2),
            'model_used': dit_model
        }
        
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@mcp.tool()
def upscale_video(
    file_path: str,
    resolution: int = 1080,
    batch_size: int = 5,
    dit_model: str = "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
    color_correction: str = "lab",
    seed: int = 42,
    blocks_to_swap: int = 0,
    temporal_overlap: int = 0
) -> Dict[str, Any]:
    """
    Upscale a video using SeedVR2.
    
    Args:
        file_path: Path to input video (MP4, AVI, etc.)
        resolution: Target resolution for short edge (default: 1080)
        batch_size: Frames per batch, must be 4n+1 (1, 5, 9, 13...)
        dit_model: DiT model to use
        color_correction: Color correction method
        seed: Random seed
        blocks_to_swap: BlockSwap blocks for VRAM optimization
        temporal_overlap: Overlap frames between batches for smooth transitions
    
    Returns:
        dict with status, output_path, and processing info
    """
    import torch
    import cv2
    import numpy as np
    
    try:
        if not os.path.exists(file_path):
            return {'status': 'error', 'error': f'File not found: {file_path}'}
        
        from src.core.generation_utils import setup_generation_context, prepare_runner
        from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches, postprocess_all_batches
        from src.utils.downloads import download_weight
        from src.utils.model_registry import DEFAULT_VAE
        from src.utils.constants import SEEDVR2_FOLDER_NAME
        from src.utils.debug import Debug
        
        debug = Debug(enabled=False)
        model_dir = os.environ.get('MODEL_DIR', f'./models/{SEEDVR2_FOLDER_NAME}')
        
        download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=model_dir, debug=debug)
        
        # Load video
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return {'status': 'error', 'error': 'Cannot open video file'}
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            frames.append(frame)
        cap.release()
        
        frames_tensor = torch.from_numpy(np.stack(frames)).to(torch.float16)
        
        # Setup
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        ctx = setup_generation_context(
            dit_device=device, vae_device=device,
            dit_offload_device='cpu', vae_offload_device='cpu',
            tensor_offload_device='cpu', debug=debug
        )
        
        runner, cache_ctx = prepare_runner(
            dit_model=dit_model, vae_model=DEFAULT_VAE,
            model_dir=model_dir, debug=debug, ctx=ctx,
            block_swap_config={'blocks_to_swap': blocks_to_swap}
        )
        ctx['cache_context'] = cache_ctx
        
        gm = get_gpu_manager()
        gm['runner'] = runner
        gm['last_used'] = time.time()
        gm['model_loaded'] = True
        
        # Process
        start_time = time.time()
        
        ctx = encode_all_batches(runner, ctx=ctx, images=frames_tensor, debug=debug,
                                 batch_size=batch_size, resolution=resolution,
                                 temporal_overlap=temporal_overlap)
        ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=seed)
        ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
        ctx = postprocess_all_batches(ctx=ctx, debug=debug, color_correction=color_correction,
                                      temporal_overlap=temporal_overlap, batch_size=batch_size)
        
        # Fix: Convert BFloat16 to Float32 before numpy conversion
        result_tensor = ctx['final_video']
        if result_tensor.dtype == torch.bfloat16:
            result_tensor = result_tensor.to(torch.float32)
        result = result_tensor.cpu().numpy()
        
        # Save
        output_dir = os.environ.get('OUTPUT_FOLDER', './outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        input_name = Path(file_path).stem
        output_path = os.path.join(output_dir, f"{input_name}_upscaled.mp4")
        
        h, w = result.shape[1:3]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        for frame in result:
            frame_bgr = cv2.cvtColor((frame * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
            writer.write(frame_bgr)
        writer.release()
        
        processing_time = time.time() - start_time
        
        return {
            'status': 'success',
            'output_path': output_path,
            'input_frames': total_frames,
            'output_frames': result.shape[0],
            'fps': fps,
            'processing_time': round(processing_time, 2),
            'fps_achieved': round(result.shape[0] / processing_time, 2)
        }
        
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@mcp.tool()
def get_gpu_status() -> Dict[str, Any]:
    """
    Get current GPU status and memory usage.
    
    Returns:
        dict with GPU info, VRAM usage, and model status
    """
    import torch
    
    gm = get_gpu_manager()
    
    status = {
        'cuda_available': torch.cuda.is_available(),
        'model_loaded': gm.get('model_loaded', False),
        'idle_seconds': int(time.time() - gm.get('last_used', 0)) if gm.get('last_used') else 0
    }
    
    if torch.cuda.is_available():
        status['gpu_name'] = torch.cuda.get_device_name(0)
        status['vram_used_mb'] = torch.cuda.memory_allocated(0) // (1024*1024)
        status['vram_reserved_mb'] = torch.cuda.memory_reserved(0) // (1024*1024)
        status['vram_total_mb'] = torch.cuda.get_device_properties(0).total_memory // (1024*1024)
    
    return status

@mcp.tool()
def release_gpu_memory() -> Dict[str, Any]:
    """
    Release GPU memory by unloading models.
    
    Returns:
        dict with status and freed memory info
    """
    import torch
    
    gm = get_gpu_manager()
    
    before_vram = 0
    if torch.cuda.is_available():
        before_vram = torch.cuda.memory_allocated(0) // (1024*1024)
    
    if gm.get('runner'):
        del gm['runner']
        gm['runner'] = None
    
    gm['model_loaded'] = False
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        after_vram = torch.cuda.memory_allocated(0) // (1024*1024)
    else:
        after_vram = 0
    
    return {
        'status': 'success',
        'vram_before_mb': before_vram,
        'vram_after_mb': after_vram,
        'freed_mb': before_vram - after_vram
    }

@mcp.tool()
def list_available_models() -> Dict[str, Any]:
    """
    List available DiT models for upscaling.
    
    Returns:
        dict with list of models and default model
    """
    from src.utils.model_registry import get_available_dit_models, DEFAULT_DIT
    
    models = get_available_dit_models()
    
    return {
        'models': models,
        'default': DEFAULT_DIT,
        'categories': {
            '3b_models': [m for m in models if '3b' in m.lower()],
            '7b_models': [m for m in models if '7b' in m.lower()],
            'gguf_models': [m for m in models if m.endswith('.gguf')]
        }
    }

if __name__ == "__main__":
    mcp.run()
