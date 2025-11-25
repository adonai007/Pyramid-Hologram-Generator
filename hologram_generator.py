"""
Hologram Generator Wrapper
Extracts and wraps the hologram generation functionality from 3DHologram.py
Following holomind_bisa patterns for clean integration
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def makeHologram(original, scale: float = 0.5, scaleR: int = 4, distance: int = 0):
    """
    Create 3D hologram from image (must have equal dimensions)
    Extracted and adapted from 3DHologram.py

    Args:
        original: Input image (numpy array)
        scale: Factor de escala de la imagen (default: 0.5)
        scaleR: Factor de escala del holograma (default: 4)
        distance: Distancia entre las imágenes rotadas (default: 0)

    Returns:
        Hologram image as numpy array
    """
    try:
        logger.info(f"Generating hologram with scale={scale}, scaleR={scaleR}, distance={distance}")

        height = int(scale * original.shape[0])
        width = int(scale * original.shape[1])

        image = cv2.resize(original, (width, height), interpolation=cv2.INTER_CUBIC)

        # Create rotated versions
        up = image.copy()
        down = rotate_bound(image.copy(), 180)
        right = rotate_bound(image.copy(), 90)
        left = rotate_bound(image.copy(), 270)

        # Calculate the maximum dimensions needed for all rotated images
        max_height = max(up.shape[0], down.shape[0], right.shape[0], left.shape[0])
        max_width = max(up.shape[1], down.shape[1], right.shape[1], left.shape[1])

        hologram = np.zeros([max_height * scaleR + distance, max_width * scaleR + distance, 3], image.dtype)

        center_x = int(hologram.shape[0] / 2)
        center_y = int(hologram.shape[1] / 2)

        # Place up image (top)
        start_x = max(0, center_x - up.shape[1] // 2 + distance)
        end_x = min(hologram.shape[1], center_x + up.shape[1] // 2 + distance)
        hologram[0:up.shape[0], start_x:end_x] = up

        # Place down image (bottom)
        down_start_y = hologram.shape[0] - down.shape[0]
        down_start_x = max(0, center_x - down.shape[1] // 2 + distance)
        down_end_x = min(hologram.shape[1], center_x + down.shape[1] // 2 + distance)
        hologram[down_start_y:hologram.shape[0], down_start_x:down_end_x] = down

        # Place right image (right side)
        right_start_x = hologram.shape[1] - right.shape[1] + distance
        right_start_y = max(0, center_x - right.shape[0] // 2)
        right_end_y = min(hologram.shape[0], right_start_y + right.shape[0])
        hologram[right_start_y:right_end_y, right_start_x:right_start_x + right.shape[1]] = right

        # Place left image (left side)
        left_start_x = distance
        left_start_y = max(0, center_x - left.shape[0] // 2)
        left_end_y = min(hologram.shape[0], left_start_y + left.shape[0])
        hologram[left_start_y:left_end_y, left_start_x:left_start_x + left.shape[1]] = left

        logger.info(f"Hologram generated successfully. Shape: {hologram.shape}")
        return hologram

    except Exception as e:
        logger.error(f"Error generating hologram: {e}")
        raise

def rotate_bound(image, angle: int) -> np.ndarray:
    """
    Rotate an image with bounds checking
    Extracted from 3DHologram.py

    Args:
        image: Input image
        angle: Rotation angle in degrees

    Returns:
        Rotated image
    """
    # Grab the dimensions of the image and then determine the center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # Grab the rotation matrix (applying the negative of the angle to rotate clockwise),
    # then grab the sine and cosine (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # Compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # Adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # Perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def process_video_hologram(video_path: str, output_path: str) -> bool:
    """
    Process video file and create hologram effect for each frame
    Adapted from 3DHologram.py process_video function

    Args:
        video_path: Path to input video
        output_path: Path for output video

    Returns:
        Success status
    """
    try:
        logger.info(f"Processing video hologram: {video_path} -> {output_path}")

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.error(f"Failed to open video file: {video_path}")
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30.0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

        # Try to read first valid frame
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

        if holo is None:
            logger.error("Could not read any valid frames from video")
            cap.release()
            return False

        # Reset video to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Define codec and create VideoWriter
        codecs = [
            ('mp4v', output_path),
            ('XVID', output_path.replace('.mp4', '.avi')),
            ('H264', output_path),
            ('MJPG', output_path.replace('.mp4', '.avi'))
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
        processed = 0

        logger.info("Starting video processing...")

        while True:
            ret, frame = cap.read()
            count += 1

            if not ret or frame is None:
                if count < 10:
                    logger.warning(f"Video ended unexpectedly at frame {count}")
                break

            try:
                frame = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_CUBIC)
                holo = makeHologram(frame)
                out.write(holo)
                processed += 1

                if processed % 10 == 0:
                    logger.info(f"Processed: {processed} frames")

            except Exception as e:
                logger.warning(f"Error processing frame {count}: {e}")
                continue

        # Release resources
        cap.release()
        out.release()

        logger.info(f"Video processing complete! Frames processed: {processed}")
        return True

    except Exception as e:
        logger.error(f"Error processing video hologram: {e}")
        return False