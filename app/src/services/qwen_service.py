import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
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
    
    def generate_lecture_content(
        self, 
        topic: str, 
        duration_minutes: int = 10,
        difficulty_level: str = "beginner",
        target_audience: str = "general",
        tone: str = "friendly",
        add_ons: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Generate lecture content with enhanced options for tone and add-ons
        """
        if add_ons is None:
            add_ons = {}
        
        # Build dynamic prompt based on add-ons
        addon_instructions = self._build_addon_instructions(add_ons)
        tone_instructions = self._get_tone_instructions(tone)
        
        prompt = f"""
        You are an expert educational content creator. Create a comprehensive lecture presentation on: "{topic}".

        Requirements:
        - Duration: {duration_minutes} minutes
        - Difficulty: {difficulty_level}
        - Target audience: {target_audience}
        - Tone: {tone} - {tone_instructions}
        - Create 5-8 slides maximum
        
        {addon_instructions}

        Provide response in this JSON format:
        {{
            "slides": [
                {{
                    "slide_number": 1,
                    "title": "Introduction to {topic}",
                    "content": "Brief bullet points or key concepts as a single string",
                    "image_prompt": "Descriptive prompt for slide background/visual",
                    "slide_type": "title",
                    "script": "Natural, conversational narration (2-3 sentences)",
                    "code_example": "// Code here if applicable",
                    "exercise": "Practice task if requested"
                }}
            ]
        }}

        Guidelines:
        - Each script should be natural speech, not written text
        - Image prompts should describe educational, professional visuals
        - Keep content concise and focused per slide
        - Scripts should flow naturally from slide to slide
        - Code examples should be practical and well-commented
        - Content field must be a single string, not a list or array
        - Use bullet points separated by newlines within the content string
        """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    parsed_data = json.loads(json_content)
                    
                    # Post-process to ensure all fields exist
                    return self._normalize_slides(parsed_data, add_ons)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                return self._create_fallback_response(topic, content, add_ons)
                
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            return self._create_fallback_response(topic, str(e), add_ons)
    
    def _build_addon_instructions(self, add_ons: Dict[str, bool]) -> str:
        """Build instruction text based on selected add-ons"""
        instructions = []
        
        if add_ons.get("code_examples", False):
            instructions.append(
                "- Include practical code examples in relevant slides with clear comments"
            )
        
        if add_ons.get("visuals", False):
            instructions.append(
                "- Make image prompts highly descriptive for generating diagrams, charts, or illustrations"
            )
        
        if add_ons.get("exercises", False):
            instructions.append(
                "- Add practice exercises or questions for learners to try"
            )
        
        if add_ons.get("qa_section", False):
            instructions.append(
                "- Include a Q&A slide at the end with common questions and answers"
            )
        
        return "\n".join(instructions) if instructions else ""
    
    def _get_tone_instructions(self, tone: str) -> str:
        """Get specific instructions for each tone"""
        tone_map = {
            "friendly": "Use warm, approachable language. Be conversational and encouraging.",
            "formal": "Use professional, academic language. Be precise and authoritative.",
            "exam": "Focus on key points for assessment. Include study tips and important concepts.",
            "story": "Use narrative techniques. Make content engaging with examples and scenarios."
        }
        return tone_map.get(tone.lower(), "Be clear and informative.")
    
    def _normalize_slides(self, data: Dict[str, Any], add_ons: Dict[str, bool]) -> Dict[str, Any]:
        """Ensure all slides have required fields"""
        slides = data.get("slides", [])
        
        for slide in slides:
            # Ensure optional fields exist if add-ons are enabled
            if add_ons.get("code_examples", False) and "code_example" not in slide:
                slide["code_example"] = ""
            
            if add_ons.get("exercises", False) and "exercise" not in slide:
                slide["exercise"] = ""
            
            # Ensure required fields
            slide.setdefault("slide_number", 1)
            slide.setdefault("title", "Untitled")
            
            # Handle content field - ensure it's a string
            content = slide.get("content", "")
            if isinstance(content, list):
                slide["content"] = "\n".join(str(item) for item in content)
            elif not isinstance(content, str):
                slide["content"] = str(content)
            else:
                slide.setdefault("content", "")
            
            slide.setdefault("image_prompt", "Educational slide design")
            slide.setdefault("slide_type", "content")
            slide.setdefault("script", "")
        
        return data
    
    def _create_fallback_response(self, topic: str, error_msg: str, add_ons: Dict[str, bool]) -> Dict[str, Any]:
        """Create fallback response if API fails"""
        base_slide = {
            "slide_number": 1,
            "title": f"Introduction to {topic}",
            "content": f"Welcome to our lecture on {topic}",
            "image_prompt": f"Professional educational slide about {topic}",
            "slide_type": "title",
            "script": f"Welcome everyone! Today we'll explore {topic}."
        }
        
        # Add optional fields based on add-ons
        if add_ons.get("code_examples", False):
            base_slide["code_example"] = "// Example code will be added here"
        
        if add_ons.get("exercises", False):
            base_slide["exercise"] = "Practice exercise will be provided"
        
        return {"slides": [base_slide]}
    
    def generate_text(self, prompt: str) -> str:
        """Simple text generation"""
        try:
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"