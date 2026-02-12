"""Image generation tool using OpenAI DALL-E API."""
from openai import OpenAI
from config import OPENAI_API_KEY, IMAGES_DIR
from pathlib import Path
import requests
from datetime import datetime

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    num_images: int = 1
) -> list:
    """
    Generate images using OpenAI's DALL-E API.
    
    Args:
        prompt: Description of the image to generate
        size: Image size - "256x256", "512x512", "1024x1024", "1792x1024", or "1024x1792"
               (default: "1024x1024")
        quality: "standard" or "hd" (hd costs more, default: "standard")
        num_images: Number of images to generate (1-10, default: 1)
    
    Returns:
        List of dictionaries containing image data and file paths
    """
    try:
        # Generate images
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=num_images,
        )
        
        saved_images = []
        
        # Download and save images
        for idx, image_data in enumerate(response.data):
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}_{idx}.png"
            filepath = IMAGES_DIR / filename
            
            # Download image
            img_response = requests.get(image_data.url)
            if img_response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
                
                saved_images.append({
                    "filename": filename,
                    "filepath": str(filepath),
                    "prompt": prompt,
                    "size": size,
                    "url": image_data.url,
                    "revised_prompt": image_data.revised_prompt
                })
        
        return saved_images
        
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")


if __name__ == "__main__":
    # Example usage
    images = generate_image(
        prompt="A modern website header design with blue and purple gradient, minimalist style",
        size="1024x1024",
        quality="standard"
    )
    for img in images:
        print(f"Generated image: {img['filename']}")
        print(f"Saved to: {img['filepath']}")
