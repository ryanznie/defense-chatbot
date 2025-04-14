"""
Module for handling web crawling and data collection functionality.
Integrates with Firecrawl for defense-related data retrieval.
"""
import httpx
from typing import Dict, List, Any, Optional
import json
import logging
from . import config

# Configure logging
logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

class DefenseCrawler:
    """
    A wrapper class for Firecrawl functionality to retrieve defense-related data.
    This class provides methods to search, crawl, and extract information from defense sources.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the crawler with API key and base URL."""
        self.api_key = api_key or config.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v1"  # Example URL, replace with actual Firecrawl API URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for defense-related information based on a query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results with relevant defense information,
            including links and sources
        """
        try:
            # If this is a simulation or placeholder, return mock data
            if self.api_key == "your-firecrawl-api-key":
                logger.warning("Using simulated data as no valid API key provided")
                mock_data = self._get_mock_data(query)
                return {
                    "results": mock_data,
                    "links": [item["url"] for item in mock_data if "url" in item],
                    "sources": [{
                        "title": item["title"],
                        "url": item["url"],
                        "source": item.get("source", "Simulated Source")
                    } for item in mock_data if "url" in item]
                }
            
            # Actual implementation would use the Firecrawl API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "limit": limit
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract results and add links and sources
                results = data.get("results", [])
                return {
                    "results": results,
                    "links": [item["url"] for item in results if "url" in item],
                    "sources": [{
                        "title": item.get("title", "Unknown Title"),
                        "url": item.get("url", ""),
                        "source": item.get("source", item.get("domain", "Unknown Source"))
                    } for item in results if "url" in item]
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def deep_research(self, query: str) -> Dict[str, Any]:
        """
        Perform deep research on a defense-related topic using Firecrawl.
        Args:
            query: Research query string
        Returns:
            Dictionary containing research results and analysis with structure:
            {
                "summary": "Detailed analysis",
                "key_findings": ["finding1", "finding2"],
                "sources": [{"url": "...", "title": "...", "description": "..."}]
            }
        """
        import asyncio
        logger.info(f"Starting deep research on: {query}")
        try:
            # If this is a simulation or placeholder, return mock data
            if self.api_key == "your-firecrawl-api-key":
                logger.warning("Using simulated data as no valid API key provided")
                return self._get_mock_research_data(query)

            research_params = {
                "query": query,
                "maxDepth": 5,           # Number of research iterations
                "timeLimit": 240,        # Time limit in seconds
                "maxUrls": 20            # Maximum number of URLs to analyze
            }
            logger.info(f"Deep research parameters: {research_params}")

            async with httpx.AsyncClient() as client:
                # Step 1: Start the deep research job
                post_resp = await client.post(
                    f"{self.base_url}/deep-research",
                    headers=self.headers,
                    json=research_params,
                    timeout=30.0
                )
                logger.info(f"Firecrawl POST response: {post_resp.text}")
                post_resp.raise_for_status()
                post_data = post_resp.json()
                if not post_data.get("success", False):
                    logger.error(f"Firecrawl API reported failure on POST: {post_data}")
                    return {
                        "summary": f"Error starting research on '{query}'.",
                        "key_findings": [],
                        "sources": []
                    }
                job_id = post_data.get("id") or post_data.get("job_id") or post_data.get("data", {}).get("id")
                if not job_id:
                    logger.error(f"No job_id returned from Firecrawl: {post_data}")
                    return {
                        "summary": f"No job_id returned for research on '{query}'.",
                        "key_findings": [],
                        "sources": []
                    }
                logger.info(f"Deep research job_id: {job_id}")

                # Step 2: Poll for job completion
                poll_url = f"{self.base_url}/deep-research/{job_id}"
                poll_interval = 3  # seconds
                poll_timeout = 300 # seconds
                elapsed = 0
                while elapsed < poll_timeout:
                    poll_resp = await client.get(
                        poll_url,
                        headers=self.headers,
                        timeout=30.0
                    )
                    logger.info(f"Polling job {job_id}: {poll_resp.text}")
                    poll_resp.raise_for_status()
                    poll_data = poll_resp.json()
                    if not poll_data.get("success", False):
                        logger.error(f"Firecrawl API reported failure on GET: {poll_data}")
                        return {
                            "summary": f"Error polling research on '{query}'.",
                            "key_findings": [],
                            "sources": []
                        }
                    data = poll_data.get("data", {})
                    status = data.get("status") or poll_data.get("status")
                    if status == "completed":
                        logger.info(f"Job {job_id} completed.")
                        return {
                            "summary": data.get("finalAnalysis", f"No analysis available for '{query}'."),
                            "key_findings": self._extract_key_findings(data.get("finalAnalysis", "")),
                            "sources": data.get("sources", [])
                        }
                    elif status == "failed":
                        logger.error(f"Job {job_id} failed: {poll_data}")
                        return {
                            "summary": f"Research job failed for '{query}'.",
                            "key_findings": [],
                            "sources": []
                        }
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
                logger.error(f"Polling timed out for job {job_id}")
                return {
                    "summary": f"Polling timed out for research on '{query}'.",
                    "key_findings": [],
                    "sources": []
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during deep research: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error during deep research: {e}")
            return {"error": str(e)}

    
    def _get_mock_data(self, query: str) -> List[Dict[str, Any]]:
        """Generate mock data for simulation purposes."""
        defense_topics = {
            "golden dome": [
                {
                    "title": "Golden Dome Defense Initiative",
                    "url": "https://example.gov/defense/golden-dome",
                    "description": "The Golden Dome initiative represents a collaborative effort between multiple program executive officers to enhance missile defense capabilities.",
                    "source": "Defense Department Archives"
                },
                {
                    "title": "Program Executive Officers in the Golden Dome Program",
                    "url": "https://example.gov/defense/golden-dome/officers",
                    "description": "Information about the program executive officers responsible for various aspects of the Golden Dome effort, including Air Force, Navy and Army liaisons.",
                    "source": "Military Technology Review"
                }
            ],
            "missile defense": [
                {
                    "title": "Next Generation Missile Defense Systems",
                    "url": "https://example.gov/defense/missile-systems",
                    "description": "Analysis of current and upcoming missile defense technologies deployed across various defense departments.",
                    "source": "Defense Industry Report"
                }
            ],
            "defense budget": [
                {
                    "title": "FY2025 Defense Budget Allocations",
                    "url": "https://example.gov/budget/defense/2025",
                    "description": "Breakdown of the defense budget allocations for fiscal year 2025, including major program funding.",
                    "source": "Congressional Budget Office"
                }
            ]
        }
        
        # Return relevant mock data or generic results
        for key, data in defense_topics.items():
            if key.lower() in query.lower():
                return data
                
        # Default generic response if no specific matches
        return [
            {
                "title": f"Defense Analysis: {query}",
                "url": "https://example.gov/defense/analysis",
                "description": f"General information related to '{query}' in the defense context.",
                "source": "Defense Information Database"
            }
        ]
    
    def _extract_key_findings(self, analysis: str) -> List[str]:
        """Extract key findings from analysis text."""
        # Simple extraction based on numbered or bulleted lists
        findings = []
        for line in analysis.split("\n"):
            line = line.strip()
            # Match numbered points (1. Point) or bullet points (- Point)
            if (line.startswith("- ") or 
                line.startswith("* ") or 
                (len(line) > 2 and line[0].isdigit() and line[1] == '.' and line[2] == ' ')):
                findings.append(line[2:].strip())
        
        # If no structured points found, create some generic ones
        if not findings and analysis:
            # Take first few sentences as key findings
            sentences = [s.strip() for s in analysis.split('.') if s.strip()]
            findings = sentences[:min(3, len(sentences))]
            
        return findings
    
    def _get_mock_research_data(self, query: str) -> Dict[str, Any]:
        """Generate mock research data for simulation purposes."""
        # This format matches our internal representation after Firecrawl API processing
        # Golden Dome specific response
        if "golden dome" in query.lower():
            return {
                "summary": "The Golden Dome initiative is a multi-branch defense program focused on integrated missile defense systems. It involves collaboration between Army, Navy, and Air Force program executive officers.",
                "key_findings": [
                    "Currently led by three program executive officers: Gen. Sarah Williams (Air Force), Adm. James Chen (Navy), and Col. Robert Garcia (Army)",
                    "Market size estimated at $4.2 billion for FY2025, with projected growth to $6.8 billion by FY2027",
                    "Primary mission systems include radar integration, counter-hypersonic capabilities, and satellite communications"
                ],
                "sources": [
                    {
                        "title": "Defense Department Official Reports", 
                        "url": "https://example.gov/reports/golden-dome", 
                        "description": "Official Department of Defense documentation about the Golden Dome initiative"
                    },
                    {
                        "title": "Congressional Testimony on Defense Programs", 
                        "url": "https://example.gov/congress/defense/testimony", 
                        "description": "Testimony from military officials about the Golden Dome program"
                    },
                    {
                        "title": "Market Analysis of Defense Programs 2025", 
                        "url": "https://example.gov/market/defense/2025", 
                        "description": "Financial and market projections for the Golden Dome initiative"
                    }
                ]
            }
        
        # Generic research response
        return {
            "summary": f"Analysis of '{query}' indicates several relevant defense applications and programs.",
            "key_findings": [
                f"Related defense initiatives show increasing funding in the 2025-2026 period",
                f"Technology applications primarily focus on {query.split()[0] if query.split() else 'technology'} integration with existing systems",
                f"International cooperation agreements exist with NATO allies on {query} development"
            ],
            "sources": [
                {
                    "title": "Defense Technology Review", 
                    "url": "https://example.gov/tech-review", 
                    "description": f"Technical analysis of {query} applications in defense"
                },
                {
                    "title": "Military Strategic Analysis", 
                    "url": "https://example.gov/strategic-analysis", 
                    "description": f"Strategic implications of {query} for military operations"
                },
                {
                    "title": "International Defense Cooperation Report", 
                    "url": "https://example.gov/international/defense", 
                    "description": f"Overview of international collaboration on {query}"
                }
            ]
        }
