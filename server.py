"""
SeedVR2 Video Upscaler - Web Server v1.4.0
Task Queue Edition - Serial GPU processing with queue management
"""
import os
import sys
import uuid
import time
import json
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from collections import deque

# Setup path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.utils import secure_filename

# Import SeedVR2 components
from src.utils.model_registry import get_available_dit_models, DEFAULT_DIT, DEFAULT_VAE
from src.utils.constants import SEEDVR2_FOLDER_NAME
from src.utils.debug import Debug

app = Flask(__name__)
CORS(app)

# Swagger config
app.config['SWAGGER'] = {
    'title': 'SeedVR2 Video Upscaler API',
    'version': '1.4.0',
    'description': 'High-quality video and image upscaling API with Task Queue'
}
swagger = Swagger(app)

# Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/app/uploads')
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', '/app/outputs')
MODEL_DIR = os.environ.get('MODEL_DIR', f'/app/models/{SEEDVR2_FOLDER_NAME}')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 500)) * 1024 * 1024
GPU_IDLE_TIMEOUT = int(os.environ.get('GPU_IDLE_TIMEOUT', 600))
MAX_HISTORY_SIZE = int(os.environ.get('MAX_HISTORY_SIZE', 100))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ============================================================================
# Task Queue System - v1.4.0
# ============================================================================

class TaskQueue:
    """Thread-safe task queue with serial GPU processing"""
    
    def __init__(self, max_history: int = 100):
        self.queue = queue.Queue()  # FIFO queue for pending tasks
        self.tasks: Dict[str, Dict[str, Any]] = {}  # All task info
        self.lock = threading.Lock()
        self.current_task_id: Optional[str] = None
        self.completed_history: deque = deque(maxlen=max_history)
        self.total_completed = 0
        self.total_failed = 0
        self.worker_thread: Optional[threading.Thread] = None
        self.running = True
        self.avg_process_time = 30.0  # Initial estimate in seconds
        
    def start_worker(self):
        """Start the background worker thread"""
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print("[Queue] Worker thread started - Serial GPU processing enabled")
        
    def _worker_loop(self):
        """Main worker loop - processes tasks one by one"""
        while self.running:
            try:
                # Wait for next task (with timeout to check running flag)
                try:
                    task_id = self.queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                with self.lock:
                    if task_id not in self.tasks:
                        continue
                    self.current_task_id = task_id
                    self.tasks[task_id]['status'] = 'processing'
                    self.tasks[task_id]['started_at'] = datetime.now().isoformat()
                    
                print(f"[Queue] Processing task {task_id}")
                
                # Process the task
                task = self.tasks[task_id]
                self._process_task(task_id, task['input_path'], task['params'])
                
                with self.lock:
                    self.current_task_id = None
                    
                self.queue.task_done()
                
            except Exception as e:
                print(f"[Queue] Worker error: {e}")
                with self.lock:
                    if self.current_task_id:
                        self.tasks[self.current_task_id]['status'] = 'failed'
                        self.tasks[self.current_task_id]['error'] = str(e)
                    self.current_task_id = None
                    
    def _process_task(self, task_id: str, input_path: str, params: Dict[str, Any]):
        """Process a single task - GPU exclusive"""
        import torch
        import cv2
        import numpy as np
        
        try:
            with self.lock:
                self.tasks[task_id]['progress'] = 0
                self.tasks[task_id]['start_time'] = time.time()
            
            # Import processing modules
            from src.core.generation_utils import setup_generation_context, prepare_runner
            from src.core.generation_phases import encode_all_batches, upscale_all_batches, decode_all_batches, postprocess_all_batches
            from src.utils.downloads import download_weight
            
            debug = Debug(enabled=params.get('debug', False))
            dit_model = params.get('dit_model', DEFAULT_DIT)
            download_weight(dit_model=dit_model, vae_model=DEFAULT_VAE, model_dir=MODEL_DIR, debug=debug)
            
            # Load input
            ext = Path(input_path).suffix.lower()
            is_video = ext in {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
            
            if is_video:
                cap = cv2.VideoCapture(input_path)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                frames = []
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    frames.append(frame)
                cap.release()
                frames_tensor = torch.from_numpy(np.stack(frames)).to(torch.float16)
            else:
                frame = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
                if frame.shape[2] == 4:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = frame.astype(np.float32) / 255.0
                frames_tensor = torch.from_numpy(frame[None, ...]).to(torch.float16)
                fps = 30.0
            
            self._update_progress(task_id, 10)
            
            # Setup context
            device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
            ctx = setup_generation_context(
                dit_device=device, vae_device=device,
                dit_offload_device='cpu', vae_offload_device='cpu',
                tensor_offload_device='cpu', debug=debug
            )
            
            # VAE quality settings
            vae_quality = params.get('vae_quality', 'high')
            vae_quality_map = {
                'low': ((512, 512), (64, 64)),
                'medium': ((768, 768), (96, 96)),
                'high': ((1024, 1024), (128, 128))
            }
            tile_size, tile_overlap = vae_quality_map.get(vae_quality, vae_quality_map['high'])
            
            runner, cache_ctx = prepare_runner(
                dit_model=dit_model, vae_model=DEFAULT_VAE,
                model_dir=MODEL_DIR, debug=debug, ctx=ctx,
                block_swap_config={'blocks_to_swap': params.get('blocks_to_swap', 0)},
                encode_tiled=params.get('encode_tiled', False),
                encode_tile_size=tile_size,
                encode_tile_overlap=tile_overlap,
                decode_tiled=params.get('decode_tiled', False),
                decode_tile_size=tile_size,
                decode_tile_overlap=tile_overlap,
                dit_cache=False, vae_cache=False
            )
            ctx['cache_context'] = cache_ctx if cache_ctx else {}
            
            self._update_progress(task_id, 30)
            
            # Process
            resolution = params.get('resolution', 1080)
            batch_size = params.get('batch_size', 5)
            
            ctx = encode_all_batches(runner, ctx=ctx, images=frames_tensor, debug=debug,
                                     batch_size=batch_size, resolution=resolution)
            self._update_progress(task_id, 50)
            
            ctx = upscale_all_batches(runner, ctx=ctx, debug=debug, seed=params.get('seed', 42))
            torch.cuda.empty_cache()
            self._update_progress(task_id, 70)
            
            ctx = decode_all_batches(runner, ctx=ctx, debug=debug)
            self._update_progress(task_id, 85)
            
            ctx = postprocess_all_batches(ctx=ctx, debug=debug,
                                          color_correction=params.get('color_correction', 'lab'))
            
            # Convert result
            result_tensor = ctx['final_video']
            if result_tensor.dtype == torch.bfloat16:
                result_tensor = result_tensor.to(torch.float32)
            result = result_tensor.cpu().numpy()
            
            # Save output
            original_name = Path(input_path).stem.split('_', 1)[-1]
            model_short = dit_model.replace('seedvr2_ema_', '').replace('.safetensors', '').replace('.gguf', '')
            with self.lock:
                start_time = self.tasks[task_id].get('start_time', time.time())
            process_time = int(time.time() - start_time)
            h, w = result.shape[1:3]
            output_res = min(h, w)
            
            color_correction = params.get('color_correction', 'lab')
            seed = params.get('seed', 42)
            encode_tiled = params.get('encode_tiled', False)
            vae_suffix = f"_vae{vae_quality[0].upper()}" if encode_tiled else ""
            output_name = f"{original_name}_{model_short}_{output_res}p_b{batch_size}_c{color_correction}_s{seed}{vae_suffix}_{process_time}s"
            
            if is_video:
                output_path = self._save_video(result, output_name, fps, w, h, input_path)
            else:
                output_path = os.path.join(OUTPUT_FOLDER, f"{output_name}.png")
                frame_out = (result[0] * 255).astype(np.uint8)
                frame_bgr = cv2.cvtColor(frame_out, cv2.COLOR_RGBA2BGRA if frame_out.shape[2] == 4 else cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_path, frame_bgr)
            
            # Mark completed
            with self.lock:
                self.tasks[task_id]['status'] = 'completed'
                self.tasks[task_id]['progress'] = 100
                self.tasks[task_id]['output_path'] = output_path
                self.tasks[task_id]['output_filename'] = Path(output_path).name
                self.tasks[task_id]['output_resolution'] = f"{w}x{h}"
                self.tasks[task_id]['process_time'] = process_time
                self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
                self.total_completed += 1
                self.completed_history.append(task_id)
                # Update average process time
                self.avg_process_time = (self.avg_process_time * 0.8) + (process_time * 0.2)
                
            print(f"[Queue] Task {task_id} completed in {process_time}s")
            
        except Exception as e:
            import traceback
            with self.lock:
                self.tasks[task_id]['status'] = 'failed'
                self.tasks[task_id]['error'] = str(e)
                self.tasks[task_id]['traceback'] = traceback.format_exc()
                self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
                self.total_failed += 1
            print(f"[Queue] Task {task_id} failed: {e}")
        finally:
            # Always cleanup GPU
            try:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass
                
    def _update_progress(self, task_id: str, progress: int):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['progress'] = progress
                
    def _save_video(self, result, output_name, fps, w, h, input_path):
        """Save video with H.264 encoding"""
        import cv2
        import subprocess
        
        temp_path = os.path.join(OUTPUT_FOLDER, f"{output_name}_temp.mp4")
        output_path = os.path.join(OUTPUT_FOLDER, f"{output_name}.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(temp_path, fourcc, fps, (w, h))
        for frame in result:
            frame_bgr = cv2.cvtColor((frame * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
            writer.write(frame_bgr)
        writer.release()
        
        # Check audio
        has_audio = False
        try:
            probe = subprocess.run([
                'ffprobe', '-v', 'error', '-select_streams', 'a',
                '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', input_path
            ], capture_output=True, text=True)
            has_audio = 'audio' in probe.stdout
        except:
            pass
        
        # Convert to H.264
        try:
            if has_audio:
                subprocess.run([
                    'ffmpeg', '-y', '-i', temp_path, '-i', input_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-map', '0:v:0', '-map', '1:a:0?', '-shortest', output_path
                ], check=True, capture_output=True)
            else:
                subprocess.run([
                    'ffmpeg', '-y', '-i', temp_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                    '-pix_fmt', 'yuv420p', output_path
                ], check=True, capture_output=True)
            os.remove(temp_path)
        except:
            if os.path.exists(temp_path):
                os.rename(temp_path, output_path)
        
        return output_path
    
    def submit(self, task_id: str, input_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new task to the queue"""
        with self.lock:
            position = self.queue.qsize() + 1  # +1 for this task
            estimated_wait = int(position * self.avg_process_time)
            
            self.tasks[task_id] = {
                'id': task_id,
                'status': 'queued',
                'progress': 0,
                'input_path': input_path,
                'params': params,
                'created_at': datetime.now().isoformat(),
                'queue_position': position,
                'estimated_wait': estimated_wait
            }
            
        self.queue.put(task_id)
        
        return {
            'task_id': task_id,
            'status': 'queued',
            'queue_position': position,
            'estimated_wait_seconds': estimated_wait
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        with self.lock:
            pending_count = self.queue.qsize()
            processing = self.current_task_id
            
            # Get pending task IDs
            pending_tasks = []
            for tid, task in self.tasks.items():
                if task['status'] == 'queued':
                    pending_tasks.append({
                        'id': tid,
                        'created_at': task['created_at'],
                        'params': {
                            'resolution': task['params'].get('resolution'),
                            'model': task['params'].get('dit_model', '').replace('seedvr2_ema_', '')
                        }
                    })
            
            # Sort by creation time
            pending_tasks.sort(key=lambda x: x['created_at'])
            
            return {
                'queue_length': pending_count,
                'processing': processing,
                'processing_progress': self.tasks[processing]['progress'] if processing and processing in self.tasks else 0,
                'pending_tasks': pending_tasks,
                'total_completed': self.total_completed,
                'total_failed': self.total_failed,
                'avg_process_time': round(self.avg_process_time, 1),
                'estimated_total_wait': int(pending_count * self.avg_process_time)
            }
    
    def get_task_position(self, task_id: str) -> Dict[str, Any]:
        """Get position of a specific task in queue"""
        with self.lock:
            if task_id not in self.tasks:
                return {'error': 'Task not found'}
            
            task = self.tasks[task_id]
            if task['status'] != 'queued':
                return {
                    'task_id': task_id,
                    'status': task['status'],
                    'position': 0,
                    'estimated_wait': 0
                }
            
            # Count position
            position = 0
            for tid, t in self.tasks.items():
                if t['status'] == 'queued' and t['created_at'] < task['created_at']:
                    position += 1
            position += 1  # 1-indexed
            
            # Add 1 if something is processing
            if self.current_task_id:
                position += 1
                
            return {
                'task_id': task_id,
                'status': 'queued',
                'position': position,
                'estimated_wait': int(position * self.avg_process_time)
            }
    
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get completed task history"""
        with self.lock:
            history = []
            for task_id in reversed(list(self.completed_history)[-limit:]):
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    history.append({
                        'id': task_id,
                        'status': task['status'],
                        'created_at': task.get('created_at'),
                        'completed_at': task.get('completed_at'),
                        'process_time': task.get('process_time'),
                        'output_filename': task.get('output_filename'),
                        'output_resolution': task.get('output_resolution')
                    })
            return history
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task info"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id].copy()
                # Add current position if queued
                if task['status'] == 'queued':
                    pos_info = self.get_task_position(task_id)
                    task['queue_position'] = pos_info.get('position', 0)
                    task['estimated_wait'] = pos_info.get('estimated_wait', 0)
                return task
            return None
    
    def shutdown(self):
        """Shutdown the worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)


# Initialize task queue
task_queue = TaskQueue(max_history=MAX_HISTORY_SIZE)


# ============================================================================
# Model Info & GPU Manager (unchanged from v1.3)
# ============================================================================

MODEL_INFO = {
    'ema_vae_fp16.safetensors': {
        'type': 'VAE', 'size': '479MB', 'precision': 'FP16',
        'desc': {'zh-CN': 'VAE编解码器 (必需)', 'en': 'VAE encoder/decoder (required)',
                 'zh-TW': 'VAE編解碼器 (必需)', 'ja': 'VAEエンコーダ/デコーダ (必須)'}
    },
    'seedvr2_ema_3b_fp16.safetensors': {
        'type': 'DiT', 'params': '3B', 'size': '6.4GB', 'precision': 'FP16', 'vram': '~12GB',
        'desc': {'zh-CN': '3B参数 FP16 - 最高质量，需要较大显存', 'en': '3B params FP16 - Best quality, requires more VRAM',
                 'zh-TW': '3B參數 FP16 - 最高品質，需要較大顯存', 'ja': '3Bパラメータ FP16 - 最高品質、大容量VRAM必要'}
    },
    'seedvr2_ema_3b_fp8_e4m3fn.safetensors': {
        'type': 'DiT', 'params': '3B', 'size': '3.2GB', 'precision': 'FP8', 'vram': '~8GB',
        'desc': {'zh-CN': '3B参数 FP8 - 质量与速度平衡 ⭐推荐', 'en': '3B params FP8 - Balanced quality & speed ⭐Recommended',
                 'zh-TW': '3B參數 FP8 - 品質與速度平衡 ⭐推薦', 'ja': '3Bパラメータ FP8 - 品質と速度のバランス ⭐推奨'}
    },
    'seedvr2_ema_3b-Q4_K_M.gguf': {
        'type': 'DiT', 'params': '3B', 'size': '1.9GB', 'precision': 'Q4', 'vram': '~4GB',
        'desc': {'zh-CN': '3B参数 4-bit量化 - 低显存设备', 'en': '3B params 4-bit quantized - Low VRAM devices',
                 'zh-TW': '3B參數 4-bit量化 - 低顯存設備', 'ja': '3Bパラメータ 4-bit量子化 - 低VRAM環境向け'}
    },
    'seedvr2_ema_3b-Q8_0.gguf': {
        'type': 'DiT', 'params': '3B', 'size': '3.5GB', 'precision': 'Q8', 'vram': '~6GB',
        'desc': {'zh-CN': '3B参数 8-bit量化 - 低显存高质量', 'en': '3B params 8-bit quantized - Low VRAM, good quality',
                 'zh-TW': '3B參數 8-bit量化 - 低顯存高品質', 'ja': '3Bパラメータ 8-bit量子化 - 低VRAM高品質'}
    },
    'seedvr2_ema_7b_fp16.safetensors': {
        'type': 'DiT', 'params': '7B', 'size': '16GB', 'precision': 'FP16', 'vram': '~24GB',
        'desc': {'zh-CN': '7B参数 FP16 - 最高质量，需要大显存', 'en': '7B params FP16 - Highest quality, requires large VRAM',
                 'zh-TW': '7B參數 FP16 - 最高品質，需要大顯存', 'ja': '7Bパラメータ FP16 - 最高品質、大容量VRAM必要'}
    },
    'seedvr2_ema_7b_fp8_e4m3fn.safetensors': {
        'type': 'DiT', 'params': '7B', 'size': '7.7GB', 'precision': 'FP8', 'vram': '~16GB',
        'desc': {'zh-CN': '7B参数 FP8 - 高质量，显存友好', 'en': '7B params FP8 - High quality, VRAM friendly',
                 'zh-TW': '7B參數 FP8 - 高品質，顯存友好', 'ja': '7Bパラメータ FP8 - 高品質、VRAM効率的'}
    },
    'seedvr2_ema_7b-Q4_K_M.gguf': {
        'type': 'DiT', 'params': '7B', 'size': '4.5GB', 'precision': 'Q4', 'vram': '~8GB',
        'desc': {'zh-CN': '7B参数 4-bit量化 - 大模型低显存方案', 'en': '7B params 4-bit quantized - Large model, low VRAM',
                 'zh-TW': '7B參數 4-bit量化 - 大模型低顯存方案', 'ja': '7Bパラメータ 4-bit量子化 - 大規模モデル低VRAM'}
    },
    'seedvr2_ema_7b-Q8_0.gguf': {
        'type': 'DiT', 'params': '7B', 'size': '8.3GB', 'precision': 'Q8', 'vram': '~12GB',
        'desc': {'zh-CN': '7B参数 8-bit量化 - 大模型平衡方案', 'en': '7B params 8-bit quantized - Large model, balanced',
                 'zh-TW': '7B參數 8-bit量化 - 大模型平衡方案', 'ja': '7Bパラメータ 8-bit量子化 - 大規模モデルバランス型'}
    },
    'seedvr2_ema_7b_sharp_fp16.safetensors': {
        'type': 'DiT', 'params': '7B', 'size': '16GB', 'precision': 'FP16', 'vram': '~24GB', 'variant': 'Sharp',
        'desc': {'zh-CN': '7B参数 锐化版 FP16 - 细节增强 ⭐最佳质量', 'en': '7B params Sharp FP16 - Enhanced details ⭐Best quality',
                 'zh-TW': '7B參數 銳化版 FP16 - 細節增強 ⭐最佳品質', 'ja': '7Bパラメータ シャープ版 FP16 - ディテール強化 ⭐最高品質'}
    },
    'seedvr2_ema_7b_sharp_fp8_e4m3fn.safetensors': {
        'type': 'DiT', 'params': '7B', 'size': '7.7GB', 'precision': 'FP8', 'vram': '~16GB', 'variant': 'Sharp',
        'desc': {'zh-CN': '7B参数 锐化版 FP8 - 细节增强，显存友好', 'en': '7B params Sharp FP8 - Enhanced details, VRAM friendly',
                 'zh-TW': '7B參數 銳化版 FP8 - 細節增強，顯存友好', 'ja': '7Bパラメータ シャープ版 FP8 - ディテール強化、VRAM効率的'}
    },
    'seedvr2_ema_7b_sharp-Q4_K_M.gguf': {
        'type': 'DiT', 'params': '7B', 'size': '4.5GB', 'precision': 'Q4', 'vram': '~8GB', 'variant': 'Sharp',
        'desc': {'zh-CN': '7B参数 锐化版 4-bit - 细节增强低显存', 'en': '7B params Sharp 4-bit - Enhanced details, low VRAM',
                 'zh-TW': '7B參數 銳化版 4-bit - 細節增強低顯存', 'ja': '7Bパラメータ シャープ版 4-bit - ディテール強化低VRAM'}
    },
    'seedvr2_ema_7b_sharp-Q8_0.gguf': {
        'type': 'DiT', 'params': '7B', 'size': '8.3GB', 'precision': 'Q8', 'vram': '~12GB', 'variant': 'Sharp',
        'desc': {'zh-CN': '7B参数 锐化版 8-bit - 细节增强平衡方案', 'en': '7B params Sharp 8-bit - Enhanced details, balanced',
                 'zh-TW': '7B參數 銳化版 8-bit - 細節增強平衡方案', 'ja': '7Bパラメータ シャープ版 8-bit - ディテール強化バランス型'}
    },
}

class GPUManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.debug = Debug(enabled=False)
        
    def get_status(self) -> Dict[str, Any]:
        import torch
        status = {
            'cuda_available': torch.cuda.is_available(),
            'processing': task_queue.current_task_id is not None,
            'current_task': task_queue.current_task_id
        }
        if torch.cuda.is_available():
            status['gpu_name'] = torch.cuda.get_device_name(0)
            status['vram_used_mb'] = torch.cuda.memory_allocated(0) // (1024*1024)
            status['vram_total_mb'] = torch.cuda.get_device_properties(0).total_memory // (1024*1024)
        return status
    
    def offload(self):
        import torch
        with self.lock:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True

gpu_manager = GPUManager()

# ============================================================================
# API Routes
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    queue_status = task_queue.get_status()
    return jsonify({
        'status': 'healthy',
        'version': '1.4.0',
        'queue_enabled': True,
        'queue_length': queue_status['queue_length'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/gpu/status')
def gpu_status():
    """Get GPU status"""
    return jsonify(gpu_manager.get_status())

@app.route('/api/gpu/offload', methods=['POST'])
def gpu_offload():
    """Release GPU memory"""
    gpu_manager.offload()
    return jsonify({'status': 'success', 'message': 'GPU memory released'})

@app.route('/api/models')
def list_models():
    """List available models"""
    available_files = set()
    if os.path.exists(MODEL_DIR):
        available_files = set(os.listdir(MODEL_DIR))
    
    models = []
    for name, info in MODEL_INFO.items():
        if info['type'] == 'DiT' and name in available_files:
            models.append({
                'name': name,
                'params': info.get('params', ''),
                'size': info.get('size', ''),
                'precision': info.get('precision', ''),
                'vram': info.get('vram', ''),
                'variant': info.get('variant', ''),
                'desc': info.get('desc', {})
            })
    
    return jsonify({
        'models': models,
        'default': DEFAULT_DIT
    })

# ============================================================================
# Queue API Routes - NEW in v1.4.0
# ============================================================================

@app.route('/api/queue/status')
def queue_status():
    """
    Get queue status
    ---
    tags: [Queue]
    responses:
      200:
        description: Queue status with pending tasks, processing info, and statistics
    """
    return jsonify(task_queue.get_status())

@app.route('/api/queue/position/<task_id>')
def queue_position(task_id):
    """
    Get task position in queue
    ---
    tags: [Queue]
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Task position and estimated wait time
    """
    result = task_queue.get_task_position(task_id)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/queue/history')
def queue_history():
    """
    Get completed task history
    ---
    tags: [Queue]
    parameters:
      - name: limit
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: List of completed tasks
    """
    limit = request.args.get('limit', 20, type=int)
    return jsonify({'history': task_queue.get_history(limit)})

# ============================================================================
# Processing API Routes
# ============================================================================

@app.route('/api/process', methods=['POST'])
def process():
    """
    Submit task to queue
    ---
    tags: [Processing]
    consumes: [multipart/form-data]
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      - name: resolution
        in: formData
        type: integer
        default: 1080
      - name: batch_size
        in: formData
        type: integer
        default: 5
      - name: dit_model
        in: formData
        type: string
      - name: color_correction
        in: formData
        type: string
        default: lab
      - name: seed
        in: formData
        type: integer
        default: 42
    responses:
      200:
        description: Task queued with position info
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    
    task_id = str(uuid.uuid4())[:8]
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_{filename}")
    file.save(input_path)
    
    params = {
        'resolution': int(request.form.get('resolution', 1080)),
        'batch_size': int(request.form.get('batch_size', 5)),
        'dit_model': request.form.get('dit_model', DEFAULT_DIT),
        'color_correction': request.form.get('color_correction', 'lab'),
        'seed': int(request.form.get('seed', 42)),
        'blocks_to_swap': int(request.form.get('blocks_to_swap', 0)),
        'vae_tiling': request.form.get('vae_tiling', 'auto'),
        'vae_quality': request.form.get('vae_quality', 'high'),
    }
    
    ext = Path(file.filename).suffix.lower()
    is_video = ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    
    resolution = params['resolution']
    vae_tiling = params['vae_tiling']
    if vae_tiling == 'on':
        params['encode_tiled'] = True
        params['decode_tiled'] = True
    elif vae_tiling == 'off':
        params['encode_tiled'] = False
        params['decode_tiled'] = False
    else:
        threshold = 1440 if is_video else 2880
        params['encode_tiled'] = resolution >= threshold
        params['decode_tiled'] = resolution >= threshold
    
    result = task_queue.submit(task_id, input_path, params)
    return jsonify(result)

@app.route('/api/status/<task_id>')
def task_status(task_id):
    """Get task status"""
    task = task_queue.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

@app.route('/api/download/<task_id>')
def download_result(task_id):
    """Download processed file"""
    task = task_queue.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    if task['status'] != 'completed':
        return jsonify({'error': 'Task not completed'}), 400
    
    output_path = task.get('output_path')
    output_filename = task.get('output_filename')
    
    if not output_path or not os.path.exists(output_path):
        return jsonify({'error': 'Output file not found'}), 404
    
    return send_file(output_path, as_attachment=True, download_name=output_filename)

# ============================================================================
# UI Route
# ============================================================================

@app.route('/')
def index():
    """Serve the web UI"""
    template_path = os.path.join(script_dir, 'templates', 'index.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "UI template not found", 404

@app.route('/docs')
def docs_redirect():
    from flask import redirect
    return redirect('/apidocs')

# ============================================================================
# Main Entry
# ============================================================================

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8200)))
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    # Start queue worker
    task_queue.start_worker()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     SeedVR2 Video Upscaler Server v1.4.0 - Queue Edition   ║
╠════════════════════════════════════════════════════════════╣
║  🔄 Task Queue: ENABLED (Serial GPU Processing)            ║
║  📊 Max History: {MAX_HISTORY_SIZE} tasks                                   ║
╚════════════════════════════════════════════════════════════╝

   🌐 Web UI:      http://{args.host}:{args.port}
   📚 API Docs:    http://{args.host}:{args.port}/docs
   🔧 Health:      http://{args.host}:{args.port}/health
   📋 Queue:       http://{args.host}:{args.port}/api/queue/status
""")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    finally:
        task_queue.shutdown()
