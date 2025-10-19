"""
Quick test script for markdown generation
"""
import requests
import json

def test_markdown():
    url = "http://localhost:8000/lecture/generate-lecture"
    
    data = {
        "topic": "React Hooks Basics",
        "tone": "friendly",
        "difficulty_level": "intermediate",
        "add_ons": {
            "code_examples": True,
            "exercises": True
        }
    }
    
    print("Testing markdown generation...")
    print(f"Topic: {data['topic']}\n")
    
    try:
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!\n")
            print(f"Generated {result['total_slides']} slides")
            print("\n" + "="*80)
            print("MARKDOWN OUTPUT:")
            print("="*80 + "\n")
            
            if 'markdown_content' in result:
                print(result['markdown_content'])
                
                # Save to file
                with open('generated_lecture.md', 'w', encoding='utf-8') as f:
                    f.write(result['markdown_content'])
                print("\n" + "="*80)
                print("✅ Saved to: generated_lecture.md")
            else:
                print("❌ No markdown_content in response")
                print("Response keys:", result.keys())
        else:
            print(f"❌ Error {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure server is running:")
        print("  uvicorn main:app --reload")

if __name__ == "__main__":
    test_markdown()