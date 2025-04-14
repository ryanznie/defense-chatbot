# Defense Analyst Chatbot

A local web application that provides a specialized defense analyst chatbot capable of processing defense-related research prompts and generating detailed, insightful responses.

## Project Architecture

This project consists of two main components:

1. **Backend (FastAPI)**: Handles chat requests, integrates with OpenAI for generating responses, and uses Firecrawl for defense-related data retrieval.
2. **Frontend (Next.js)**: Provides a user-friendly chat interface for submitting research prompts and displaying results.

## Prerequisites

- Python 3.7 or later
- Node.js 14.x or later
- npm or yarn

## Setup Instructions

### Backend Setup

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root by copying the `.env.example` file:
   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file with your API keys:
   ```
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4
   MAX_TOKENS=2000
   TEMPERATURE=0.7
   FIRECRAWL_API_KEY=your-firecrawl-api-key
   CORS_ORIGINS=http://localhost:3000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

## Running the Application

### Start the Backend Server

1. From the project root, run:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be available at http://localhost:8000

2. You can access the API documentation at http://localhost:8000/docs

### Start the Frontend Development Server

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The frontend will be available at http://localhost:3000

## Features

- Advanced defense research capabilities
- Integration with OpenAI for detailed response generation
- Real-time data retrieval using Firecrawl
- Markdown rendering for rich text responses
- Source attribution for research data
- Conversation history tracking

## Example Usage

The chatbot can handle various defense-related queries, such as:
- "What are the program executive officers related to the Golden Dome effort?"
- "What is the market size of the Golden Dome effort by mission system?"
- "Explain the latest developments in missile defense technologies"
- "Analyze the FY2025 defense budget allocations for cyber initiatives"

## Project Structure

```
defense-chatbot/
├── app/                  # Backend FastAPI application
│   ├── __init__.py
│   ├── config.py         # Configuration and environment variables
│   ├── crawler.py        # Firecrawl integration
│   └── main.py           # Main FastAPI application
├── frontend/             # Next.js frontend
│   ├── components/       # React components
│   ├── pages/            # Next.js pages
│   ├── styles/           # CSS styles
│   └── types/            # TypeScript type definitions
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## License

This project is intended for educational and research purposes.
