#!/usr/bin/env python3
"""
HoloVoice - Web App integrating ElevenLabs Voice Agent with Hologram Generation
Extracting best practices from holomind_bisa architecture
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
import cv2
import numpy as np

# Configure logging (following holomind_bisa patterns)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==============================================================================
# CONFIGURATION MANAGEMENT (inspired by holomind_bisa)
# ==============================================================================

@dataclass
class AppConfig:
    """Configuration management following holomind_bisa patterns"""
    elevenlabs_agent_url: str = "https://elevenlabs.io/app/talk-to?agent_id=agent_6301kawg1z5efpvvp2kf89dngav6"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: List[str] = field(default_factory=lambda: ['.png', '.jpg', '.jpeg', '.avi', '.mp4'])
    hologram_settings: Dict[str, Any] = field(default_factory=lambda: {
        'scale': 0.5,
        'scaleR': 4,
        'distance': 0
    })

    def __post_init__(self):
        # Create directories if they don't exist
        Path(self.upload_dir).mkdir(exist_ok=True)
        Path(self.output_dir).mkdir(exist_ok=True)

# ==============================================================================
# HOLOGRAM PROCESSOR (integrating with existing 3DHologram.py)
# ==============================================================================

class HologramProcessor:
    """Handles hologram generation using the existing 3DHologram.py"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.processing_jobs: Dict[str, Dict[str, Any]] = {}

    async def process_file(self, file_path: str, job_id: str) -> Dict[str, Any]:
        """Process uploaded file and generate hologram"""
        try:
            self.processing_jobs[job_id] = {
                'status': 'processing',
                'progress': 0,
                'start_time': time.time()
            }

            # Determine output path
            file_name = Path(file_path).stem
            output_path = os.path.join(self.config.output_dir, f"hologram_{file_name}_{job_id}")

            # Call the existing hologram generator
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Process image
                output_file = await self._process_image(file_path, output_path)
            elif file_path.lower().endswith(('.avi', '.mp4')):
                # Process video
                output_file = await self._process_video(file_path, output_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")

            self.processing_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'output_file': output_file,
                'end_time': time.time()
            })

            return self.processing_jobs[job_id]

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self.processing_jobs[job_id].update({
                'status': 'failed',
                'error': str(e),
                'end_time': time.time()
            })
            raise

    async def _process_image(self, input_path: str, output_path: str) -> str:
        """Process image file using 3DHologram.py logic"""
        # Import the hologram generation function
        import sys
        sys.path.append('.')

        try:
            # Read image
            orig = cv2.imread(input_path)
            if orig is None:
                raise ValueError(f"Could not read image: {input_path}")

            # Generate hologram using the same logic as 3DHologram.py
            from hologram_generator import makeHologram  # We'll create this wrapper

            holo = makeHologram(orig, **self.config.hologram_settings)

            # Save output
            output_file = f"{output_path}.png"
            cv2.imwrite(output_file, holo)

            return output_file

        except ImportError:
            # Fallback: call 3DHologram.py as subprocess
            output_file = f"{output_path}.png"
            result = await asyncio.create_subprocess_exec(
                'python', '3DHologram.py', input_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode != 0:
                stderr = await result.stderr.read()
                raise RuntimeError(f"Hologram generation failed: {stderr.decode()}")

            # The 3DHologram.py saves as hologram.png, we need to rename it
            default_output = "hologram.png"
            if os.path.exists(default_output):
                os.rename(default_output, output_file)

            return output_file

    async def _process_video(self, input_path: str, output_path: str) -> str:
        """Process video file using 3DHologram.py logic"""
        # Similar to image processing but for videos
        output_file = f"{output_path}.mp4"

        # Call 3DHologram.py as subprocess for video processing
        result = await asyncio.create_subprocess_exec(
            'python', '3DHologram.py', input_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await result.wait()

        if result.returncode != 0:
            stderr = await result.stderr.read()
            raise RuntimeError(f"Video hologram generation failed: {stderr.decode()}")

        # Rename the default output
        default_output = "hologram_output.mp4"
        if os.path.exists(default_output):
            os.rename(default_output, output_file)
        elif os.path.exists("hologram.avi"):
            # Sometimes it creates .avi
            os.rename("hologram.avi", output_file)

        return output_file

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        return self.processing_jobs.get(job_id)

# ==============================================================================
# VOICE AGENT INTEGRATION
# ==============================================================================

class VoiceAgentManager:
    """Manages ElevenLabs voice agent integration"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.agent_url = config.elevenlabs_agent_url

    def get_agent_embed_code(self) -> str:
        """Generate embed code for ElevenLabs voice agent"""
        return f"""
        <iframe
            src="{self.agent_url}"
            width="100%"
            height="600px"
            frameborder="0"
            allow="microphone; autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy">
        </iframe>
        """

# ==============================================================================
# FASTAPI APPLICATION
# ==============================================================================

app = FastAPI(
    title="HoloVoice - Holographic Voice Assistant",
    description="Web app integrating ElevenLabs voice agent with hologram generation",
    version="1.0.0"
)

# Initialize components
config = AppConfig()
hologram_processor = HologramProcessor(config)
voice_manager = VoiceAgentManager(config)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory=config.output_dir), name="outputs")

# Templates
templates = Jinja2Templates(directory="templates")

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "agent_embed": voice_manager.get_agent_embed_code()
    })

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Upload and process file for hologram generation"""

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {config.allowed_extensions}"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > config.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {config.max_file_size} bytes"
        )

    # Save uploaded file
    job_id = str(uuid.uuid4())
    upload_path = os.path.join(config.upload_dir, f"{job_id}_{file.filename}")

    with open(upload_path, "wb") as f:
        f.write(file_content)

    # Start background processing
    background_tasks.add_task(hologram_processor.process_file, upload_path, job_id)

    return {
        "job_id": job_id,
        "message": "File uploaded and processing started",
        "status_url": f"/status/{job_id}"
    }

@app.get("/status/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get processing status for a job"""
    status = hologram_processor.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")

    return status

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket for real-time status updates"""
    await websocket.accept()

    try:
        while True:
            status = hologram_processor.get_job_status(job_id)
            if status:
                await websocket.send_json(status)

                if status.get('status') in ['completed', 'failed']:
                    break

            await asyncio.sleep(1)  # Update every second

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download processed hologram"""
    status = hologram_processor.get_job_status(job_id)
    if not status or status.get('status') != 'completed':
        raise HTTPException(status_code=404, detail="Result not ready or job failed")

    output_file = status.get('output_file')
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        output_file,
        media_type='application/octet-stream',
        filename=os.path.basename(output_file)
    )

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    logger.info("Starting HoloVoice web application...")
    logger.info(f"ElevenLabs Agent URL: {config.elevenlabs_agent_url}")

    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )