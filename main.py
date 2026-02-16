# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from moviepy.editor import ImageClip, AudioFileClip
from fastapi.responses import FileResponse

app = FastAPI()

# Allow your app to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your Zeana app domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-video")
async def generate_video(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    duration: int = Form(18)  # default 18 seconds
):
    temp_dir = tempfile.mkdtemp()

    image_path = os.path.join(temp_dir, "image.jpg")
    audio_path = os.path.join(temp_dir, "audio.mp3")
    video_path = os.path.join(temp_dir, "output.mp4")

    # Save uploaded files
    with open(image_path, "wb") as f:
        f.write(await image.read())

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Create video from image and audio
    clip = ImageClip(image_path).set_duration(duration)
    audio_clip = AudioFileClip(audio_path)
    clip = clip.set_audio(audio_clip)
    clip.write_videofile(video_path, fps=24, codec="libx264")

    return FileResponse(video_path, media_type="video/mp4")
