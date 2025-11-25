import cv2
import numpy as np
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def makeHologram(original,scale=0.5,scaleR=4,distance=0):
    '''
        Create 3D hologram from image (must have equal dimensions)
    '''
    
    height = int((scale*original.shape[0]))
    width = int((scale*original.shape[1]))
    
    image = cv2.resize(original, (width, height), interpolation = cv2.INTER_CUBIC)
    
    up = image.copy()
    down = rotate_bound(image.copy(),180)
    right = rotate_bound(image.copy(), 90)
    left = rotate_bound(image.copy(), 270)
    
    # Calculate the maximum dimensions needed for all rotated images
    max_height = max(up.shape[0], down.shape[0], right.shape[0], left.shape[0])
    max_width = max(up.shape[1], down.shape[1], right.shape[1], left.shape[1])
    
    hologram = np.zeros([max_height*scaleR+distance, max_width*scaleR+distance, 3], image.dtype)
    
    center_x = int((hologram.shape[0])/2)
    center_y = int((hologram.shape[1])/2)
    
    # Place up image (top)
    start_x = max(0, center_x - up.shape[1]//2 + distance)
    end_x = min(hologram.shape[1], center_x + up.shape[1]//2 + distance)
    hologram[0:up.shape[0], start_x:end_x] = up
    
    # Place down image (bottom)
    down_start_y = hologram.shape[0] - down.shape[0]
    down_start_x = max(0, center_x - down.shape[1]//2 + distance)
    down_end_x = min(hologram.shape[1], center_x + down.shape[1]//2 + distance)
    hologram[down_start_y:hologram.shape[0], down_start_x:down_end_x] = down
    
    # Place right image (right side) - use correct dimensions after rotation
    right_start_x = hologram.shape[1] - right.shape[1] + distance
    right_start_y = max(0, center_x - right.shape[0]//2)
    right_end_y = min(hologram.shape[0], right_start_y + right.shape[0])
    hologram[right_start_y:right_end_y, right_start_x:right_start_x + right.shape[1]] = right
    
    # Place left image (left side) - use correct dimensions after rotation
    left_start_x = distance
    left_start_y = max(0, center_x - left.shape[0]//2)
    left_end_y = min(hologram.shape[0], left_start_y + left.shape[0])
    hologram[left_start_y:left_end_y, left_start_x:left_start_x + left.shape[1]] = left
    
    #cv2.imshow("up",up)
    #cv2.imshow("down",down)
    #cv2.imshow("left",left)
    #cv2.imshow("right",right)
    #cv2.imshow("hologram",hologram)
    #cv2.waitKey()
    return hologram

def process_video(video):
    """
    Process video file and create hologram effect for each frame.
    Includes robust error handling for corrupted videos.
    """
    # Validate video file exists
    if not os.path.exists(video):
        logger.error(f"Video file not found: {video}")
        return False
    
    cap = cv2.VideoCapture(video)
    
    # Check if video opened successfully
    if not cap.isOpened():
        logger.error(f"Failed to open video file: {video}")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        logger.warning("Could not detect FPS, defaulting to 30")
        fps = 30.0
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video properties: {width}x{height}, {fps} FPS")
    
    # Try to read first valid frame to initialize hologram dimensions
    holo = None
    first_frame_attempts = 0
    max_attempts = 100
    
    while holo is None and first_frame_attempts < max_attempts:
        ret, frame = cap.read()
        first_frame_attempts += 1
        
        if ret and frame is not None:
            try:
                frame = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_CUBIC)
                holo = makeHologram(frame)
                logger.info(f"Successfully read first frame after {first_frame_attempts} attempts")
            except Exception as e:
                logger.warning(f"Error processing frame {first_frame_attempts}: {e}")
                continue
        elif not ret:
            logger.warning(f"Failed to read frame {first_frame_attempts}")
    
    if holo is None:
        logger.error("Could not read any valid frames from video")
        cap.release()
        return False
    
    # Reset video to beginning for full processing
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Define codec and create VideoWriter
    # Try multiple codecs for better compatibility
    codecs = [
        ('mp4v', 'hologram_output.mp4'),
        ('XVID', 'hologram_output.avi'),
        ('H264', 'hologram_output.mp4'),
        ('MJPG', 'hologram_output.avi')
    ]
    
    out = None
    output_file = None
    
    for codec_name, filename in codecs:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec_name)
            out = cv2.VideoWriter(filename, fourcc, fps, (holo.shape[1], holo.shape[0]))
            if out.isOpened():
                output_file = filename
                logger.info(f"Using codec: {codec_name}, output: {filename}")
                break
            else:
                out.release()
        except Exception as e:
            logger.warning(f"Codec {codec_name} failed: {e}")
    
    if out is None or not out.isOpened():
        logger.error("Could not initialize video writer with any codec")
        cap.release()
        return False
    
    # Process video frames
    count = 0
    skipped = 0
    processed = 0
    
    # If total_frames is unreliable (0 or negative), count manually
    if total_frames <= 0:
        logger.warning("Frame count unavailable, will process until end of video")
        total_frames = "unknown"
    
    logger.info(f"Starting video processing... Total frames: {total_frames}")
    
    while True:
        ret, frame = cap.read()
        count += 1
        
        if not ret or frame is None:
            # End of video or read error
            if count < 10:  # If we fail very early, it's likely an error
                logger.warning(f"Video ended unexpectedly at frame {count}")
            break
        
        try:
            # Resize and process frame
            frame = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_CUBIC)
            holo = makeHologram(frame)
            out.write(holo)
            processed += 1
            
            # Progress indicator
            if processed % 10 == 0 or processed == 1:
                if isinstance(total_frames, int):
                    progress = (processed / total_frames) * 100
                    logger.info(f"Processed: {processed}/{total_frames} frames ({progress:.1f}%)")
                else:
                    logger.info(f"Processed: {processed} frames")
                    
        except Exception as e:
            logger.warning(f"Error processing frame {count}: {e}")
            skipped += 1
            continue
        
        # Safety check: if we've processed way more than expected, break
        if isinstance(total_frames, int) and count > total_frames * 2:
            logger.warning("Processed more frames than expected, stopping")
            break
    
    # Release resources
    cap.release()
    out.release()
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info(f"Processing complete!")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Frames processed: {processed}")
    logger.info(f"Frames skipped: {skipped}")
    logger.info(f"{'='*50}\n")
    
    return True

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
 
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
 
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
 
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
 
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.error("Usage: python 3DHologram.py <input_file>")
        logger.info("  input_file: Path to image (PNG, JPG) or video (AVI, MP4)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(input_file):
        logger.error(f"File not found: {input_file}")
        sys.exit(1)
    
    # Try to load as image first
    logger.info(f"Processing file: {input_file}")
    orig = cv2.imread(input_file)
    
    if orig is not None:
        # It's an image
        logger.info("Detected image file, creating hologram...")
        try:
            holo = makeHologram(orig, scale=1.0)
            output_file = "hologram.png"
            cv2.imwrite(output_file, holo)
            logger.info(f"Hologram saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error creating hologram: {e}")
            sys.exit(1)
    else:
        # Try as video
        logger.info("Detected video file, processing frames...")
        success = process_video(input_file)
        if not success:
            logger.error("Video processing failed")
            sys.exit(1)
