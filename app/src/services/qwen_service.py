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
        Generate lecture content with enhanced prompt engineering
        """
        if add_ons is None:
            add_ons = {}
        
        # Calculate optimal slide count based on duration
        slides_count = max(3, min(8, duration_minutes // 2))
        
        # Build comprehensive system message
        system_message = self._build_system_message(difficulty_level, target_audience, tone)
        
        # Build structured user prompt
        user_prompt = self._build_user_prompt(
            topic, duration_minutes, slides_count, difficulty_level, 
            target_audience, tone, add_ons
        )
        
        try:
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                temperature=0.7,
                max_tokens=4000,
            )
            
            content = response.choices[0].message.content
            
            # Parse and validate JSON
            parsed_data = self._extract_and_validate_json(content, topic, add_ons)
            return parsed_data
                
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            return self._create_fallback_response(topic, str(e), add_ons)
    
    def _build_system_message(self, difficulty: str, audience: str, tone: str) -> str:
        """Build detailed system message to set context"""
        return f"""You are an expert educational content creator and instructional designer specializing in creating engaging, effective lectures.

Your expertise includes:
- Pedagogical best practices for {difficulty} level content
- Creating content for {audience} audiences
- Using a {tone} tone that enhances learning
- Structuring information for optimal retention
- Writing clear, executable code examples
- Designing visual learning aids

Your task is to create a comprehensive lecture presentation that balances theory with practical application."""

    def _build_user_prompt(
        self, topic: str, duration: int, slides_count: int, 
        difficulty: str, audience: str, tone: str, add_ons: Dict[str, bool]
    ) -> str:
        """Build comprehensive user prompt with clear structure"""
        
        # Tone-specific instructions
        tone_instructions = {
            "friendly": "Use conversational language, analogies, and relatable examples. Be encouraging and supportive.",
            "formal": "Use precise academic language, formal structure, and authoritative tone. Cite concepts properly.",
            "exam": "Focus on testable knowledge, key definitions, common pitfalls, and exam strategies. Be direct and comprehensive.",
            "story": "Use narrative structure, real-world scenarios, and character-driven examples. Make it engaging and memorable."
        }
        
        # Difficulty-specific instructions
        difficulty_instructions = {
            "beginner": "Start with fundamentals. Use simple language. Provide step-by-step explanations. Include many examples.",
            "intermediate": "Assume basic knowledge. Focus on practical application. Include best practices and common patterns.",
            "advanced": "Deep technical details. Discuss trade-offs, optimizations, and edge cases. Reference advanced concepts."
        }
        
        prompt = f"""Create a {duration}-minute lecture presentation on: "{topic}"

## LECTURE PARAMETERS
- Duration: {duration} minutes ({slides_count} slides)
- Difficulty: {difficulty}
- Target Audience: {audience}
- Tone: {tone}

## TONE GUIDELINES
{tone_instructions.get(tone, tone_instructions["friendly"])}

## DIFFICULTY GUIDELINES
{difficulty_instructions.get(difficulty, difficulty_instructions["beginner"])}

## CONTENT REQUIREMENTS"""

        # Add-on specific requirements
        if add_ons.get("code_examples", False):
            prompt += """

### Code Examples (REQUIRED)
- Include 2-3 practical, runnable code examples
- Use proper syntax highlighting markers
- Add clear inline comments explaining each section
- Show both basic and slightly advanced usage
- Include common pitfalls or errors to avoid
- For React/JS: use modern ES6+ syntax, hooks, and best practices
- For Python: use type hints and clear variable names
- For general code: show complete, working examples (not snippets)"""

        if add_ons.get("visuals", False):
            prompt += """

### Visual Descriptions (REQUIRED)
- Create highly detailed image prompts for diagrams, flowcharts, or illustrations
- Specify colors, layout, and key visual elements
- Make prompts actionable for image generation AI
- Include data visualization descriptions when relevant"""

        if add_ons.get("exercises", False):
            prompt += """

### Practice Exercises (REQUIRED)
- Include hands-on exercises that reinforce concepts
- Provide clear instructions and expected outcomes
- Range from simple to challenging
- Include hints or solution approaches"""

        if add_ons.get("qa_section", False):
            prompt += """

### Q&A Section (REQUIRED)
- Add a final slide with 3-5 common questions
- Provide detailed, practical answers
- Address misconceptions or confusion points"""

        # JSON structure and examples
        prompt += f"""

## OUTPUT FORMAT
Return a valid JSON object following this EXACT structure:

{{
  "slides": [
    {{
      "slide_number": 1,
      "title": "Clear, Descriptive Title",
      "content": "Well-structured content with:\\n• Bullet point 1\\n• Bullet point 2\\n• Key takeaway",
      "image_prompt": "Detailed description for visual: professional, clean design showing [specific elements], [color scheme], [style]",
      "slide_type": "title",
      "script": "Natural, conversational narration that flows smoothly. 2-4 sentences that sound like spoken language, not written text.",
      "code_example": "// Only if code_examples enabled\\nconst example = () => {{\\n  // Clear comments\\n  return 'working code';\\n}}",
      "exercise": "Only if exercises enabled: Clear task with expected outcome"
    }}
  ]
}}

## SLIDE STRUCTURE REQUIREMENTS

**Slide 1 (Title Slide):**
- Engaging title
- Brief overview (1-2 sentences)
- Set expectations
- Hook the audience

**Slides 2-{slides_count-1} (Content Slides):**
- One main concept per slide
- 3-5 bullet points max
- Balance theory with examples"""

        if add_ons.get("code_examples", False):
            prompt += "\n- Include code example with detailed comments"

        prompt += f"""

**Slide {slides_count} (Conclusion):**
- Recap key points (3-5 items)
- Call to action or next steps
- Additional resources if relevant"""

        if add_ons.get("qa_section", False):
            prompt += "\n- Or use as Q&A slide"

        prompt += """

## QUALITY STANDARDS

### Content Field:
- Must be a single string (not array)
- Use \\n for line breaks between bullet points
- Each bullet should be substantial (not just keywords)
- Include context and explanation

### Script Field:
- Write as SPOKEN language, not formal writing
- Use contractions, natural phrasing
- Connect to previous and next slides
- Be engaging and clear
- 2-4 sentences per slide

### Code Examples:
- Must be complete and runnable
- Include error handling where relevant
- Use meaningful variable names
- Add comments for complex logic
- Show real-world usage patterns

### Image Prompts:
- Be specific about visual elements
- Include style guidance (professional, modern, clean)
- Specify colors when important
- Describe layout and composition

## CRITICAL RULES
1. Return ONLY valid JSON (no markdown code blocks)
2. Ensure all strings are properly escaped
3. Keep slide_number sequential starting from 1
4. Content must be educational and accurate
5. Scripts must sound natural when read aloud
6. Code must follow modern best practices

Begin creating the lecture now."""

        return prompt

    def _extract_and_validate_json(
        self, content: str, topic: str, add_ons: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Extract and validate JSON from response"""
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            # Find JSON bounds
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_content = content[start_idx:end_idx]
            parsed_data = json.loads(json_content)
            
            # Validate and normalize
            return self._normalize_slides(parsed_data, add_ons)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            print(f"Content preview: {content[:500]}")
            return self._create_fallback_response(topic, str(e), add_ons)
    
    def _normalize_slides(self, data: Dict[str, Any], add_ons: Dict[str, bool]) -> Dict[str, Any]:
        """Ensure all slides have required fields and proper formatting"""
        slides = data.get("slides", [])
        
        for i, slide in enumerate(slides):
            # Ensure slide number
            slide["slide_number"] = slide.get("slide_number", i + 1)
            
            # Required fields with defaults
            slide.setdefault("title", f"Slide {i + 1}")
            slide.setdefault("slide_type", "content")
            slide.setdefault("image_prompt", "Professional educational slide design, clean and modern")
            slide.setdefault("script", f"This slide covers {slide.get('title', 'important content')}.")
            
            # Handle content field - ensure it's a well-formatted string
            content = slide.get("content", "")
            if isinstance(content, list):
                slide["content"] = "\n".join(f"• {str(item)}" for item in content)
            elif not isinstance(content, str):
                slide["content"] = str(content)
            else:
                slide["content"] = content or "Content to be added"
            
            # Conditional fields based on add-ons
            if add_ons.get("code_examples", False):
                if "code_example" not in slide or not slide["code_example"]:
                    slide["code_example"] = None
            else:
                slide["code_example"] = None
            
            if add_ons.get("exercises", False):
                if "exercise" not in slide or not slide["exercise"]:
                    slide["exercise"] = None
            else:
                slide["exercise"] = None
        
        return data
    
    def _create_fallback_response(
        self, topic: str, error_msg: str, add_ons: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Create high-quality fallback response"""
        slides = [
            {
                "slide_number": 1,
                "title": f"{topic}: Introduction",
                "content": f"• Welcome to this lecture on {topic}\n• We'll explore key concepts and practical applications\n• This session is designed to build your understanding from the ground up",
                "image_prompt": f"Professional title slide for {topic}, modern design, educational style, clean typography",
                "slide_type": "title",
                "script": f"Welcome everyone! Today we're diving into {topic}. This is an exciting topic that has real-world applications, and I'm going to make sure you understand the fundamentals clearly.",
                "code_example": "// Example code will be provided" if add_ons.get("code_examples") else None,
                "exercise": "Practice exercises will be included" if add_ons.get("exercises") else None
            },
            {
                "slide_number": 2,
                "title": "Core Concepts",
                "content": f"• Understanding the fundamentals of {topic}\n• Key principles and terminology\n• How these concepts apply in practice",
                "image_prompt": f"Diagram showing core concepts of {topic}, clean infographic style",
                "slide_type": "content",
                "script": f"Let's start with the core concepts. Understanding these fundamentals is crucial because they form the foundation of everything else we'll cover.",
                "code_example": None,
                "exercise": None
            },
            {
                "slide_number": 3,
                "title": "Key Takeaways",
                "content": f"• We've covered the essentials of {topic}\n• Remember to practice these concepts\n• Continue exploring to deepen your knowledge",
                "image_prompt": "Summary slide with key points, professional design",
                "slide_type": "conclusion",
                "script": "To wrap up, remember that mastering these concepts takes practice. Keep experimenting and don't hesitate to explore further resources.",
                "code_example": None,
                "exercise": None
            }
        ]
        
        return {"slides": slides}
    
    def generate_text(self, prompt: str) -> str:
        """Simple text generation with improved prompting"""
        try:
            system_msg = "You are a helpful, knowledgeable assistant. Provide clear, accurate, and well-structured responses."
            
            response = self.client.chat.completions.create(
                model="qwen3-max-preview",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"