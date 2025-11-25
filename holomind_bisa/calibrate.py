#!/usr/bin/env python3
"""
HoloMind Calibration Tool
Calibrates holographic display settings for optimal projection
"""

import cv2
import numpy as np
import json
import os
import argparse

def draw_calibration_square(frame, x, y, size):
    """Draw calibration square on frame"""
    cv2.rectangle(frame, (x-size//2, y-size//2), (x+size//2, y+size//2), (0, 255, 0), 2)
    cv2.putText(frame, "Adjust square to match pyramid base", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "Arrow keys: move | +/-: size | S: save | ESC: exit",
                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def main():
    parser = argparse.ArgumentParser(description='HoloMind Calibration Tool')
    parser.add_argument('--profile', type=str, default='default',
                       help='Calibration profile name')
    args = parser.parse_args()

    # Default calibration values
    x, y = 512, 512  # Center of 1024x1024
    size = 400

    # Load existing profiles
    profiles = {}
    if os.path.exists('calibration_profiles.json'):
        try:
            with open('calibration_profiles.json', 'r') as f:
                profiles = json.load(f)
        except:
            print("Warning: Could not load existing profiles")

    # Load existing profile if it exists
    if args.profile in profiles:
        profile = profiles[args.profile]
        x = profile.get('projection_x', x)
        y = profile.get('projection_y', y)
        size = profile.get('projection_size', size)
        print(f"Loaded existing profile: {args.profile}")

    cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Calibration', 1024, 1024)

    print("Calibration Tool Started")
    print("Use arrow keys to position square")
    print("Use +/- to adjust size")
    print("Press 'S' to save, 'ESC' to exit")

    while True:
        # Create black frame
        frame = np.zeros((1024, 1024, 3), dtype=np.uint8)

        # Draw calibration square
        draw_calibration_square(frame, x, y, size)

        cv2.imshow('Calibration', frame)

        key = cv2.waitKey(0) & 0xFF

        # Arrow keys for movement
        if key == 82:  # Up arrow
            y = max(0, y - 10)
        elif key == 84:  # Down arrow
            y = min(1024, y + 10)
        elif key == 81:  # Left arrow
            x = max(0, x - 10)
        elif key == 83:  # Right arrow
            x = min(1024, x + 10)

        # Size adjustment
        elif key == ord('+') or key == ord('='):
            size = min(800, size + 20)
        elif key == ord('-'):
            size = max(100, size - 20)

        # Save
        elif key == ord('s') or key == ord('S'):
            # Get display info
            display_width = 1920  # Default, could be detected
            display_height = 1080

            profile_data = {
                "display_width": display_width,
                "display_height": display_height,
                "projection_x": x,
                "projection_y": y,
                "projection_size": size,
                "reflector_type": "pyramid"
            }

            profiles[args.profile] = profile_data

            with open('calibration_profiles.json', 'w') as f:
                json.dump(profiles, f, indent=4)

            print(f"Calibration saved to profile: {args.profile}")
            print(f"Settings: x={x}, y={y}, size={size}")

        # Exit
        elif key == 27:  # ESC
            break

    cv2.destroyAllWindows()
    print("Calibration complete")

if __name__ == "__main__":
    main()