# Higgsfield Lecture Generator API

A FastAPI backend for generating lecture presentations using Qwen LLM and Higgsfield image generation APIs. This project is built for the Higgsfield Hackathon 2025.

## Features

- **Lecture Generation**: Create complete lecture presentations from any topic
- **LLM Integration**: Uses Qwen API (DashScope) for intelligent content generation
- **Image Generation**: Integrates with Higgsfield API for slide image generation
- **Flexible Configuration**: Customizable duration, difficulty level, and target audience
- **RESTful API**: Clean, well-documented endpoints

## Project Structure

```
higgsfield/
├── app/
│   ├── routes/
│   │   ├── text_route.py          # Text generation routes
│   │   ├── image_route.py         # Image generation routes
│   │   └── lecture_route.py       # Lecture generation routes
│   ├── src/
│   │   ├── endpoints/
│   │   │   ├── text_endpoints.py
│   │   │   ├── image_endpoints.py
│   │   │   └── lecture_endpoints.py
│   │   ├── models/
│   │   │   └── model.py           # Pydantic models
│   │   └── services/
│   │       └── qwen_service.py    # Qwen API integration
│   └── utils/
│       └── db.py
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── test.py                       # Qwen API test script
├── test_lecture_api.py           # API test script
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
# Higgsfield API credentials
HF_API_KEY=your_higgsfield_api_key_here
HF_SECRET=your_higgsfield_secret_here

# Qwen/DashScope API credentials
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

### 3. Get API Keys

#### Higgsfield API
1. Go to https://cloud.higgsfield.ai/promocode
2. Sign in and apply your $100 coupon
3. Create API key at https://cloud.higgsfield.ai/api-keys

#### Qwen API (DashScope)
1. Sign up at https://dashscope.aliyun.com/
2. Get your API key from the dashboard

### 4. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Lecture Generation

#### POST `/lecture/generate-lecture`

Generate a complete lecture presentation.

**Request Body:**
```json
{
  "topic": "Introduction to Machine Learning",
  "duration_minutes": 15,
  "difficulty_level": "beginner",
  "target_audience": "students"
}
```

**Response:**
```json
{
  "status": 1,
  "topic": "Introduction to Machine Learning",
  "duration_minutes": 15,
  "total_slides": 6,
  "lecture_script": "Welcome to our lecture on Machine Learning...",
  "slides": [
    {
      "slide_number": 1,
      "title": "Introduction to Machine Learning",
      "content": "Brief content for this slide...",
      "image_prompt": "Professional slide showing introduction to Machine Learning, clean design, educational style",
      "slide_type": "title"
    }
  ]
}
```

#### GET `/lecture/{topic}`

Quick lecture generation with query parameters.

**Example:** `GET /lecture/quantum-computing?duration=20&difficulty=advanced`

### Text Generation

#### POST `/lecture/generate-text`

Simple text generation using Qwen API.

**Parameters:**
- `prompt` (string): The text prompt

### Image Generation

#### POST `/generate-image`

Generate images using Higgsfield API.

**Request Body:**
```json
{
  "text": "A beautiful sunset over mountains"
}
```

## Usage Examples

### Python Client

```python
import requests

# Generate a lecture
response = requests.post(
    "http://localhost:8000/lecture/generate-lecture",
    json={
        "topic": "Introduction to AI",
        "duration_minutes": 10,
        "difficulty_level": "beginner"
    }
)

lecture = response.json()
print(f"Generated {lecture['total_slides']} slides for: {lecture['topic']}")
```

### cURL

```bash
curl -X POST "http://localhost:8000/lecture/generate-lecture" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Blockchain Technology",
    "duration_minutes": 20,
    "difficulty_level": "intermediate"
  }'
```

## Testing

Run the test script to verify everything works:

```bash
python test_lecture_api.py
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps for Frontend Integration

The generated lecture data can be used to:

1. **Display slides** with titles and content
2. **Generate images** using the `image_prompt` for each slide
3. **Create audio** from the `lecture_script` using TTS
4. **Compose video** by combining slides, audio, and avatar

## Hackathon Track

This project is built for the **SWE Track** at Higgsfield Hackathon 2025, focusing on:
- Fast, reliable execution
- Production-ready code
- Real feature implementation
- Multimodal API integration

## License

Built for Higgsfield Hackathon 2025
