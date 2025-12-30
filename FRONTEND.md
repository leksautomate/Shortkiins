# Python Frontend Framework Options

This document outlines the best Python-based frontend frameworks you can use to build a web interface for the Video Generator Pipeline.

## Recommended Frameworks

### 1. **Streamlit** ⭐ (Best for Quick Prototypes)

**Best for:** Rapid prototyping, data science dashboards, internal tools

```python
import streamlit as st
from pathlib import Path
from main import VideoPipeline

st.title("🎬 AI Video Generator")

# Input
script = st.text_area("Enter your script:", height=200)
aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16"])
image_provider = st.selectbox("Image Provider", ["wavespeed", "freepik", "replicate"])
scene_duration = st.slider("Scene Duration (seconds)", 1.0, 10.0, 3.0)

# Generate button
if st.button("Generate Video"):
    with st.spinner("Generating video..."):
        pipeline = VideoPipeline(
            script=script,
            output_path=Path("output/video.mp4"),
            scene_duration=scene_duration,
            image_provider=image_provider,
        )
        output = pipeline.run()
        st.success(f"Video generated: {output}")
        st.video(str(output))
```

**Installation:**
```bash
pip install streamlit
streamlit run app.py
```

**Pros:**
- ✅ Fastest development (minutes to working app)
- ✅ Beautiful built-in components
- ✅ Auto-reloads on code changes
- ✅ Easy progress bars, spinners, file uploads
- ✅ Perfect for MVP/prototype

**Cons:**
- ❌ Limited customization
- ❌ Not ideal for complex layouts
- ❌ Session state management can be tricky

---

### 2. **Gradio** ⭐ (Best for ML Demos)

**Best for:** Machine learning demos, sharing prototypes, HuggingFace deployment

```python
import gradio as gr
from pathlib import Path
from main import VideoPipeline

def generate_video(script, aspect_ratio, provider, duration):
    """Generate video from script."""
    settings.aspect_ratio = aspect_ratio

    pipeline = VideoPipeline(
        script=script,
        output_path=Path("output/video.mp4"),
        scene_duration=duration,
        image_provider=provider,
    )

    output = pipeline.run()
    return str(output)

# Create interface
interface = gr.Interface(
    fn=generate_video,
    inputs=[
        gr.Textbox(lines=10, label="Script", placeholder="Enter your script..."),
        gr.Radio(["16:9", "9:16"], label="Aspect Ratio", value="16:9"),
        gr.Dropdown(["wavespeed", "freepik", "replicate"], label="Image Provider"),
        gr.Slider(1, 10, value=3, label="Scene Duration (seconds)"),
    ],
    outputs=gr.Video(label="Generated Video"),
    title="🎬 AI Video Generator",
    description="Transform your script into a professional video with AI",
    examples=[
        ["Welcome to the future of AI...", "16:9", "wavespeed", 3],
    ]
)

interface.launch(share=True)  # Creates public link
```

**Installation:**
```bash
pip install gradio
python app.py
```

**Pros:**
- ✅ Perfect for ML/AI demos
- ✅ One-click public sharing
- ✅ Built-in queue system for long tasks
- ✅ Easy HuggingFace Spaces deployment
- ✅ Beautiful default styling

**Cons:**
- ❌ Less flexible than full web frameworks
- ❌ Limited layout control

---

### 3. **Flask** (Best for Custom Web Apps)

**Best for:** Full control, custom designs, RESTful APIs

```python
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from main import VideoPipeline
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json

    # Run pipeline in background
    def run_pipeline():
        pipeline = VideoPipeline(
            script=data['script'],
            output_path=Path(f"output/{data['id']}.mp4"),
            scene_duration=data.get('scene_duration', 3),
            image_provider=data.get('provider', 'wavespeed'),
        )
        pipeline.run()

    thread = threading.Thread(target=run_pipeline)
    thread.start()

    return jsonify({"status": "processing", "id": data['id']})

@app.route('/video/<video_id>')
def get_video(video_id):
    return send_file(f"output/{video_id}.mp4")

if __name__ == '__main__':
    app.run(debug=True)
```

**Frontend (templates/index.html):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Video Generator</title>
</head>
<body>
    <h1>🎬 AI Video Generator</h1>
    <textarea id="script" rows="10" cols="50"></textarea>
    <select id="aspect-ratio">
        <option value="16:9">16:9 Landscape</option>
        <option value="9:16">9:16 Portrait</option>
    </select>
    <button onclick="generateVideo()">Generate</button>
    <video id="result" controls></video>

    <script>
    async function generateVideo() {
        const script = document.getElementById('script').value;
        const aspectRatio = document.getElementById('aspect-ratio').value;

        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                script: script,
                aspect_ratio: aspectRatio,
                id: Date.now()
            })
        });

        const data = await response.json();
        // Poll for completion...
    }
    </script>
</body>
</html>
```

**Pros:**
- ✅ Full control over design
- ✅ Mature ecosystem
- ✅ Easy to integrate with React, Vue, etc.
- ✅ RESTful API support

**Cons:**
- ❌ More boilerplate code
- ❌ Need to handle frontend separately

---

### 4. **FastAPI** (Best for APIs + Modern UI)

**Best for:** Production APIs, async support, modern stack

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from main import VideoPipeline
import uuid

app = FastAPI()

class VideoRequest(BaseModel):
    script: str
    aspect_ratio: str = "16:9"
    image_provider: str = "wavespeed"
    scene_duration: float = 3.0

@app.post("/generate")
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    video_id = str(uuid.uuid4())
    output_path = Path(f"output/{video_id}.mp4")

    def run_pipeline():
        settings.aspect_ratio = request.aspect_ratio
        pipeline = VideoPipeline(
            script=request.script,
            output_path=output_path,
            scene_duration=request.scene_duration,
            image_provider=request.image_provider,
        )
        pipeline.run()

    background_tasks.add_task(run_pipeline)
    return {"video_id": video_id, "status": "processing"}

@app.get("/video/{video_id}")
async def get_video(video_id: str):
    return FileResponse(f"output/{video_id}.mp4")
```

**Pros:**
- ✅ Async/await support
- ✅ Automatic API documentation (Swagger UI)
- ✅ Type validation with Pydantic
- ✅ Modern Python best practices
- ✅ WebSocket support for real-time updates

**Cons:**
- ❌ Need separate frontend
- ❌ Slightly steeper learning curve

---

### 5. **NiceGUI** (Best for Desktop-like Web Apps)

**Best for:** Desktop app feel in browser, real-time updates

```python
from nicegui import ui
from pathlib import Path
from main import VideoPipeline

def generate_video():
    script = script_input.value
    aspect_ratio = aspect_select.value

    with ui.dialog() as dialog:
        ui.label('Generating video...')
        ui.spinner(size='lg')

    dialog.open()

    pipeline = VideoPipeline(
        script=script,
        output_path=Path("output/video.mp4"),
        scene_duration=3.0,
        image_provider='wavespeed',
    )
    output = pipeline.run()

    dialog.close()
    ui.notify('Video generated!', type='positive')
    video_player.set_source(str(output))

ui.label('🎬 AI Video Generator').classes('text-3xl font-bold')

script_input = ui.textarea('Script').classes('w-full')
aspect_select = ui.select(['16:9', '9:16'], value='16:9', label='Aspect Ratio')

ui.button('Generate Video', on_click=generate_video)

video_player = ui.video('')

ui.run(port=8080)
```

**Pros:**
- ✅ Very Pythonic (no HTML/CSS needed)
- ✅ Real-time updates
- ✅ Beautiful Tailwind CSS styling
- ✅ Desktop app feel

**Cons:**
- ❌ Newer framework (smaller community)
- ❌ Less flexible for complex layouts

---

## Comparison Table

| Framework | Difficulty | Speed | Customization | Best For |
|-----------|-----------|-------|---------------|----------|
| **Streamlit** | ⭐ Easy | ⚡⚡⚡ Fast | ⚙️ Limited | Quick prototypes |
| **Gradio** | ⭐ Easy | ⚡⚡⚡ Fast | ⚙️ Limited | ML demos |
| **NiceGUI** | ⭐⭐ Medium | ⚡⚡ Medium | ⚙️⚙️ Medium | Desktop-like apps |
| **Flask** | ⭐⭐ Medium | ⚡⚡ Medium | ⚙️⚙️⚙️ Full | Custom web apps |
| **FastAPI** | ⭐⭐⭐ Hard | ⚡⚡⚡ Fast | ⚙️⚙️⚙️ Full | Production APIs |

---

## Recommended Setup

### For Quick Demo: Streamlit

```bash
# Install
pip install streamlit

# Create app.py
cat > app.py << 'EOF'
import streamlit as st
from pathlib import Path
from main import VideoPipeline
from config import settings

st.set_page_config(page_title="AI Video Generator", page_icon="🎬")

st.title("🎬 AI Video Generator")
st.markdown("Transform your script into professional videos with AI")

# Sidebar settings
st.sidebar.header("Settings")
aspect_ratio = st.sidebar.radio("Aspect Ratio", ["16:9 (Landscape)", "9:16 (Portrait)"])
image_provider = st.sidebar.selectbox("Image Provider", ["wavespeed", "freepik", "replicate"])
scene_duration = st.sidebar.slider("Scene Duration", 1.0, 10.0, 3.0)

# Main input
script = st.text_area("Enter your script:", height=200,
    placeholder="Welcome to the future of AI-powered video creation...")

if st.button("🚀 Generate Video", type="primary"):
    if not script:
        st.error("Please enter a script!")
    else:
        # Set aspect ratio
        settings.aspect_ratio = aspect_ratio.split()[0]

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Generating voiceover...")
        progress_bar.progress(15)

        # Run pipeline
        try:
            pipeline = VideoPipeline(
                script=script,
                output_path=Path("output/video.mp4"),
                scene_duration=scene_duration,
                image_provider=image_provider,
            )

            output = pipeline.run()

            progress_bar.progress(100)
            status_text.text("✅ Complete!")

            st.success("Video generated successfully!")
            st.video(str(output))

            # Download button
            with open(output, "rb") as f:
                st.download_button(
                    label="📥 Download Video",
                    data=f,
                    file_name="generated_video.mp4",
                    mime="video/mp4"
                )
        except Exception as e:
            st.error(f"Error: {e}")
EOF

# Run
streamlit run app.py
```

### For Production: FastAPI + React

**Backend (api.py):**
```bash
pip install fastapi uvicorn python-multipart
```

See FastAPI example above, then run:
```bash
uvicorn api:app --reload
```

**Frontend:** Use React, Vue, or Next.js to call the API

---

## Next Steps

1. **Choose a framework** based on your needs
2. **Install dependencies**: `pip install streamlit` (or your choice)
3. **Create UI**: Use examples above as starting point
4. **Add features**:
   - File upload for scripts
   - Progress tracking
   - Video gallery
   - User authentication
   - Queue management for multiple videos

## Questions?

- For prototypes: Start with **Streamlit**
- For ML demos: Use **Gradio**
- For production: Go with **FastAPI + React**
- For quick custom UI: Try **NiceGUI**
