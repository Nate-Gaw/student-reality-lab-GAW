# 🤖 AI Toolkit

A modular Python toolkit for AI-powered tasks including web search, image generation, and website design analysis.

## 📋 Features

### 1. 🔍 Web Search Tool
- Uses OpenAI API with web search capabilities
- Conducts real-time research on any topic
- Returns current, up-to-date information (bypasses the AI knowledge cutoff)
- Perfect for staying informed on latest developments

**Cost:** Free (uses standard GPT-4 API calls)

### 2. 🎨 Image Generation Tool
- Uses OpenAI's DALL-E 3 for professional image generation
- Multiple size options (256x256 to 1792x1024)
- HD quality option for higher-fidelity images
- Auto-saves images with timestamps
- Perfect for quickly generating web assets

**Cost:** ~$0.04 (standard) to $0.20 (HD) per image

### 3. 📸 Website Screenshot & Design Analysis
- Takes screenshots of any website using Playwright
- Automatically sends screenshots to Google Gemini for AI analysis
- Provides detailed feedback on:
  - Visual design quality
  - User experience
  - Accessibility
  - Modern design standards
  - Specific improvement suggestions

**Cost:** Free (uses Gemini API which has free tier)

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+
- OpenAI API key (OpenAI account)
- Google Gemini API key (Google Cloud account)

### Installation

1. **Set up environment variables**
   - Verify `.env` file exists in the project root with:
     ```
     OPENAI_API_KEY=your_key_here
     GEMINI_API_KEY=your_key_here
     ```

2. **Run setup script**
   ```bash
   python setup.py
   ```
   This will:
   - Install all Python dependencies
   - Configure Playwright and download browsers

## 📖 Usage

### Web Search
```bash
python main.py search "your search query"

# With custom result count
python main.py search "AI trends 2024" --max-results 10
```

### Generate Images
```bash
# Basic usage (default: 1024x1024, standard quality)
python main.py generate-image "a modern website header"

# Advanced options
python main.py generate-image "website design" --size 1792x1024 --quality hd --num 2
```

**Size options:** 256x256, 512x512, 1024x1024, 1792x1024, 1024x1792
**Quality options:** standard (default), hd

### Analyze Website Design
```bash
# Basic analysis with default criteria
python main.py analyze-website https://example.com

# Custom analysis prompt
python main.py analyze-website https://example.com --prompt "Focus on mobile responsiveness"
```

## 📁 Project Structure

```
CLI-AI-ToolKit/
├── .env                          # API keys (already configured)
├── config.py                     # Configuration & API key loading
├── main.py                       # CLI entry point
├── setup.py                      # Setup script
├── requirements.txt              # Python dependencies
├── tools/
│   ├── __init__.py              # Tools package
│   ├── web_search.py            # Web search implementation
│   ├── image_generator.py       # Image generation implementation
│   └── website_analyzer.py      # Website screenshot & analysis
└── outputs/
    ├── images/                  # Generated images
    └── screenshots/             # Website screenshots
```

## 🔧 Adding New Tools

The toolkit is designed to be easily extensible. To add a new tool:

1. **Create tool file** in `tools/` folder:
   ```python
   # tools/my_new_tool.py
   from config import OPENAI_API_KEY  # or GEMINI_API_KEY
   
   def my_function(args):
       """Your tool implementation."""
       pass
   ```

2. **Export from tools package** in `tools/__init__.py`:
   ```python
   from .my_new_tool import my_function
   __all__ = ["web_search", "generate_image", "analyze_website_design", "my_function"]
   ```

3. **Add CLI command** in `main.py`:
   ```python
   my_tool_parser = subparsers.add_parser("my-tool", help="My new tool")
   my_tool_parser.add_argument("arg", help="Argument description")
   
   elif args.command == "my-tool":
       result = my_function(args.arg)
       print(result)
   ```

## 💰 Cost Estimate

- **Web Search:** ~$0.01-0.05 per search (GPT-4 API)
- **Image Generation:** $0.04-0.20 per image (HD costs more)
- **Website Analysis:** Free! (Gemini has generous free tier)

## 🔑 API Keys Setup

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Log in or create account
3. Navigate to API Keys section
4. Create new secret key
5. Add to `.env` as `OPENAI_API_KEY=sk-...`

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com)
2. Click "Get API Key"
3. Create new API key
4. Add to `.env` as `GEMINI_API_KEY=AIza...`

### Brave Search API Key (Optional - for Real Web Search)
*Note: Web search currently uses mock results by default. For real web search:*

1. Go to [Brave Search API](https://api.search.brave.com)
2. Sign up for free tier
3. Get your API key
4. Add to `.env` as `BRAVE_API_KEY=your_key_here`

Without this, web search will still work but will provide placeholder results that ChatGPT will analyze philosophically.

## 🐛 Troubleshooting

**Playwright not installing?**
```bash
# Manually install Playwright browsers
python -m playwright install
```

**API key errors?**
- Verify `.env` file is in the project root
- Check API keys are valid and active
- Ensure no extra spaces in `.env` file

**Rate limit errors?**
- Wait a minute before retrying
- Check your OpenAI account for usage/limits
- Consider upgrading your OpenAI plan

## 📝 License

This toolkit is provided as-is for educational and personal use.
