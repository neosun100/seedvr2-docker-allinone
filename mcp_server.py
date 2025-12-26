"""
SeedVR2 Video Upscaler - MCP Server v1.4.0
Task Queue Edition - Supports queue status and serial processing
"""
import os
import sys
import time
import uuid
import requests
from pathlib import Path
from typing import Optional, Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from fastmcp import FastMCP

mcp = FastMCP("seedvr2-upscaler")

# API base URL (connects to the main server)
API_BASE = os.environ.get('SEEDVR2_API_URL', 'http://localhost:8200')

@mcp.tool()
def get_queue_status() -> Dict[str, Any]:
    """
    Get current task queue status.
    
    Returns:
        dict with queue_length, processing task, pending tasks, and statistics
    """
    try:
        resp = requests.get(f"{API_BASE}/api/queue/status", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def submit_image_task(
    file_path: str,
    resolution: int = 1080,
    dit_model: str = "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
    color_correction: str = "lab",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Submit an image upscaling task to the queue.
    
    Args:
        file_path: Path to input image (PNG, JPG, etc.)
        resolution: Target resolution for short edge (default: 1080)
        dit_model: DiT model to use (default: 3B FP8)
        color_correction: Color correction method: lab, wavelet, hsv, adain, none
        seed: Random seed for reproducibility
    
    Returns:
        dict with task_id, queue_position, and estimated_wait_seconds
    """
    try:
        if not os.path.exists(file_path):
            return {'status': 'error', 'error': f'File not found: {file_path}'}
        
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            data = {
                'resolution': resolution,
                'dit_model': dit_model,
                'color_correction': color_correction,
                'seed': seed,
                'batch_size': 1
            }
            resp = requests.post(f"{API_BASE}/api/process", files=files, data=data, timeout=30)
        
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def submit_video_task(
    file_path: str,
    resolution: int = 1080,
    batch_size: int = 5,
    dit_model: str = "seedvr2_ema_3b_fp8_e4m3fn.safetensors",
    color_correction: str = "lab",
    seed: int = 42
) -> Dict[str, Any]:
    """
    Submit a video upscaling task to the queue.
    
    Args:
        file_path: Path to input video (MP4, AVI, etc.)
        resolution: Target resolution for short edge (default: 1080)
        batch_size: Frames per batch, must be 4n+1 (1, 5, 9, 13...)
        dit_model: DiT model to use
        color_correction: Color correction method
        seed: Random seed
    
    Returns:
        dict with task_id, queue_position, and estimated_wait_seconds
    """
    try:
        if not os.path.exists(file_path):
            return {'status': 'error', 'error': f'File not found: {file_path}'}
        
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            data = {
                'resolution': resolution,
                'batch_size': batch_size,
                'dit_model': dit_model,
                'color_correction': color_correction,
                'seed': seed
            }
            resp = requests.post(f"{API_BASE}/api/process", files=files, data=data, timeout=30)
        
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a specific task.
    
    Args:
        task_id: The task ID returned from submit_image_task or submit_video_task
    
    Returns:
        dict with task status, progress, queue_position (if queued), and result info (if completed)
    """
    try:
        resp = requests.get(f"{API_BASE}/api/status/{task_id}", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def get_task_position(task_id: str) -> Dict[str, Any]:
    """
    Get position of a task in the queue.
    
    Args:
        task_id: The task ID
    
    Returns:
        dict with position and estimated_wait time
    """
    try:
        resp = requests.get(f"{API_BASE}/api/queue/position/{task_id}", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def wait_for_task(task_id: str, timeout: int = 600, poll_interval: int = 5) -> Dict[str, Any]:
    """
    Wait for a task to complete (blocking).
    
    Args:
        task_id: The task ID to wait for
        timeout: Maximum wait time in seconds (default: 600)
        poll_interval: Polling interval in seconds (default: 5)
    
    Returns:
        dict with final task status and result info
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(f"{API_BASE}/api/status/{task_id}", timeout=10)
            result = resp.json()
            
            status = result.get('status')
            if status in ['completed', 'failed']:
                return result
            
            time.sleep(poll_interval)
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    return {'status': 'timeout', 'error': f'Task did not complete within {timeout} seconds'}

@mcp.tool()
def get_queue_history(limit: int = 20) -> Dict[str, Any]:
    """
    Get history of completed tasks.
    
    Args:
        limit: Maximum number of tasks to return (default: 20)
    
    Returns:
        dict with list of completed tasks
    """
    try:
        resp = requests.get(f"{API_BASE}/api/queue/history", params={'limit': limit}, timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def get_gpu_status() -> Dict[str, Any]:
    """
    Get current GPU status and memory usage.
    
    Returns:
        dict with GPU info, VRAM usage, and processing status
    """
    try:
        resp = requests.get(f"{API_BASE}/api/gpu/status", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def release_gpu_memory() -> Dict[str, Any]:
    """
    Release GPU memory.
    
    Returns:
        dict with status
    """
    try:
        resp = requests.post(f"{API_BASE}/api/gpu/offload", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def list_available_models() -> Dict[str, Any]:
    """
    List available DiT models for upscaling.
    
    Returns:
        dict with list of models and default model
    """
    try:
        resp = requests.get(f"{API_BASE}/api/models", timeout=10)
        return resp.json()
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

if __name__ == "__main__":
    mcp.run()
