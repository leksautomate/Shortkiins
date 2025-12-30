#!/usr/bin/env python3
"""FastAPI backend for Video Generator Pipeline - Production Ready."""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from main import VideoPipeline

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Generator API",
    description="Generate professional videos from scripts using AI",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for frontend
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# In-memory job storage (use Redis in production)
jobs = {}


class VideoRequest(BaseModel):
    """Request model for video generation."""
    script: str = Field(..., min_length=10, description="Script text to convert to video")
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|9:16)$", description="Video aspect ratio")
    image_provider: str = Field(default="wavespeed", pattern="^(wavespeed|freepik|replicate)$")
    scene_duration: float = Field(default=3.0, ge=1.0, le=10.0, description="Duration of each scene in seconds")
    voice_id: Optional[str] = Field(default=None, description="Optional custom voice ID")


class JobStatus(BaseModel):
    """Job status response model."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    video_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


async def run_video_pipeline(job_id: str, request: VideoRequest):
    """Background task to run video generation pipeline."""

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Starting video generation..."

        # Set aspect ratio
        settings.aspect_ratio = request.aspect_ratio

        # Output path
        output_dir = settings.output_dir
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{job_id}.mp4"

        jobs[job_id]["progress"] = 20
        jobs[job_id]["message"] = "Generating voiceover..."

        # Create pipeline
        pipeline = VideoPipeline(
            script=request.script,
            output_path=output_path,
            scene_duration=request.scene_duration,
            image_provider=request.image_provider,
            voice_id=request.voice_id,
        )

        jobs[job_id]["progress"] = 40
        jobs[job_id]["message"] = "Generating images..."

        # Run pipeline (blocking - runs in background)
        await asyncio.to_thread(pipeline.run)

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "Video generation complete!"
        jobs[job_id]["video_url"] = f"/api/videos/{job_id}"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["progress"] = 0


@app.get("/")
async def root():
    """Serve frontend HTML."""
    return FileResponse("static/index.html")


@app.post("/api/generate", response_model=JobStatus)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Generate a video from script.

    Creates a background job and returns job ID for status tracking.
    """

    # Validate API keys
    if not settings.groq_api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Job created",
        "video_url": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    # Start background task
    background_tasks.add_task(run_video_pipeline, job_id, request)

    return JobStatus(**jobs[job_id])


@app.post("/api/upload")
async def upload_script(file: UploadFile = File(...)):
    """Upload a text file with script content."""

    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(status_code=400, detail="Only .txt and .md files allowed")

    content = await file.read()
    script = content.decode('utf-8')

    return {"script": script, "filename": file.filename}


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a video generation job."""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(**jobs[job_id])


@app.get("/api/videos/{job_id}")
async def get_video(job_id: str):
    """Download generated video."""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    if jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video not ready yet")

    video_path = settings.output_dir / f"{job_id}.mp4"

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"ai_video_{job_id}.mp4"
    )


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its video file."""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    # Delete video file if exists
    video_path = settings.output_dir / f"{job_id}.mp4"
    if video_path.exists():
        video_path.unlink()

    # Delete job from memory
    del jobs[job_id]

    return {"message": "Job deleted successfully"}


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return {"jobs": list(jobs.values())}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "jobs_count": len(jobs)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
