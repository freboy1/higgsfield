from fastapi import APIRouter
from app.src.models.model import GeneratedTextResponse, TextForGenerationPrompt, Slide, PromptAndImageRequest
from fastapi.responses import FileResponse
from app.src.endpoints.lecture_endpoints import LectureMarkdownFormatter
from app.src.endpoints.image_endpoints import get_images_with_avatar
from dotenv import load_dotenv
import os
import json
import requests, time
import cv2
import numpy as np

from typing import List, Optional
router = APIRouter()


load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_SECRET = os.getenv("HF_SECRET")

def check_for_generation_video(job_set_id):
    url = "https://platform.higgsfield.ai/v1/job-sets/" + job_set_id
    headers = {
        "hf-api-key": HF_API_KEY,
        "hf-secret": HF_SECRET
    }

    response = requests.get(url, headers=headers)
    print(response)
    if (response.status_code == 200) :
        data = response.json()
        jobs = data.get("jobs", [])
        if jobs:
            first = jobs[0]
            status = first.get("status")
            results = first.get("results") or {}
            min_info = results.get("raw")

            if (status == 'completed'):
                if min_info and "url" in min_info:
                    return min_info["url"]
    return False

def generate_single_video(slide: List[dict], avatar: str):
    url = "https://platform.higgsfield.ai/v1/speak/veo3"

    headers = {
        "Content-Type": "application/json",
        "hf-api-key": HF_API_KEY,
        "hf-secret": HF_SECRET
    }

    data = {
        "params": {
            "model": "veo-3-fast",
            "prompt": '''
            You are generating a professional presentation-style explainer video.  Inputs: - Image A: presenter’s face or half-body portrait - Image B: presentation slide - Optional: audio narration (voice-over) or TTS will be provided separately  Layout requirements: - 16:9 horizontal video - Image B (slide) must fill 75–80% of the left side — full clarity, no cropping of text - Image A (human) should appear on the right side as a fixed webcam avatar - Avatar must remain fixed in size (approx 20–25% width), vertically centered - No overlapping or clutter — clean separation between presenter and slide  Motion & Behavior: - Human should appear naturally alive (subtle head motion, eye blinks, light expression) - Do NOT overly animate or distort the presenter - No camera zoom, no transitions — stable, professional composition - If audio or TTS is provided, sync mouth motion and pacing to narration  Style and atmosphere: - Modern educational / startup keynote style (TED, OpenAI DevDay, Loom, Google Meet) - Neutral lighting, realistic color retention - No effects, particles, borders, or distracting visual elements - Absolutely NO watermarks or fake UI elements  Output: - 1080p 16:9 MP4 video - Ready to serve directly as a lecture / lection preview''',
            "quality": "basic",
            "input_image": {
                "type": "image_url",
                "image_url": slide["url"]
                },
            "aspect_ratio": "16:9",
            "audio_prompt": slide["script"],
            "enhance_prompt": True
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        data = response.json()
        return data.get("id")
    return False


def get_videos_with_avatar(slides: List[dict], avatar: str):
    # prompts = split_slides(text)
    videosIdsAndUrls: List[dict] = []
    # print(prompts)
    for slide in slides:
        job_set_id = generate_single_video(slide, avatar)
        if (job_set_id != ''):
            videosIdsAndUrls.append({"id": job_set_id, "url": None, "script": slide["script"], "title": slide['title'], "content": slide["content"]})
    time.sleep(30)  
    print(videosIdsAndUrls)

    while True:
        all_done = True
        for img in videosIdsAndUrls:
            if img["url"] is None:
                result = check_for_generation_video(img["id"])  
                if result:
                    img["url"] = result 
                else:
                    all_done = False
        if all_done:
            break
        time.sleep(5)
    print(videosIdsAndUrls)
    
    return videosIdsAndUrls

def download_video(url, filename):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

def merge_videos_from_urls(urls, output_file="merged.mp4"):
    os.makedirs("videos", exist_ok=True)
    video_files = []

    for i, url in enumerate(urls):
        filename = f"videos/video_{i}.mp4"
        download_video(url, filename)
        video_files.append(filename)

    # Read first video for frame size and FPS
    first = cv2.VideoCapture(video_files[0])
    fps = first.get(cv2.CAP_PROP_FPS)
    width = int(first.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(first.get(cv2.CAP_PROP_FRAME_HEIGHT))
    first.release()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for vf in video_files:
        cap = cv2.VideoCapture(vf)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        cap.release()

    out.release()

@router.post("/generate-video", response_model=GeneratedTextResponse)
def generate_video(prompt: PromptAndImageRequest):
    markdown_formatter = LectureMarkdownFormatter()
    print(prompt.text)
    slides = LectureMarkdownFormatter.parse_markdown_to_slides(prompt.text)
    print(prompt.avatar)
    print(json.dumps(slides, indent=2, ensure_ascii=False))
    # print(json.dumps(get_images_with_avatar(slides, "https://d3snorpfx4xhv8.cloudfront.net/c2906af4-60bf-416c-95e0-639aa06d11cd/37657c2a-3962-4575-bb80-89c2864f0be9.jpeg"), indent=2, ensure_ascii=False))
    images = get_images_with_avatar(slides, "https://d3snorpfx4xhv8.cloudfront.net/c2906af4-60bf-416c-95e0-639aa06d11cd/37657c2a-3962-4575-bb80-89c2864f0be9.jpeg")
    print(json.dumps(images, indent=2, ensure_ascii=False))
    videos = get_videos_with_avatar(images, "https://d3snorpfx4xhv8.cloudfront.net/c2906af4-60bf-416c-95e0-639aa06d11cd/37657c2a-3962-4575-bb80-89c2864f0be9.jpeg")
    print(json.dumps(videos, indent=2, ensure_ascii=False))
    urls = []
    for video in videos:
        urls.append(video["url"])

    output_file = "merged.mp4"
    merge_videos_from_urls(urls, output_file=output_file)

    if not os.path.exists(output_file):
        return {"status": 0, "error": "Failed to create merged video."}

    return FileResponse(output_file, media_type="video/mp4", filename="lecture_video.mp4")
