from PIL import Image, ExifTags

def inspect_exif(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            if not exif_data:
                print(f"No EXIF data found in '{image_path}'.")
                return

            print(f"EXIF data for '{image_path}':")
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                print(f"  Tag: {tag_name} (ID: {tag_id}), Value: {value}")

    except FileNotFoundError:
        print(f"Error: File not found at '{image_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # Ensure you have a file in the input directory to test this.
    inspect_exif("input/IMG_0005_.JPG")
