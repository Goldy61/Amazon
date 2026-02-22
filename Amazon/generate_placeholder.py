#!/usr/bin/env python3
"""
Generate different styles of crazy placeholder images
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random
import os

def create_placeholder(style="crazy"):
    """Create different styles of placeholder images"""
    
    width, height = 500, 500
    
    if style == "crazy":
        return create_psychedelic_placeholder(width, height)
    elif style == "neon":
        return create_neon_placeholder(width, height)
    elif style == "galaxy":
        return create_galaxy_placeholder(width, height)
    else:
        return create_simple_placeholder(width, height)

def create_psychedelic_placeholder(width, height):
    """Create a psychedelic style placeholder"""
    image = Image.new('RGB', (width, height))
    
    # Create rainbow waves
    for y in range(height):
        for x in range(width):
            wave1 = math.sin(x * 0.02) * 50
            wave2 = math.cos(y * 0.02) * 50
            wave3 = math.sin((x + y) * 0.01) * 30
            
            r = int(128 + 127 * math.sin((x + wave1) * 0.01))
            g = int(128 + 127 * math.sin((y + wave2) * 0.01))
            b = int(128 + 127 * math.sin((x + y + wave3) * 0.01))
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            image.putpixel((x, y), (r, g, b))
    
    return add_text_overlay(image, "🌈 WILD 🌈", "PRODUCT", "AMAZING!")

def create_neon_placeholder(width, height):
    """Create a neon style placeholder"""
    image = Image.new('RGB', (width, height), (10, 10, 30))  # Dark blue background
    draw = ImageDraw.Draw(image)
    
    # Add neon grid
    grid_size = 25
    neon_color = (0, 255, 255)  # Cyan
    
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=neon_color, width=1)
    
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=neon_color, width=1)
    
    # Add neon circles
    for _ in range(10):
        x = random.randint(50, width-50)
        y = random.randint(50, height-50)
        radius = random.randint(20, 60)
        
        colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
        color = random.choice(colors)
        
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], outline=color, width=3)
    
    return add_text_overlay(image, "⚡ NEON ⚡", "STYLE", "ELECTRIC!")

def create_galaxy_placeholder(width, height):
    """Create a galaxy style placeholder"""
    image = Image.new('RGB', (width, height), (5, 5, 20))  # Dark space
    draw = ImageDraw.Draw(image)
    
    # Add stars
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(100, 255)
        size = random.randint(1, 3)
        
        star_color = (brightness, brightness, brightness)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=star_color)
    
    # Add nebula effect
    center_x, center_y = width // 2, height // 2
    for _ in range(1000):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, 150)
        
        x = int(center_x + math.cos(angle) * distance)
        y = int(center_y + math.sin(angle) * distance)
        
        if 0 <= x < width and 0 <= y < height:
            colors = [(100, 50, 150), (150, 50, 100), (50, 100, 150)]
            color = random.choice(colors)
            draw.point((x, y), fill=color)
    
    return add_text_overlay(image, "🌌 COSMIC 🌌", "PRODUCT", "STELLAR!")

def create_simple_placeholder(width, height):
    """Create a simple but stylish placeholder"""
    image = Image.new('RGB', (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    # Add gradient border
    border_width = 20
    for i in range(border_width):
        color_val = 200 - i * 5
        color = (color_val, color_val, color_val)
        draw.rectangle([i, i, width-i-1, height-i-1], outline=color, width=1)
    
    return add_text_overlay(image, "📦 PRODUCT 📦", "IMAGE", "LOADING...")

def add_text_overlay(image, main_text, sub_text, bottom_text):
    """Add text overlay to image"""
    draw = ImageDraw.Draw(image)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 50)
        font_medium = ImageFont.truetype("arial.ttf", 30)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()
    
    width, height = image.size
    
    # Main text
    if font_large:
        bbox = draw.textbbox((0, 0), main_text, font=font_large)
        text_width = bbox[2] - bbox[0]
    else:
        text_width = 200
    
    x = (width - text_width) // 2
    y = height // 2 - 50
    
    # Add outline
    outline_color = (0, 0, 0)
    text_color = (255, 255, 255)
    
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), main_text, fill=outline_color, font=font_large)
    
    draw.text((x, y), main_text, fill=text_color, font=font_large)
    
    # Sub text
    if font_medium:
        bbox = draw.textbbox((0, 0), sub_text, font=font_medium)
        sub_width = bbox[2] - bbox[0]
    else:
        sub_width = 100
    
    sub_x = (width - sub_width) // 2
    sub_y = y + 60
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                draw.text((sub_x + dx, sub_y + dy), sub_text, fill=outline_color, font=font_medium)
    
    draw.text((sub_x, sub_y), sub_text, fill=(255, 200, 0), font=font_medium)
    
    # Bottom text
    if font_small:
        bbox = draw.textbbox((0, 0), bottom_text, font=font_small)
        bottom_width = bbox[2] - bbox[0]
    else:
        bottom_width = 80
    
    bottom_x = (width - bottom_width) // 2
    bottom_y = sub_y + 40
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                draw.text((bottom_x + dx, bottom_y + dy), bottom_text, fill=outline_color, font=font_small)
    
    draw.text((bottom_x, bottom_y), bottom_text, fill=(0, 255, 255), font=font_small)
    
    return image

def main():
    """Generate placeholder with specified style"""
    import sys
    
    style = sys.argv[1] if len(sys.argv) > 1 else "crazy"
    
    print(f"🎨 Generating {style} placeholder...")
    
    image = create_placeholder(style)
    
    os.makedirs('static/images', exist_ok=True)
    image.save('static/images/placeholder.jpg', 'JPEG', quality=95)
    
    print(f"✅ {style.title()} placeholder created: static/images/placeholder.jpg")
    print("🔥 Available styles: crazy, neon, galaxy, simple")

if __name__ == "__main__":
    main()