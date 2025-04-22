"""
Main FastAPI application for the defense analyst chatbot.
Provides API endpoints for chat functionality and integrates OpenAI and Firecrawl.
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import openai
import asyncio
import uuid
import time

from . import config
from .crawler import DefenseCrawler

# Configure logging
logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

# Configure OpenAI API
openai.api_key = config.OPENAI_API_KEY

# Initialize FastAPI application
app = FastAPI(
    title="Defense Analyst Chatbot API",
    description="API for a defense research assistant chatbot that integrates with OpenAI and Firecrawl",
    version="1.0.0"
)

@app.get("/healthz", tags=["health"])
def healthz():
    """Health check endpoint for container orchestration and monitoring."""
    return JSONResponse(content={"status": "ok"})

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the defense crawler
defense_crawler = DefenseCrawler()

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    prompt: str
    conversation_id: Optional[str] = None
    include_research_data: bool = True

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    conversation_id: str
    research_data: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None

# In-memory cache for conversations (would use a proper database in production)
conversation_cache = {}

async def get_openai_response(prompt: str, research_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Get a response from the OpenAI API based on the prompt and research data.
    
    Args:
        prompt: User's research prompt
        research_data: Optional research data to include in the context
        
    Returns:
        Generated response from OpenAI
    """
    try:
        # Prepare system message with context about being a defense analyst assistant
        system_message = """
        You are a specialized defense analyst chatbot designed to provide detailed and insightful responses
        to defense-related research queries. Your responses should be detailed, accurate, and showcase
        deep understanding of defense topics, programs, and technologies. 
        Do not include any personal opinions, and DO NOT answer any questions that are not related to defense and government.
        """
        
        # Prepare the messages for the OpenAI chat completion
        messages = [{"role": "system", "content": system_message}]
        
        # Add research data if available
        if research_data:
            # Extract sources information
            sources_info = research_data.get('sources', [])
            
            # Format sources for the context
            formatted_sources = "\n".join([f"- {source.get('title', 'Unknown')}: {source.get('url', '')}" 
                                     + (f" - {source.get('description', '')}" if source.get('description') else "")
                                     for source in sources_info]) if sources_info else "No sources available"
            
            research_context = f"""
            I've gathered the following research information to help with this query:
            
            Summary: {research_data.get('summary', 'No summary available')}
            
            Key Findings:
            {' '.join(['- ' + finding for finding in research_data.get('key_findings', [])])}
            
            Relevant Sources:
            {formatted_sources}
            
            Please incorporate this information into your response when relevant. Make sure to reference the sources when appropriate.
            """
            messages.append({"role": "system", "content": research_context})
        
        # Add the user's prompt
        messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI API
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=config.OPENAI_MODEL,
            messages=messages,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE
        )
        
        # Extract and return the response text
        return response['choices'][0]['message']['content'].strip()
        
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Defense Analyst Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Submit a research prompt for analysis"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request and return a response.
    
    Endpoint accepts a research prompt, optionally performs web research using Firecrawl,
    and generates a detailed response using OpenAI.
    """
    try:
        # Generate or use the existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"Processing chat request for conversation {conversation_id}")
        
        # Initialize response data
        research_data = None
        sources = []
        
        # Perform research if requested
        if request.include_research_data:
            try:
                # Get research data from Firecrawl
                research_data = await defense_crawler.deep_research(request.prompt)
                
                # Extract sources if available
                sources = research_data.get("sources", [])
                
                logger.info(f"Research data retrieved with {len(sources)} sources for prompt: {request.prompt[:50]}...")
            except Exception as e:
                logger.warning(f"Error retrieving research data: {e}")
                # Continue without research data if there's an error
                research_data = None
                sources = []
                
        # Generate response using OpenAI
        response_text = await get_openai_response(request.prompt, research_data)
        
        # Store conversation in cache (would use a database in production)
        conversation_cache[conversation_id] = {
            "last_prompt": request.prompt,
            "last_response": response_text,
            "timestamp": time.time()
        }
        
        # Return the response
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            research_data=research_data,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "api_keys": {
        "openai": "configured" if config.OPENAI_API_KEY != "your-openai-api-key" else "not configured",
        "firecrawl": "configured" if config.FIRECRAWL_API_KEY != "your-firecrawl-api-key" else "not configured"
    }}

# Run the application with Uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
