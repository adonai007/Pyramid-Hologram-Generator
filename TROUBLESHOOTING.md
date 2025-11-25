# Troubleshooting Guide - Pyramid Hologram Generator

## Common Issues and Solutions

### Video Processing Errors

#### Issue: "Processing 0 frames" or Corrupted Video Errors

**Symptoms:**
```
[mpeg4 @ ...] ac-tex damaged at X Y
[mpeg4 @ ...] Error at MB: XXXX
Processing 0 frames
Total:1 of 0
```

**Root Causes:**
1. Video file has codec corruption or damaged frames
2. Incomplete video file or interrupted recording
3. Unsupported codec or container format
4. Frame count metadata is incorrect or missing

**Solutions:**

##### Solution 1: Repair Video with FFmpeg (Recommended)

Use FFmpeg to re-encode the video and fix corruption:

```bash
# Basic repair - re-encode to H.264/MP4
ffmpeg -i corrupted_video.avi -c:v libx264 -preset medium -crf 23 repaired_video.mp4

# For AVI output with XVID codec
ffmpeg -i corrupted_video.avi -c:v mpeg4 -q:v 5 repaired_video.avi

# High quality repair
ffmpeg -i corrupted_video.avi -c:v libx264 -preset slow -crf 18 repaired_video.mp4
```

Then process the repaired video:
```bash
python 3DHologram.py repaired_video.mp4
```

##### Solution 2: Extract and Process Individual Frames

If the video is severely corrupted, extract frames as images:

```bash
# Extract all readable frames
ffmpeg -i corrupted_video.avi -vsync 0 frame_%04d.png

# Process each frame individually
for file in frame_*.png; do
    python 3DHologram.py "$file"
done
```

##### Solution 3: Use the Improved Script

The updated [`3DHologram.py`](3DHologram.py:1) now includes:
- Automatic video validation
- Corrupted frame skipping
- Multiple codec fallback options
- Better error messages and logging
- Progress indicators

Simply run:
```bash
python 3DHologram.py your_video.avi
```

The script will now:
- Detect and report video issues
- Skip corrupted frames automatically
- Try multiple output codecs
- Provide detailed progress information

---

## Video Format Recommendations

### Supported Input Formats
- **Best:** MP4 with H.264 codec
- **Good:** AVI with XVID or MJPEG codec
- **Acceptable:** Most common video formats (MOV, MKV, WebM)

### Recommended Video Specifications
- **Resolution:** Square aspect ratio (e.g., 640x640, 1280x1280)
- **Frame Rate:** 24-30 FPS
- **Codec:** H.264 or XVID
- **Bitrate:** 5-10 Mbps for good quality

### Creating Compatible Videos

#### Using FFmpeg to Convert Videos

```bash
# Convert any video to compatible format
ffmpeg -i input_video.mp4 -vf "scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset medium -crf 23 -r 30 output_video.mp4

# For AVI output
ffmpeg -i input_video.mp4 -vf "scale=640:640:force_original_aspect_ratio=decrease,pad=640:640:(ow-iw)/2:(oh-ih)/2" -c:v mpeg4 -q:v 5 -r 30 output_video.avi
```

---

## Error Messages Explained

### "Video file not found"
**Cause:** The specified file path doesn't exist.
**Solution:** Check the file path and ensure the file exists.

### "Failed to open video file"
**Cause:** File is corrupted, unsupported format, or missing codecs.
**Solution:** 
1. Try repairing with FFmpeg
2. Convert to a supported format
3. Install required codecs (opencv-python includes most)

### "Could not read any valid frames from video"
**Cause:** All frames in the video are corrupted or unreadable.
**Solution:**
1. Repair video with FFmpeg
2. Extract frames as images and process individually
3. Check if the video plays in a media player

### "Could not initialize video writer with any codec"
**Cause:** System doesn't support any of the output codecs.
**Solution:**
1. Install FFmpeg on your system
2. Update opencv-python: `pip install --upgrade opencv-python`
3. Try a different output format by modifying the script

### "Video ended unexpectedly at frame X"
**Cause:** Video has fewer frames than expected or ends abruptly.
**Solution:** This is usually not critical - the script will process available frames.

---

## Performance Optimization

### For Large Videos

1. **Reduce Resolution:**
   ```python
   # In 3DHologram.py, modify line 62:
   frame = cv2.resize(frame, (320, 320), interpolation=cv2.INTER_CUBIC)
   ```

2. **Process in Batches:**
   ```bash
   # Split video into segments
   ffmpeg -i large_video.mp4 -c copy -segment_time 60 -f segment output%03d.mp4
   
   # Process each segment
   for file in output*.mp4; do
       python 3DHologram.py "$file"
   done
   ```

3. **Use Lower Quality Settings:**
   ```python
   # Modify makeHologram call:
   holo = makeHologram(frame, scale=0.3, scaleR=3)
   ```

### Memory Issues

If you encounter memory errors:
1. Close other applications
2. Process shorter video segments
3. Reduce frame resolution
4. Use a machine with more RAM

---

## Installation Issues

### OpenCV Installation Problems

```bash
# Uninstall and reinstall
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python

# If issues persist, try:
pip install opencv-python-headless
```

### NumPy Compatibility

```bash
# Ensure compatible versions
pip install numpy>=1.19.0
pip install opencv-python>=4.5.0
```

---

## Testing Your Setup

### Quick Test Script

Create a test file `test_setup.py`:

```python
import cv2
import numpy as np
import sys

print(f"Python version: {sys.version}")
print(f"OpenCV version: {cv2.__version__}")
print(f"NumPy version: {np.__version__}")

# Test video codecs
codecs = ['mp4v', 'XVID', 'H264', 'MJPG']
for codec in codecs:
    try:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        print(f"✓ Codec {codec} available")
    except:
        print(f"✗ Codec {codec} not available")
```

Run it:
```bash
python test_setup.py
```

---

## Getting Help

If you continue to experience issues:

1. **Check the logs:** The improved script provides detailed logging
2. **Verify your video:** Try playing it in VLC or another media player
3. **Test with a simple video:** Create a test video to isolate the issue
4. **Check system resources:** Ensure adequate RAM and disk space
5. **Update dependencies:** `pip install --upgrade opencv-python numpy`

### Creating a Test Video

```bash
# Create a simple test video with FFmpeg
ffmpeg -f lavfi -i testsrc=duration=5:size=640x640:rate=30 -pix_fmt yuv420p test_video.mp4

# Process it
python 3DHologram.py test_video.mp4
```

If the test video works but your video doesn't, the issue is with your video file.

---

## Additional Resources

- **FFmpeg Documentation:** https://ffmpeg.org/documentation.html
- **OpenCV Documentation:** https://docs.opencv.org/
- **Video Codec Guide:** https://trac.ffmpeg.org/wiki/Encode/H.264

---

*Last Updated: 2025-01-25*