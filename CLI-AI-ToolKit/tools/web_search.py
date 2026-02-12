"""Web search tool using DuckDuckGo search and OpenAI for analysis."""
from openai import OpenAI
from config import OPENAI_API_KEY
import requests

try:
    from ddgs import DDGS
except ImportError:
    print("Error: ddgs not installed")
    print("Run: pip install ddgs")
    raise

client = OpenAI(api_key=OPENAI_API_KEY)


def _perform_web_search(query: str, num_results: int = 5) -> list:
    """
    Perform actual web search using DuckDuckGo.
    
    Args:
        query: Search query
        num_results: Number of results to return
    
    Returns:
        List of search results with title, URL, and snippet
    """
    try:
        ddgs = DDGS()
        results = list(ddgs.text(
            query,
            max_results=num_results
        ))
        
        search_results = []
        for result in results:
            if result:
                search_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", "") or result.get("url", ""),
                    "snippet": result.get("body", "") or result.get("snippet", "")
                })
        
        return search_results
        
    except Exception as e:
        print(f"Error performing web search: {str(e)}")
        return []


def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform web search and get brief ChatGPT analysis of current information.
    
    Args:
        query: Search query string
        max_results: Maximum number of search results to include (default: 5)
    
    Returns:
        Brief analysis of the search results with sources
    """
    try:
        # Perform actual web search
        search_results = _perform_web_search(query, max_results)
        
        if not search_results:
            return f"No search results found for: {query}"
        
        # Format search results for GPT
        results_text = "Recent Search Results:\n"
        for i, result in enumerate(search_results, 1):
            results_text += f"\n{i}. {result['title']}\n"
            results_text += f"   URL: {result['url']}\n"
            results_text += f"   {result['snippet'][:200]}...\n"
        
        # Send to ChatGPT for brief synthesis
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on these recent web search results about "{query}", provide a BRIEF (2-3 paragraphs) summary of the latest information:

{results_text}

Be concise and focus on the most important recent developments."""
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Format output with sources
        analysis = response.choices[0].message.content
        
        # Add sources section
        sources_section = "\n\n" + "="*60 + "\n📚 SOURCES YOU CAN VISIT:\n" + "="*60 + "\n"
        for i, result in enumerate(search_results, 1):
            sources_section += f"\n{i}. {result['title']}\n"
            sources_section += f"   🔗 {result['url']}\n"
        
        return analysis + sources_section
            
    except Exception as e:
        raise Exception(f"Web search failed: {str(e)}")


if __name__ == "__main__":
    # Example usage
    result = web_search("Latest developments in AI 2024")
    print(result)
