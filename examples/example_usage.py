#!/usr/bin/env python3
"""
Example usage of the AD-Census Python wrapper

This script demonstrates how to use the adcensus package to compute
disparity maps from stereo image pairs.
"""

import sys
import os
import argparse
import time

try:
    import adcensus
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install required packages:")
    print("  pip install -r requirements.txt")
    print("  pip install .")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Compute disparity map from stereo image pair using AD-Census algorithm'
    )
    parser.add_argument('left_image', help='Path to left image')
    parser.add_argument('right_image', help='Path to right image')
    parser.add_argument('--output', '-o', default='disparity',
                       help='Output path for disparity map (default: disparity)')
    parser.add_argument('--min-disparity', type=int, default=0,
                       help='Minimum disparity value (default: 0)')
    parser.add_argument('--max-disparity', type=int, default=64,
                       help='Maximum disparity value (default: 64)')
    parser.add_argument('--no-lr-check', action='store_true',
                       help='Disable left-right consistency check')
    parser.add_argument('--no-filling', action='store_true',
                       help='Disable disparity filling')
    parser.add_argument('--no-colormap', action='store_true',
                       help='Do not save colorized disparity map')
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.exists(args.left_image):
        print(f"Error: Left image not found: {args.left_image}")
        sys.exit(1)
    
    if not os.path.exists(args.right_image):
        print(f"Error: Right image not found: {args.right_image}")
        sys.exit(1)
    
    print("=" * 70)
    print("AD-Census Stereo Matching")
    print("=" * 70)
    print(f"Left image:       {args.left_image}")
    print(f"Right image:      {args.right_image}")
    print(f"Output:           {args.output}")
    print(f"Disparity range:  [{args.min_disparity}, {args.max_disparity}]")
    print("=" * 70)
    
    # Load images to get dimensions
    print("\nLoading images...")
    left_img = cv2.imread(args.left_image, cv2.IMREAD_COLOR)
    right_img = cv2.imread(args.right_image, cv2.IMREAD_COLOR)
    
    if left_img is None:
        print(f"Error: Failed to load left image: {args.left_image}")
        sys.exit(1)
    
    if right_img is None:
        print(f"Error: Failed to load right image: {args.right_image}")
        sys.exit(1)
    
    if left_img.shape != right_img.shape:
        print(f"Error: Image dimensions must match!")
        print(f"  Left:  {left_img.shape}")
        print(f"  Right: {right_img.shape}")
        sys.exit(1)
    
    height, width = left_img.shape[:2]
    print(f"Image dimensions: {width} x {height}")
    
    # Create stereo matcher
    print("\nInitializing AD-Census stereo matcher...")
    stereo = adcensus.ADCensusStereo(
        min_disparity=args.min_disparity,
        max_disparity=args.max_disparity,
        do_lr_check=not args.no_lr_check,
        do_filling=not args.no_filling
    )
    
    # Compute disparity
    print("\nComputing disparity map...")
    start_time = time.time()
    
    try:
        disparity = stereo.compute(left_img, right_img)
    except Exception as e:
        print(f"Error during disparity computation: {e}")
        sys.exit(1)
    
    elapsed_time = time.time() - start_time
    print(f"Done! Processing time: {elapsed_time:.2f} seconds")
    
    # Print statistics
    valid_mask = np.isfinite(disparity)
    if np.any(valid_mask):
        min_disp = np.min(disparity[valid_mask])
        max_disp = np.max(disparity[valid_mask])
        mean_disp = np.mean(disparity[valid_mask])
        valid_ratio = np.sum(valid_mask) / disparity.size * 100
        
        print("\nDisparity statistics:")
        print(f"  Min:    {min_disp:.2f}")
        print(f"  Max:    {max_disp:.2f}")
        print(f"  Mean:   {mean_disp:.2f}")
        print(f"  Valid:  {valid_ratio:.1f}%")
    else:
        print("\nWarning: No valid disparity values found!")
    
    # Save disparity map
    print(f"\nSaving disparity map to {args.output}...")
    try:
        adcensus.save_disparity(
            disparity, 
            args.output,
            colormap=not args.no_colormap
        )
    except Exception as e:
        print(f"Error saving disparity map: {e}")
        sys.exit(1)
    
    print("\nProcessing complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

