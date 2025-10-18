from fastapi import APIRouter
from app.src.models.model import TextForGenerationPrompt, GenerateImageResponse, TextAndAvatarGeneration
import requests
import json
import time
import os
from dotenv import load_dotenv
from typing import List, Optional

router = APIRouter()

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
HF_SECRET = os.getenv("HF_SECRET")

def divide_prompt(text):
    #here i will divide it 
    return [text]

def generate_image(text):
    url = "https://platform.higgsfield.ai/v1/text2image/nano-banana"
    headers = {
        "Content-Type": "application/json",
        "hf-api-key": HF_API_KEY,
        "hf-secret": HF_SECRET
    }

    data = {
        "params": {
            "prompt": text,
            "aspect_ratio": "4:3",
            "input_images": []
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        data = response.json()
        return data.get("id")
    return ""

def generate_image_with_avatar(text, avatar_url):
    url = "https://platform.higgsfield.ai/v1/text2image/seedream"
    headers = {
        "Content-Type": "application/json",
        "hf-api-key": HF_API_KEY,
        "hf-secret": HF_SECRET
    }

    data = {
        "params": {
            "prompt": text,
            "quality": "basic",
            "aspect_ratio": "4:3",
            "input_images": [
            {
                "type": "image_url",
                "image_url": avatar_url
            }
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        data = response.json()
        return data.get("id")
    return ""

def check_for_generated(job_set_id):
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
            min_info = results.get("min")

            if (status == 'completed'):
                if min_info and "url" in min_info:
                    return min_info["url"]
    return False

def get_images(text):
    prompts = divide_prompt(text)
    imagesIdsAndUrls: List[dict] = []
    print(prompts)
    for prompt_text in prompts:
        job_set_id = generate_image(prompt_text)
        if (job_set_id != ''):
            imagesIdsAndUrls.append({"id": job_set_id, "url": None})
    time.sleep(30)  
    print(imagesIdsAndUrls)

    while True:
        all_done = True
        for img in imagesIdsAndUrls:
            if img["url"] is None:
                result = check_for_generated(img["id"])  
                if result:
                    img["url"] = result 
                else:
                    all_done = False
        if all_done:
            break
        time.sleep(5)
    print(imagesIdsAndUrls)
    
    return imagesIdsAndUrls


def get_images_with_avatar(text, avatar):
    prompts = divide_prompt(text)
    imagesIdsAndUrls: List[dict] = []
    print(prompts)
    for prompt_text in prompts:
        job_set_id = generate_image_with_avatar(prompt_text, avatar)
        if (job_set_id != ''):
            imagesIdsAndUrls.append({"id": job_set_id, "url": None})
    time.sleep(30)  
    print(imagesIdsAndUrls)

    while True:
        all_done = True
        for img in imagesIdsAndUrls:
            if img["url"] is None:
                result = check_for_generated(img["id"])  
                if result:
                    img["url"] = result 
                else:
                    all_done = False
        if all_done:
            break
        time.sleep(5)
    print(imagesIdsAndUrls)
    
    return imagesIdsAndUrls

@router.post("/generate-image", response_model=GenerateImageResponse)
def generate_images(prompt: TextForGenerationPrompt):
    imagesIdsAndUrls = get_images(prompt.text)
    return {"status": 1, "result": imagesIdsAndUrls}


@router.post("/generate-image-with-avatar", response_model=GenerateImageResponse)
def generate_images(prompt: TextAndAvatarGeneration):
    imagesIdsAndUrls = get_images_with_avatar(prompt.text, prompt.avatar)
    return {"status": 1, "result": imagesIdsAndUrls}



