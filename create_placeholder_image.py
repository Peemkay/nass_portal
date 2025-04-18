from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    """Create a placeholder image for announcements"""
    # Create a new image with a blue background
    width, height = 1200, 600
    background_color = (30, 60, 114)  # Dark blue color
    image = Image.new('RGB', (width, height), background_color)
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Draw a lighter blue rectangle in the center
    rect_width, rect_height = 800, 300
    rect_left = (width - rect_width) // 2
    rect_top = (height - rect_height) // 2
    rect_right = rect_left + rect_width
    rect_bottom = rect_top + rect_height
    rect_color = (42, 82, 152)  # Lighter blue color
    draw.rectangle([rect_left, rect_top, rect_right, rect_bottom], fill=rect_color)
    
    # Add text
    try:
        # Try to load a font (this might not work in all environments)
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    text = "NASS Announcement"
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (400, 60)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    text_color = (255, 255, 255)  # White color
    
    # Draw the text
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Save the image
    output_dir = os.path.join('nass_portal', 'static', 'images')
    output_path = os.path.join(output_dir, 'placeholder-image.png')
    image.save(output_path)
    
    print(f"Placeholder image created at {output_path}")

if __name__ == "__main__":
    create_placeholder_image()
