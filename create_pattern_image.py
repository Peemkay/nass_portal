from PIL import Image, ImageDraw
import os

def create_pattern_image():
    # Create a directory for the image if it doesn't exist
    os.makedirs('nass_portal/static/images', exist_ok=True)
    
    # Create a new image with a white background
    width, height = 200, 200
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a pattern of dots
    dot_spacing = 20
    dot_radius = 2
    for x in range(0, width, dot_spacing):
        for y in range(0, height, dot_spacing):
            draw.ellipse((x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius), fill=(255, 255, 255, 50))
    
    # Save the image
    image_path = 'nass_portal/static/images/pattern.png'
    image.save(image_path)
    print(f"Pattern image created at {image_path}")

if __name__ == "__main__":
    create_pattern_image()
