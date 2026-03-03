"""Website screenshot and design analysis tool using Playwright and OpenAI Vision."""
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

from openai import OpenAI
from config import OPENAI_API_KEY, SCREENSHOTS_DIR

# Configure OpenAI API
client = OpenAI(api_key=OPENAI_API_KEY)


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
    Send a website screenshot to OpenAI GPT-4o for design analysis.
    
    Args:
        screenshot_path: Path to the screenshot image
        analysis_prompt: Custom analysis prompt (optional)
    
    Returns:
        String containing GPT-4o's design feedback
    """
    try:
        # Read and encode image
        with open(screenshot_path, "rb") as img_file:
            image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
        
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
        
        # Create the request with image using GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_str = str(e).lower()
        if "api_key" in error_str or "invalid" in error_str or "401" in error_str:
            raise Exception(
                f"❌ OpenAI API Error: Invalid or expired API key.\n"
                f"Please verify your OPENAI_API_KEY in .env file.\n"
                f"Get a valid key from: https://platform.openai.com/api-keys\n"
                f"Details: {str(e)}"
            )
        else:
            raise Exception(f"Website analysis failed: {str(e)}")


async def screenshot_and_analyze(url: str, analysis_prompt: str = None) -> dict:
    """
    Screenshot a website and get design feedback from GPT-4o (async wrapper).
    
    Args:
        url: Website URL to analyze
        analysis_prompt: Custom analysis prompt (optional)
    
    Returns:
        Dictionary containing screenshot path and analysis feedback
    """
    try:
        # Take screenshot
        print(f"📸 Taking screenshot of {url}...")
        screenshot_path = await take_screenshot(url)
        print(f"✅ Screenshot saved to: {screenshot_path}")
        
        # Analyze with OpenAI GPT-4o
        print(f"🤖 Sending to OpenAI GPT-4o for analysis...")
        feedback = analyze_website_design(screenshot_path, analysis_prompt)
        print(f"✅ Analysis complete!")
        
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
