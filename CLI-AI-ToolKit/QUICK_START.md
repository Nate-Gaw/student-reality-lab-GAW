# 🚀 Quick Reference Guide

## First Time Setup

```bash
# 1. Navigate to the toolkit directory
cd "d:\College Classes\IS219\CLI-AI-ToolKit"

# 2. Run the setup script (installs dependencies + Playwright)
python setup.py

# 3. Done! Start using the tools
```

## Command Examples

### 🔍 Web Search - Get Current Information
```bash
# Search for latest AI developments
python main.py search "latest AI developments 2024"

# Get information on a specific topic
python main.py search "climate change impacts" --max-results 10
```
**Use Case:** When you need current information that your AI knowledge doesn't cover

---

### 🎨 Image Generation - Create Website Assets
```bash
# Generate a single image
python main.py generate-image "modern minimalist landing page design"

# Generate high-quality version
python main.py generate-image "professional website hero section" --quality hd

# Generate multiple images at once
python main.py generate-image "product showcase mockup" --num 3

# Specify size (for different use cases)
python main.py generate-image "website header" --size 1792x1024
```
**Use Case:** Quickly create visual assets for websites, presentations, or designs

---

### 📸 Website Analysis - Get Design Feedback
```bash
# Analyze any website's design
python main.py analyze-website https://www.example.com

# Add custom focus
python main.py analyze-website https://myproject.com --prompt "Focus on mobile responsiveness and loading performance"
```
**Use Case:** Get AI feedback on website designs before launch

---

## Using the Tools Programmatically

You can import the tools directly in your Python scripts:

```python
from tools import web_search, generate_image, run_website_analysis

# Web search
result = web_search("what is quantum computing")
print(result)

# Image generation
images = generate_image("sleek gadget product photo", num_images=2)
for img in images:
    print(f"Generated: {img['filepath']}")

# Website analysis
analysis = run_website_analysis("https://example.com")
print(analysis['analysis'])
```

---

## File Organization

```
outputs/
├── images/              ← All generated images saved here
│   ├── generated_20240210_120530_0.png
│   └── generated_20240210_120531_0.png
└── screenshots/         ← All website screenshots saved here
    └── screenshot_20240210_121000.png
```

---

## Workflow Examples

### Example 1: Create a Website from Scratch
```bash
# Step 1: Research the topic
python main.py search "best practices for e-commerce websites"

# Step 2: Generate visual assets
python main.py generate-image "modern e-commerce product showcase" --quality hd

# Step 3: Review competitor designs
python main.py analyze-website https://www.shopify.com
python main.py analyze-website https://www.etsy.com

# Step 4: Analyze your own site
python main.py analyze-website https://yoursite.com --prompt "Compare my design to these competitors"
```

### Example 2: Market Research + Content Creation
```bash
# Get current market data
python main.py search "AI market trends 2024 market size growth"

# Create visuals for the content
python main.py generate-image "AI market growth visualization chart" --num 2

# Verify your website looks professional
python main.py analyze-website https://yourcontentsite.com
```

---

## Tips & Tricks

1. **Save search results:** Pipe output to a file
   ```bash
   python main.py search "your topic" > research_results.txt
   ```

2. **Batch image generation:** Use a loop
   ```bash
   for prompt in "website header" "about section" "footer design"; do
     python main.py generate-image "$prompt"
   done
   ```

3. **Compare designs:** Analyze multiple sites
   ```bash
   python main.py analyze-website https://site1.com > analysis1.txt
   python main.py analyze-website https://site2.com > analysis2.txt
   ```

---

## Cost Tracking

**Web Search:** ~$0.01-0.05 per query
- Use strategically for truly current information needs

**Image Generation:** $0.04-0.20 per image
- Standard quality: $0.04 per image (1024x1024)
- HD quality: ~$0.20 per image
- Larger sizes cost more

**Website Analysis:** Free!
- Uses Gemini API's free tier
- Unlimited analysis requests

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `python setup.py` again |
| Playwright errors | Run `python -m playwright install` |
| API key errors | Check `.env` file exists and has valid keys |
| Timeout on website | Some sites may take longer, wait 30s |
| Image generation slow | This is normal, DALL-E takes 30-60s per image |

---

## Need Help?

- **Add a new tool?** See "Adding New Tools" section in README.md
- **API issues?** Check OpenAI dashboard and Google AI Studio
- **Performance?** API latency varies; results will eventually appear

Happy building! 🚀
