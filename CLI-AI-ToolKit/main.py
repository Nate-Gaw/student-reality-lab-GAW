"""Main CLI entry point for the AI Toolkit."""
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools import web_search, generate_image, run_website_analysis


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="AI Toolkit - Web Search, Image Generation, and Website Analysis"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Tool to use")
    
    # Web Search Command
    search_parser = subparsers.add_parser("search", help="Perform web search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results (default: 5)"
    )
    
    # Image Generation Command
    image_parser = subparsers.add_parser("generate-image", help="Generate image with DALL-E")
    image_parser.add_argument("prompt", help="Image description prompt")
    image_parser.add_argument(
        "--size",
        default="1024x1024",
        choices=["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"],
        help="Image size (default: 1024x1024)"
    )
    image_parser.add_argument(
        "--quality",
        default="standard",
        choices=["standard", "hd"],
        help="Image quality (default: standard)"
    )
    image_parser.add_argument(
        "--num",
        type=int,
        default=1,
        help="Number of images (default: 1)"
    )
    
    # Website Analysis Command
    website_parser = subparsers.add_parser("analyze-website", help="Screenshot and analyze website design")
    website_parser.add_argument("url", help="Website URL to analyze")
    website_parser.add_argument(
        "--prompt",
        help="Custom analysis prompt (optional)"
    )
    
    args = parser.parse_args()
    
    if args.command == "search":
        print(f"🔍 Searching for: {args.query}\n")
        result = web_search(args.query, max_results=args.max_results)
        print(result)
        
    elif args.command == "generate-image":
        print(f"🎨 Generating image: {args.prompt}\n")
        images = generate_image(
            prompt=args.prompt,
            size=args.size,
            quality=args.quality,
            num_images=args.num
        )
        for img in images:
            print(f"✅ Generated: {img['filename']}")
            print(f"   Location: {img['filepath']}")
            print(f"   Revised Prompt: {img['revised_prompt']}\n")
            
    elif args.command == "analyze-website":
        print(f"📸 Analyzing website: {args.url}\n")
        result = run_website_analysis(args.url, args.prompt)
        print(f"Screenshot saved to: {result['screenshot_path']}\n")
        print("Design Analysis:")
        print(result['analysis'])
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
