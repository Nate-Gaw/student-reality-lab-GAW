"""Website screenshot and design analysis tool using Playwright and Gemini."""
import base64
from pathlib import Path
from datetime import datetime
import asyncio

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright not installed. Please run: pip install playwright")
    print("Then run: playwright install")
    raise

from google.genai import Client
from config import GEMINI_API_KEY, SCREENSHOTS_DIR

# Configure Gemini API
client = Client(api_key=GEMINI_API_KEY)


async def take_screenshot(url: str, full_page: bool = True) -> str:
    """
    Take a screenshot of a website using Playwright.
    
    Args:
        url: Website URL to screenshot
        full_page: Whether to capture full page or viewport (default: True)
    
    Returns:
        Path to saved screenshot file
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # Navigate to URL with shorter timeout and faster load strategy
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait a brief moment for any lazy-loaded content
            await page.wait_for_timeout(2000)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = SCREENSHOTS_DIR / filename
            
            # Take screenshot
            await page.screenshot(path=str(filepath), full_page=full_page)
            
            return str(filepath)
        finally:
            await browser.close()


def analyze_website_design(screenshot_path: str, analysis_prompt: str = None) -> str:
    """
    Send a website screenshot to Gemini for design analysis.
    
    Args:
        screenshot_path: Path to the screenshot image
        analysis_prompt: Custom analysis prompt (optional)
    
    Returns:
        String containing Gemini's design feedback
    """
    try:
        # Read and encode image
        with open(screenshot_path, "rb") as img_file:
            image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
        
        # Determine MIME type
        file_ext = Path(screenshot_path).suffix.lower()
        mime_type = "image/png" if file_ext == ".png" else "image/jpeg"
        
        # Prepare the message
        if analysis_prompt is None:
            analysis_prompt = """Please analyze this website screenshot and provide detailed feedback on:

1. **Visual Design Quality**: Color scheme, typography, layout consistency
2. **User Experience**: Navigation clarity, call-to-action visibility, spacing
3. **Accessibility**: Contrast ratios, text readability, responsive considerations
4. **Modern Standards**: Does it follow current web design trends?
5. **Strengths**: What works well in the design?
6. **Improvements**: What could be improved?
7. **Overall Score**: Rate the design from 1-10 with justification

Please be specific and constructive in your feedback."""
        
        # Create the prompt with image
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_data
                            }
                        },
                        {
                            "text": analysis_prompt
                        }
                    ]
                }
            ]
        )
        
        return response.text
        
    except Exception as e:
        raise Exception(f"Website analysis failed: {str(e)}")


async def screenshot_and_analyze(url: str, analysis_prompt: str = None) -> dict:
    """
    Screenshot a website and get design feedback from Gemini (async wrapper).
    
    Args:
        url: Website URL to analyze
        analysis_prompt: Custom analysis prompt (optional)
    
    Returns:
        Dictionary containing screenshot path and analysis feedback
    """
    try:
        # Take screenshot
        screenshot_path = await take_screenshot(url)
        
        # Analyze with Gemini
        feedback = analyze_website_design(screenshot_path, analysis_prompt)
        
        return {
            "url": url,
            "screenshot_path": screenshot_path,
            "analysis": feedback
        }
    except Exception as e:
        raise Exception(f"Screenshot and analysis failed: {str(e)}")


def run_website_analysis(url: str, analysis_prompt: str = None) -> dict:
    """
    Synchronous wrapper for screenshot_and_analyze.
    
    Args:
        url: Website URL to analyze
        analysis_prompt: Custom analysis prompt (optional)
    
    Returns:
        Dictionary containing screenshot path and analysis feedback
    """
    return asyncio.run(screenshot_and_analyze(url, analysis_prompt))


if __name__ == "__main__":
    # Example usage
    result = run_website_analysis("https://www.example.com")
    print(f"Screenshot saved to: {result['screenshot_path']}")
    print("\nDesign Analysis:")
    print(result['analysis'])
