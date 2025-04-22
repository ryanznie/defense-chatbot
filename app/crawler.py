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
        self.base_url = "https://api.firecrawl.dev/v1"
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
            # Firecrawl API
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
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return {"error": str(e)}
    
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
        # Guardrail: Only allow defense/government-related queries
        if not self._is_defense_related(query):
            logger.warning(f"Query not related to defense or government: {query}")
            return {
                "summary": "Sorry, I can only assist with defense or government-related research questions.",
                "key_findings": [],
                "sources": []
            }
        try:
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
                    "summary": f"Polling timed out for research on '{query[:100]}'.",
                    "key_findings": [],
                    "sources": []
                }
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during deep research: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error during deep research: {e}")
            return {"error": str(e)}


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
    

    def _is_defense_related(self, query: str) -> bool:
        """Return True if the query is related to defense or government topics."""
        keywords = [
            # Existing keywords
            "defense", "military", "dod", "government", "program executive officer", "market size",
            "mission system", "contract", "army", "navy", "air force", "golden dome", "homeland security",
            "intelligence", "federal", "agency", "warfighter", "missile", "weapons", "procurement",
            "department of defense", "usaf", "usn", "usmc", "us army", "us navy", "us air force",
            "national guard", "veteran", "combat", "strategic", "warfighting", "defence", "counterterrorism",
            "nato", "allies", "dhs", "congress", "senate", "military base", "military spending", "defense budget",
            "defense technology", "defense contractor", "defense acquisition", "defense program",
            # Expanded defense/government/security keywords
            "darpa", "nsa", "cia", "fbi", "space force", "defense industry", "military intelligence",
            "armed forces", "homeland", "security clearance", "clearance", "classified", "unclassified",
            "public sector", "doe", "doj", "dos", "state department", "defense innovation", "defense logistics",
            "military research", "military technology", "armed services", "defense policy", "defense spending",
            "military operations", "force structure", "defense review", "joint chiefs", "combatant command",
            "socom", "centcom", "pacom", "eucom", "africom", "northcom", "spacecom", "indopacom",
            "defense grant", "defense r&d", "defense funding", "military contract", "military supplier",
            "military procurement", "military training", "military exercise", "military doctrine",
            "military readiness", "military logistics", "military support", "military alliance", "military assistance",
            "military aid", "military deployment", "military force", "military personnel", "military veteran",
            "military reserve", "military retiree", "military spouse", "military dependent", "military family",
            "palantir", "anduril", 'budget'
        ]
        q = query.lower()
        return any(kw in q for kw in keywords)
