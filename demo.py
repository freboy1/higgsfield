#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def demo_lecture_api():
    """Demonstrate the lecture generation API"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("HIGGSFIELD LECTURE GENERATOR API DEMO")
    print("=" * 60)
    
    # Test 1: Generate a lecture
    print("\n1. Generating a lecture on 'Introduction to AI'...")
    print("-" * 50)
    
    lecture_request = {
        "topic": "Introduction to Artificial Intelligence",
        "duration_minutes": 10,
        "difficulty_level": "beginner",
        "target_audience": "students"
    }
    
    try:
        response = requests.post(
            f"{base_url}/lecture/generate-lecture",
            json=lecture_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS! Generated lecture:")
            print(f"  Topic: {result['topic']}")
            print(f"  Duration: {result['duration_minutes']} minutes")
            print(f"  Total slides: {result['total_slides']}")
            
            print(f"\n  Slides Generated:")
            for i, slide in enumerate(result['slides'][:3], 1):  # Show first 3 slides
                print(f"    {i}. {slide['title']}")
                print(f"       Content: {slide['content'][:80]}...")
                print(f"       Script: {slide['script'][:100]}...")
                print(f"       Image Prompt: {slide['image_prompt'][:60]}...")
                print()
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API. Make sure server is running:")
        print("  uvicorn main:app --reload")
        return
    
    # Test 2: Simple text generation
    print("\n2. Testing simple text generation...")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}/lecture/generate-text",
            params={"prompt": "What is machine learning?"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Generated text:")
            print(f"  {result['text'][:150]}...")
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 3: API health check
    print("\n3. API Health Check...")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! API is running:")
            print(f"  Message: {result['message']}")
            print(f"  Version: {result['version']}")
            print(f"  Available endpoints: {list(result['endpoints'].keys())}")
        else:
            print(f"ERROR: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Set up your real API keys in .env file")
    print("2. Build your React/Next.js frontend")
    print("3. Integrate with Higgsfield image generation")
    print("4. Add TTS and video composition features")

if __name__ == "__main__":
    demo_lecture_api()
