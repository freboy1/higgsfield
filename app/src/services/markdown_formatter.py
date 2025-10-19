"""
Markdown Formatter Service for Lecture Content
Converts lecture slides into human-readable markdown format
"""

from typing import List, Dict, Any
import re
from app.src.models.model import Slide
class LectureMarkdownFormatter:
    """
    Service to format lecture content into human-readable markdown
    """
    
    @staticmethod
    def format_lecture_to_markdown(
        topic: str,
        slides: List[Any],
        tone: str = "friendly",
        difficulty_level: str = "beginner"
    ) -> str:
        """
        Convert lecture slides into a structured markdown document
        
        Args:
            topic: Lecture topic/title
            slides: List of SlideInstruction objects
            tone: Lecture tone (friendly, formal, exam, story)
            difficulty_level: Target audience level (beginner, intermediate, advanced)
            
        Returns:
            Formatted markdown string
        """
        markdown_parts = []
        
        # Title
        markdown_parts.append(f"# {topic}\n")
        
        # Group slides by type
        intro_slides = [s for s in slides if s.slide_type == "title" or s.slide_number == 1]
        content_slides = [s for s in slides if s.slide_type == "content" and s.slide_number > 1]
        conclusion_slides = [s for s in slides if s.slide_type in ["conclusion", "summary"]]
        qa_slides = [s for s in slides if s.slide_type == "qa"]
        
        # Introduction Section
        if intro_slides:
            markdown_parts.append("## Introduction\n")
            for slide in intro_slides:
                if slide.script:
                    markdown_parts.append(f"{slide.script}\n")
                if slide.content and slide.content != slide.script:
                    markdown_parts.append(f"\n{slide.content}\n")
            markdown_parts.append("")
        
        # Main Content Section
        if content_slides:
            markdown_parts.append("## Main Content\n")
            
            # Add introductory sentence
            first_script = content_slides[0].script if content_slides and content_slides[0].script else ""
            if first_script:
                intro_sentence = first_script.split('.')[0] + '.'
                markdown_parts.append(f"{intro_sentence} Let's look at the key aspects:\n")
            
            # Process each content slide
            for slide in content_slides:
                # Format as bullet point with concept name
                concept_name = slide.title.replace("Slide ", "").strip()
                
                # Skip if title is too similar to main topic
                if concept_name.lower() not in topic.lower():
                    # Get description from content or script
                    description = ""
                    if slide.content:
                        # Clean up content
                        desc_lines = slide.content.strip().split('\n')
                        # Take first non-empty line
                        for line in desc_lines:
                            clean_line = line.strip().lstrip('-').lstrip('•').strip()
                            if clean_line and len(clean_line) > 10:
                                description = clean_line
                                break
                    
                    if not description and slide.script:
                        # Use first sentence from script
                        sentences = slide.script.split('.')
                        if len(sentences) > 0:
                            description = sentences[0].strip() + '.'
                    
                    # Add the bullet point
                    if description:
                        # Truncate if too long
                        if len(description) > 200:
                            description = description[:197] + "..."
                        markdown_parts.append(f"- **{concept_name}**: {description}\n")
                
                # Add code example if present
                if slide.code_example and slide.code_example.strip():
                    markdown_parts.append("\n**Code Example:**\n")
                    # Detect language from code content
                    code = slide.code_example.strip()
                    language = "javascript"
                    if "def " in code or "import " in code:
                        language = "python"
                    elif "public class" in code or "System.out" in code:
                        language = "java"
                    
                    markdown_parts.append(f"```{language}\n{code}\n```\n")
                
                # Add exercise if present
                if slide.exercise and slide.exercise.strip():
                    markdown_parts.append(f"\n**Practice Exercise:** {slide.exercise}\n")
            
            markdown_parts.append("")
        
        # Brief Summary Section
        markdown_parts.append("## Brief Summary\n")
        if conclusion_slides:
            for slide in conclusion_slides:
                if slide.script:
                    markdown_parts.append(f"{slide.script}\n")
                elif slide.content:
                    markdown_parts.append(f"{slide.content}\n")
        else:
            # Generate default summary
            markdown_parts.append(
                f"In this lecture, we have covered the essential concepts of {topic}. "
                "This knowledge will help you further study the material and apply it in practical situations.\n"
            )
        markdown_parts.append("")
        
        # Key Findings Section
        markdown_parts.append("## Key Findings\n")
        key_points = LectureMarkdownFormatter._extract_key_points(slides, topic)
        for point in key_points:
            markdown_parts.append(f"- {point}\n")
        markdown_parts.append("")
        
        # Q&A Section (if present)
        if qa_slides:
            markdown_parts.append("## Questions & Answers\n")
            for slide in qa_slides:
                if slide.content:
                    qa_content = slide.content.strip()
                    # Format Q&A properly
                    if '\n' in qa_content:
                        lines = qa_content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                if line.startswith(('Q:', 'Question:', 'Q.')):
                                    markdown_parts.append(f"\n**{line}**\n")
                                elif line.startswith(('A:', 'Answer:', 'A.')):
                                    markdown_parts.append(f"{line}\n")
                                else:
                                    markdown_parts.append(f"{line}\n")
                    else:
                        markdown_parts.append(f"{qa_content}\n")
                    markdown_parts.append("")
        
        return "\n".join(markdown_parts)
    
    @staticmethod
    def _extract_key_points(slides: List[Any], topic: str) -> List[str]:
        """
        Extract key takeaways from all slides
        """
        key_points = []
        
        # Extract unique concepts from content slides
        for slide in slides:
            if slide.slide_type in ["title", "qa"] or slide.slide_number == 1:
                continue
            
            # Add main concept from title
            if slide.title:
                concept = slide.title.replace("Slide ", "").strip()
                # Skip if concept is too similar to topic
                if concept.lower() not in topic.lower() and len(concept) > 3:
                    point = f"Understanding {concept.lower()}"
                    # Avoid duplicates
                    if point not in key_points:
                        key_points.append(point)
        
        # Add practice-related points
        has_code = any(hasattr(slide, 'code_example') and slide.code_example for slide in slides)
        has_exercises = any(hasattr(slide, 'exercise') and slide.exercise for slide in slides)
        
        if has_code:
            key_points.append("Practice with the provided code examples")
        
        if has_exercises:
            key_points.append("Complete the practice exercises to reinforce learning")
        
        # Add generic points if not enough specific ones
        if len(key_points) < 3:
            generic_points = [
                "Review and reinforce the core concepts discussed",
                "Apply learned principles through hands-on practice",
                "Explore additional resources for deeper understanding"
            ]
            for point in generic_points:
                if len(key_points) >= 5:
                    break
                if point not in key_points:
                    key_points.append(point)
        
        # Limit to top 5 points
        return key_points[:5]
    
    @staticmethod
    def _parse_qa(section_text: str) -> List[Dict[str, str]]:
        qa_pairs = []
        question = None
        answer = None

        for line in section_text.splitlines():
            line = line.strip()
            if line.lower().startswith(("q:", "question:")):
                question = line.split(":", 1)[1].strip()
            elif line.lower().startswith(("a:", "answer:")):
                answer = line.split(":", 1)[1].strip()
                if question:
                    qa_pairs.append({"question": question, "answer": answer})
                    question, answer = None, None
        return qa_pairs
    
    @staticmethod
    def parse_markdown_to_slides(markdown_text: str) -> List[Dict[str, Any]]:
        """
        Parse markdown lecture text and reconstruct slides
        (supports Key takeaway, Script, Image sections)
        """
        slides = []

        # Extract main topic
        topic_match = re.search(r"^# (.+)", markdown_text, flags=re.MULTILINE)
        topic = topic_match.group(1).strip() if topic_match else "Untitled Lecture"

        # Split sections by "##"
        raw_sections = re.split(r"^## ", markdown_text, flags=re.MULTILINE)
        raw_sections = [s.strip() for s in raw_sections if s.strip() and not s.startswith("# ")]

        slide_counter = 1

        for section in raw_sections:
            lines = section.splitlines()
            if not lines:
                continue

            section_title = lines[0].strip()
            section_body = "\n".join(lines[1:]).strip()

            # Extract optional fields
            script_match = re.search(r"\*\*Script\*\*:\s*(.+?)(?:\n\n|\Z)", section_body, flags=re.DOTALL)
            image_match = re.search(r"\*\*Image\*\*:\s*(.+?)(?:\n\n|\Z)", section_body, flags=re.DOTALL)
            takeaway_match = re.search(r"Key takeaway:\s*(.+)", section_body)

            script = script_match.group(1).strip() if script_match else None
            image_prompt = image_match.group(1).strip() if image_match else None
            takeaway = takeaway_match.group(1).strip() if takeaway_match else None

            # Remove extracted fields from main body
            clean_body = re.sub(r"\*\*Script\*\*:.+?(?:\n\n|\Z)", "", section_body, flags=re.DOTALL)
            clean_body = re.sub(r"\*\*Image\*\*:.+?(?:\n\n|\Z)", "", clean_body, flags=re.DOTALL)
            clean_body = re.sub(r"Key takeaway:.+", "", clean_body, flags=re.DOTALL).strip()

            # Identify slide type
            slide_type = "content"
            if section_title.lower().startswith("introduction"):
                slide_type = "title"
            elif section_title.lower().startswith(("summary", "you did it")):
                slide_type = "summary"
            elif section_title.lower().startswith(("key findings", "conclusion")):
                slide_type = "conclusion"

            # Create slide
            slide = {
                "slide_number": slide_counter,
                "title": section_title,
                "content": clean_body,
                "image_prompt": image_prompt,
                "slide_type": slide_type,
                "script": script or takeaway or None
            }
            slides.append(slide)
            slide_counter += 1

        return slides
