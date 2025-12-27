import os
import locale
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime

# --- CONFIGURATION ---
INPUT_DIR = "input"
OUTPUT_DIR = "output"
JPEG_QUALITY = 95
FONT_SIZE_RATIO = 50  # Denominator: larger value reduces font size
MARGIN_RATIO = 50     # Denominator: larger value reduces margin

# Set locale to user's default setting for date formatting
try:
    locale.setlocale(locale.LC_TIME, '')
except Exception as e:
    print(f"Warning: Could not set locale. Defaulting to system standard. Error: {e}")

def setup_directories():
    """Creates working directories if they don't exist."""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_files_to_process():
    """
    Returns a list of files present in 'input' but not in 'output'.
    """
    try:
        input_files = set(f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
        # Check if output directory exists, if not treat as empty
        if os.path.exists(OUTPUT_DIR):
            processed_files = set(os.listdir(OUTPUT_DIR))
        else:
            processed_files = set()
        
        files_to_process = list(input_files - processed_files)
        
        print(f"Found {len(input_files)} files in '{INPUT_DIR}'.")
        print(f"Found {len(processed_files)} already processed files in '{OUTPUT_DIR}'.")
        print(f"To process: {len(files_to_process)} files.")
        
        # Print already present files for clarity (optional, can be verbose)
        # for fname in sorted(list(input_files.intersection(processed_files))):
        #     print(f"- '{fname}' already present, skipping.")

        return sorted(files_to_process)
    except FileNotFoundError as e:
        print(f"Error: Directory '{e.filename}' does not exist. Please ensure it is created.")
        return []


def get_exif_date(image):
    """
    Extracts the capture date from EXIF metadata.
    Tries 'DateTimeOriginal' (36867) first, then 'DateTime' (306) as fallback.
    """
    exif_data = image.getexif()
    if not exif_data:
        return None

    # List of date tags to search in order of preference
    date_tags = [36867, 306] # [DateTimeOriginal, DateTime]
    
    for tag in date_tags:
        date_str = exif_data.get(tag)
        if date_str:
            try:
                # Common EXIF format: 'YYYY:MM:DD HH:MM:SS'
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                # If format is unexpected, continue searching
                print(f"Warning: Invalid date format '{date_str}' for tag {tag}. Trying next.")
                continue
    return None

def format_date_localized(dt_object):
    """Formats the datetime object according to the system locale."""
    if not dt_object:
        return ""
    # Format: "Day Month Year, HH:MM" (Month name is localized)
    # %d: Day, %B: Full month name, %Y: Year, %H: Hour (24h), %M: Minute
    return dt_object.strftime("%d %B %Y, %H:%M")

def apply_watermark(image_path, output_path):
    """Applies watermark with EXIF date to an image."""
    try:
        with Image.open(image_path) as img:
            # Preserve original EXIF metadata
            exif_original = img.info.get('exif')

            # 1. Extract date and time
            date_original = get_exif_date(img)
            if not date_original:
                print(f"Warning: EXIF 'DateTimeOriginal' not found for '{os.path.basename(image_path)}'. Skipping.")
                return False

            watermark_text = format_date_localized(date_original)
            
            # 2. Prepare for drawing
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # 3. Calculate font size and type
            font_size = max(15, int(min(width, height) / FONT_SIZE_RATIO))
            try:
                # Try to use a common system font
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                print("Warning: Font 'arial.ttf' not found. Using Pillow default font.")
                # Fallback to default font
                font = ImageFont.load_default()

            # 4. Calculate position
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            margin = max(10, int(min(width, height) / MARGIN_RATIO))
            x = width - text_width - margin
            y = height - text_height - margin

            # 5. Apply shadow (outline) for better visibility
            shadow_color = "black"
            for offset in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                 draw.text((x + offset[0], y + offset[1]), watermark_text, font=font, fill=shadow_color)
            
            # 6. Apply text
            text_color = "white"
            draw.text((x, y), watermark_text, font=font, fill=text_color)
            
            # 7. Save the image
            # Convert to RGB if necessary (e.g., for PNG with transparency)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            if exif_original:
                img.save(output_path, "jpeg", quality=JPEG_QUALITY, exif=exif_original)
            else:
                img.save(output_path, "jpeg", quality=JPEG_QUALITY)
                
            print(f"Processing '{os.path.basename(image_path)}'... Done.")
            return True

    except FileNotFoundError:
        print(f"Error: File not found '{image_path}'.")
        return False
    except Exception as e:
        print(f"Error processing '{os.path.basename(image_path)}': {e}")
        return False

def main():
    """Main function of the script."""
    print("--- Starting EXIF Watermark Script ---")
    
    setup_directories()
    
    files_to_process = get_files_to_process()
    
    if not files_to_process:
        print("\nNo new files to process. Exiting.")
        return

    processed_count = 0
    error_count = 0
    
    for filename in files_to_process:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        if apply_watermark(input_path, output_path):
            processed_count += 1
        else:
            error_count += 1
            
    print("\n--- Execution Summary ---")
    print(f"Successfully processed: {processed_count}")
    print(f"Errors or skipped: {error_count}")
    print("-------------------------")

if __name__ == "__main__":
    main()
