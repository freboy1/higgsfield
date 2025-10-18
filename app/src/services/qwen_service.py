import os
from openai import OpenAI
from typing import List, Dict, Any
import json

class QwenService:
    def __init__(self):
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is required")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
    
    def generate_lecture_content(self, topic: str, duration_minutes: int, difficulty_level: str, target_audience: str) -> Dict[str, Any]:
        """
        Generate lecture content including slides and script using Qwen API
        """
        prompt = f"""
        You are an expert educational content creator. Create a comprehensive lecture presentation on the topic: "{topic}".

        Requirements:
        - Duration: {duration_minutes} minutes
        - Difficulty: {difficulty_level}
        - Target audience: {target_audience}
        - Create 5-8 slides maximum
        - Each slide should have a clear title, content, image prompt, and detailed script for that specific slide

        Please provide your response in the following JSON format:
        {{
            "slides": [
                {{
                    "slide_number": 1,
                    "title": "Introduction to [Topic]",
                    "content": "Brief content for this slide...",
                    "image_prompt": "Professional slide showing introduction to [topic], clean design, educational style",
                    "slide_type": "title",
                    "script": "Welcome everyone! Today we're going to explore [topic]. This is an exciting field that [brief introduction]. Let me start by explaining what [topic] is and why it matters..."
                }},
                {{
                    "slide_number": 2,
                    "title": "Key Concepts",
                    "content": "Main concepts and definitions...",
                    "image_prompt": "Infographic showing key concepts of [topic], modern design, clear typography",
                    "slide_type": "content",
                    "script": "Now let's dive into the key concepts. The first important concept is [concept 1]. This means [explanation]. The second concept is [concept 2], which is crucial because [explanation]..."
                }}
            ]
        }}

        Important guidelines:
        - Each script should be 2-3 sentences that naturally flow from the previous slide
        - Make the script conversational and engaging for the target audience
        - Each script should explain the content shown on that specific slide
        - Make sure each image_prompt is descriptive and suitable for generating educational slides
        - Focus on creating engaging, informative content that matches the difficulty level and audience
        - The script should feel like natural speech, not written text
        """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                # Extract JSON from the response (in case there's extra text)
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: create a simple structure if JSON parsing fails
                return self._create_fallback_response(topic, content)
                
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            return self._create_fallback_response(topic, f"Error generating content: {str(e)}")
    
    def _create_fallback_response(self, topic: str, content: str) -> Dict[str, Any]:
        """Create a fallback response if API call fails"""
        return {
            "slides": [
                {
                    "slide_number": 1,
                    "title": f"Introduction to {topic}",
                    "content": f"Welcome to our lecture on {topic}. This presentation will cover the key concepts and provide you with a comprehensive understanding.",
                    "image_prompt": f"Professional slide showing introduction to {topic}, clean design, educational style",
                    "slide_type": "title",
                    "script": f"Welcome everyone! Today we're going to explore {topic}. This is an exciting field that has many applications in our daily lives. Let me start by explaining what {topic} is and why it matters to you."
                },
                {
                    "slide_number": 2,
                    "title": f"Key Concepts of {topic}",
                    "content": f"Let's explore the main concepts related to {topic} and understand their importance.",
                    "image_prompt": f"Infographic showing key concepts of {topic}, modern design, clear typography",
                    "slide_type": "content",
                    "script": f"Now let's dive into the key concepts of {topic}. The first important concept we need to understand is the fundamental principles. This is crucial because it forms the foundation for everything else we'll learn today."
                }
            ]
        }
    
    def generate_text(self, prompt: str) -> str:
        """
        Simple text generation using Qwen API
        """
        try:
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            return f"Error generating text: {str(e)}"
