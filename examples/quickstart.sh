#!/bin/bash
# Quick start script for testing the video generator

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the pipeline with the sample script
python main.py \
    --script-file examples/sample_script.txt \
    --output output/sample_video.mp4 \
    --scene-duration 3 \
    --image-provider replicate \
    --verbose

echo "Done! Check output/sample_video.mp4"
