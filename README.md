# EXIF Watermark Python

This project contains a Python script to apply a text watermark to images, based on the capture date and time read from EXIF metadata.

## Structure

-   `input/`: Folder where source images should be placed.
-   `output/`: Folder where the script will save the processed watermarked images.
-   `watermark_exif.py`: The main script that performs the processing.
-   `inspect_exif.py`: A utility script to inspect the EXIF metadata of an image.

## Setup

1.  Clone the repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Apply Watermark to Images

This command analyzes the `input` folder, compares files with those already present in `output`, and applies the watermark with the EXIF date to all new files.

**Command:**
```bash
python watermark_exif.py
```

The date format will automatically adapt to your system's locale (e.g., "27 December 2025" for English systems, "27 dicembre 2025" for Italian systems).

### 2. Inspect EXIF Metadata (Optional)

This command is a utility to view all EXIF tags contained in a single image file. Useful for debugging why a date might not be read correctly.

**Note:** To inspect a different file, you must manually edit the `inspect_exif.py` file and change the filename within the script (e.g., `"input/IMG_0006.JPG"`).

**Command:**
```bash
python inspect_exif.py
```

---

## 📱 Bonus: Running on Android (Termux)

This section explains how to configure an automated workflow on Android to watermark photos using **Termux**. This allows you to process photos directly on your phone without moving files to a PC.

### Prerequisites

1.  **Termux** (Download from **F-Droid**, *not* the Play Store).
2.  **Termux:Widget** (Optional, for a Home screen shortcut).
3.  **Python** (Installed via Termux).

### 1. Environment Installation

Open Termux and run these commands to update the system and install Python along with necessary graphics libraries:

```bash
# Update repositories
pkg update && pkg upgrade

# Grant access to phone storage (Click "Allow" on the popup)
termux-setup-storage

# Install Python and system libraries for image/font handling
pkg install python libjpeg-turbo zlib freetype

# Install Pillow (Python library)
# Note: We use --no-cache-dir to force correct compilation with the installed FreeType
pip install --no-cache-dir Pillow
```

### 2. Configuration (Magic Links)

The script expects to find an `input` folder, an `output` folder, and optionally an `arial.ttf` font file. Instead of moving photos manually, we create **Symlinks** (virtual shortcuts) pointing to your actual Camera folder.

**2.1 Create the project folder**
```bash
mkdir -p ~/downloads/exif-watermark-py
cd ~/downloads/exif-watermark-py
# Clone the repo here or copy the .py files manually
```

**2.2 Link the Camera Folder**
Replace `"Canon EOS R100"` with the exact name of your camera folder inside `DCIM` or `Pictures`.

```bash
# This makes the script think your camera photos are in "input"
ln -s ~/storage/pictures/"Canon EOS R100" input
```

**2.3 Link the Output Folder**
We create a `watermarked` folder directly inside your camera album so processed photos appear in your Gallery immediately.

```bash
# Create the real folder
mkdir -p ~/storage/pictures/"Canon EOS R100"/watermarked

# Link it to the script's output
ln -s ~/storage/pictures/"Canon EOS R100"/watermarked output
```

**2.4 Link the Font**
Android uses Roboto, not Arial. We create a "fake" Arial pointing to the system font.

```bash
ln -s /system/fonts/Roboto-Regular.ttf arial.ttf
```

### 3. Running the Script manually

```bash
python watermark_exif.py
```

### 4. Automation (Home Screen Widget)

To run the script with a single tap from your Home screen:

1.  **Create the shortcuts folder:**
    ```bash
    mkdir -p ~/.shortcuts
    ```

2.  **Create the launch script (`watermark.sh`):**
    ```bash
    echo "#!/bin/bash" > ~/.shortcuts/watermark.sh
    echo "cd ~/downloads/exif-watermark-py" >> ~/.shortcuts/watermark.sh
    echo "python watermark_exif.py" >> ~/.shortcuts/watermark.sh
    echo "echo ''" >> ~/.shortcuts/watermark.sh
    echo "read -p 'Press Enter to close...'" >> ~/.shortcuts/watermark.sh
    ```

3.  **Make it executable:**
    ```bash
    chmod +x ~/.shortcuts/watermark.sh
    ```

4.  **Add to Home Screen:**
    *   Go to your Android Home Screen.
    *   Long press -> **Widgets** -> **Termux:Widget**.
    *   Select `watermark.sh`.

*> **Note for Android 13+:** If the widget doesn't work, go to Termux:Widget App Info -> "Advanced Settings" -> "Allow restricted settings".*