import requests
import json

# Test the lecture generation API
def test_lecture_generation():
    base_url = "http://localhost:8000"
    
    # Test data
    lecture_request = {
        "topic": "Introduction to Machine Learning",
        "duration_minutes": 15,
        "difficulty_level": "beginner",
        "target_audience": "students"
    }
    
    print("Testing Lecture Generation API...")
    print(f"Request: {json.dumps(lecture_request, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/lecture/generate-lecture",
            json=lecture_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS! Generated lecture:")
            print(f"Topic: {result['topic']}")
            print(f"Duration: {result['duration_minutes']} minutes")
            print(f"Total slides: {result['total_slides']}")
            print("\nSlides:")
            for slide in result['slides']:
                print(f"  {slide['slide_number']}. {slide['title']}")
                print(f"     Content: {slide['content'][:100]}...")
                print(f"     Script: {slide['script'][:150]}...")
                print(f"     Image Prompt: {slide['image_prompt']}")
                print()
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running.")
        print("Run: uvicorn main:app --reload")

def test_simple_text_generation():
    base_url = "http://localhost:8000"
    
    print("\nTesting Simple Text Generation...")
    
    try:
        response = requests.post(
            f"{base_url}/lecture/generate-text",
            params={"prompt": "Explain quantum computing in simple terms"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Generated text:")
            # Handle Unicode characters properly
            text = result['text'].encode('utf-8', errors='replace').decode('utf-8')
            print(text)
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Make sure the server is running.")

if __name__ == "__main__":
    test_lecture_generation()
    test_simple_text_generation()
