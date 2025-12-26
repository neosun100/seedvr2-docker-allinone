"""
SeedVR2 Video Upscaler - MCP Server
Model Context Protocol interface for programmatic access

Tools:
- upscale_image: Upscale a single image
- upscale_video: Upscale a video file  
- get_gpu_status: Get GPU status
- release_gpu_memory: Release GPU memory
- list_available_models: List available models
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from fastmcp import FastMCP

mcp = FastMCP("seedvr2-upscaler")

# See full implementation in repository

if __name__ == "__main__":
    mcp.run()
