# Defense Analyst Chatbot

A local web app that provides a specialized defense analyst chatbot capable of processing defense-related research prompts and generating detailed, insightful responses.

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

### Easiest: Run with Docker Compose

You can run both the backend (FastAPI) and frontend (Next.js) together using Docker Compose. Place your API keys in a `.env` file in the project root first.

**Build and start all services**

From the project root, run:
```sh
docker-compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000)

**Stop all services**
```sh
docker-compose down
```

### Manual: Run Backend and Frontend Separately

**Backend:**
```bash
cd app
pip install -r ../requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000)

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
- "What (the fuck) does Palantir do for the government?" (pls take the swear word out btw)

It will not work if you ask it to do something that is not related to defense or government, such as "Where is the best ice cream in Boston?"

## Project Structure

```
defense-chatbot/
├── app/                       # Backend FastAPI application
│   ├── __init__.py
│   ├── config.py              # Configuration and environment variables
│   ├── crawler.py             # Firecrawl integration
│   ├── main.py                # Main FastAPI application
│   └── test_crawler.py        # Backend unit tests
├── frontend/                  # Next.js frontend
│   ├── components/            # React components
│   ├── pages/                 # Next.js pages
│   ├── styles/                # CSS styles
│   ├── types/                 # TypeScript type definitions
│   ├── package.json           # Frontend dependencies
│   ├── package-lock.json      # Frontend lock file
│   └── Dockerfile             # Frontend container config
├── app/Dockerfile             # Backend container config
├── docker-compose.yaml        # Compose file for backend & frontend
├── requirements.txt           # Python dependencies
├── .env.example               # Example environment variables
├── .env                       # (gitignored) Actual environment variables
└── README.md                  # This file
```

## License

This project is intended for educational and research purposes.
