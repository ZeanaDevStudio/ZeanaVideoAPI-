import subprocess
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from moviepy.editor import ImageClip, AudioFileClip

app = FastAPI()

@app.post("/generate-video")
async def generate_video(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    duration: int = Form(...)
):
    image_path = f"/tmp/{uuid.uuid4()}_{image.filename}"
    audio_path = f"/tmp/{uuid.uuid4()}_{audio.filename}"
    output_path = f"/tmp/output_{uuid.uuid4()}.mp4"

    # Save uploaded files
    with open(image_path, "wb") as f:
        f.write(await image.read())

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Create video from image
    image_clip = ImageClip(image_path, duration=duration)
    image_clip = image_clip.set_duration(duration)
    image_clip.write_videofile("/tmp/temp_video.mp4", fps=1)

    # Use FFmpeg to merge video + audio (most stable)
    merge_cmd = [
        "ffmpeg",
        "-y",
        "-i", "/tmp/temp_video.mp4",
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    subprocess.run(merge_cmd, check=True)

    return FileResponse(output_path, media_type="video/mp4", filename="final_video.mp4")
