# Video Generator Pipeline

An automated video generation pipeline that converts scripts into fully produced videos with AI-generated visuals, voiceovers, and subtitles.

## Features

- **Text-to-Speech**: Custom voice generation using Inworld AI API
- **Subtitle Generation**: Automatic .srt file creation using OpenAI Whisper
- **AI Scene Division**: Intelligent script segmentation with Groq API
- **Image Generation**: Background visuals using Freepik Seedream 4 or Wave Speed zimage
- **Video Effects**: Zoom effects and transitions with MoviePy
- **Final Assembly**: Professional video merging and subtitle burning with FFmpeg

## Workflow

1. **Script Input**: Accept user script (paste or file)
2. **TTS Generation**: Convert script to speech with Inworld AI
3. **Subtitle Creation**: Generate .srt from audio using Whisper
4. **Scene Division**: Split script into 3-second scenes with image prompts (Groq)
5. **Image Generation**: Create background images for each scene
6. **Video Creation**: Convert images to videos with effects (MoviePy)
7. **Final Assembly**: Merge videos and burn subtitles (FFmpeg)

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg installed on your system

```bash
# Install FFmpeg (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install ffmpeg

# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Windows)
# Download from https://ffmpeg.org/download.html
```

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Shortkiins
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Basic Usage

```bash
python main.py --script "Your script text here"
```

### From File

```bash
python main.py --script-file input.txt
```

### Advanced Options

```bash
python main.py \
  --script-file input.txt \
  --output output/my_video.mp4 \
  --scene-duration 3 \
  --voice-id custom_voice_123 \
  --image-model seedream4
```

## Configuration

Edit `.env` file to configure:

- API keys for Inworld AI, Groq, Freepik, Replicate
- Output directories
- Default scene duration
- Voice settings

## Project Structure

```
Shortkiins/
├── main.py                 # Main pipeline orchestrator
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── modules/
│   ├── __init__.py
│   ├── tts.py           # Text-to-speech module
│   ├── subtitles.py     # Subtitle generation
│   ├── scene_division.py # Script segmentation
│   ├── image_gen.py     # Image generation
│   ├── video_effects.py # MoviePy effects
│   └── assembler.py     # FFmpeg assembly
└── examples/
    └── sample_script.txt
```

## API Documentation

### Inworld AI
- Sign up: https://studio.inworld.ai/
- Documentation: https://docs.inworld.ai/

### Groq
- Sign up: https://console.groq.com/
- Documentation: https://console.groq.com/docs

### Freepik
- Sign up: https://www.freepik.com/api
- Documentation: https://www.freepik.com/api/docs

### Replicate
- Sign up: https://replicate.com/
- Documentation: https://replicate.com/docs

## Examples

See `examples/` directory for sample scripts and outputs.

## Troubleshooting

### FFmpeg not found
Ensure FFmpeg is installed and in your system PATH.

### API rate limits
The pipeline implements retry logic and backoff for API calls.

### Memory issues
Large videos may require significant RAM. Adjust `SCENE_DURATION` to create shorter segments.

## License

MIT

## Contributing

Pull requests are welcome! Please open an issue first to discuss proposed changes.
